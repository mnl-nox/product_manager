from __future__ import annotations

import json
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import io
import math
import os
import re
import secrets
import sqlite3
import sys
import time
from http.cookies import SimpleCookie
from zipfile import ZIP_DEFLATED, ZipFile
import xml.sax.saxutils as xml_utils
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))


def default_data_path() -> Path:
    if os.name == 'nt':
        base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
    return base / 'ProductManager' / 'product_manager.db'


if os.environ.get('PRODUCT_MANAGER_DB'):
    DB_PATH = Path(os.environ['PRODUCT_MANAGER_DB']).expanduser().resolve()
elif getattr(sys, 'frozen', False):
    DB_PATH = default_data_path()
else:
    DB_PATH = BASE_DIR / 'db' / 'product_manager.db'

SCHEMA_PATH = BASE_DIR / 'db' / 'schema.sql'
UI_DIR = BASE_DIR / 'ui'

CLIENT_ALLOWED_STATUS = {'active', 'inactive', 'pending'}
PRODUCT_ALLOWED_STATUS = {'available', 'reserved', 'out_of_stock'}
MAX_BODY_BYTES = 32 * 1024
SESSION_TTL_SECONDS = 12 * 60 * 60
USER_ROLES = {'admin', 'operator', 'finance', 'viewer'}
ROLE_PERMISSIONS = {
    'admin': {'*'},
    'operator': {'read', 'catalog:write', 'alerts:write'},
    'finance': {'read', 'finance:read', 'finance:write'},
    'viewer': {'read'},
}
APP_VERSION = (BASE_DIR / 'VERSION').read_text(encoding='utf-8').strip() if (BASE_DIR / 'VERSION').exists() else 'unknown'
TELEMETRY_EVENTS = {'javascript_error', 'unhandled_rejection'}


def telemetry_endpoint_configured() -> bool:
    try:
        parsed = urllib.parse.urlparse(os.environ.get('PRODUCT_MANAGER_TELEMETRY_URL', '').strip())
    except ValueError:
        return False
    return parsed.scheme == 'https' and bool(parsed.netloc) and parsed.username is None and parsed.password is None


def send_telemetry_event(event_name: str) -> bool:
    """Forward an allow-listed, content-free diagnostic to an admin endpoint."""
    endpoint = os.environ.get('PRODUCT_MANAGER_TELEMETRY_URL', '').strip()
    if not telemetry_endpoint_configured() or event_name not in TELEMETRY_EVENTS:
        return False
    body = json.dumps({
        'application': 'product-manager',
        'version': APP_VERSION,
        'event': event_name,
    }).encode('utf-8')
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={'Content-Type': 'application/json', 'User-Agent': f'ProductManager/{APP_VERSION}'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def ensure_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = SCHEMA_PATH.read_text(encoding='utf-8')
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.executescript(schema_sql)
        for table in ('clients', 'products'):
            columns = {row[1] for row in conn.execute(f'PRAGMA table_info({table})')}
            if 'created_by' not in columns:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN created_by INTEGER REFERENCES app_users(id)')
            if table == 'products' and 'active' not in columns:
                conn.execute('ALTER TABLE products ADD COLUMN active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))')
        finance_columns = {row[1] for row in conn.execute('PRAGMA table_info(finance_entries)')}
        if 'amount' in finance_columns and 'amount_cents' not in finance_columns:
            conn.executescript('''
                BEGIN IMMEDIATE;
                CREATE TABLE finance_entries_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_type TEXT NOT NULL CHECK(entry_type IN ('income','expense')),
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
                    entry_date TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'paid' CHECK(status IN ('planned','paid','cancelled')),
                    created_by INTEGER REFERENCES app_users(id),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO finance_entries_v2 (id, entry_type, category, description, amount_cents, entry_date, status, created_by, created_at)
                    SELECT id, entry_type, category, description, CAST(ROUND(amount * 100) AS INTEGER), entry_date, status, created_by, created_at
                    FROM finance_entries WHERE amount > 0;
                DROP TABLE finance_entries;
                ALTER TABLE finance_entries_v2 RENAME TO finance_entries;
                CREATE INDEX IF NOT EXISTS idx_finance_entries_date ON finance_entries(entry_date, id);
                COMMIT;
            ''')
        finance_columns = {row[1] for row in conn.execute('PRAGMA table_info(finance_entries)')}
        for column, declaration in (
            ('department_id', 'INTEGER REFERENCES hr_departments(id)'),
            ('org_unit_id', 'INTEGER REFERENCES org_units(id)'),
        ):
            if column not in finance_columns:
                conn.execute(f'ALTER TABLE finance_entries ADD COLUMN {column} {declaration}')
        sales_columns = {row[1] for row in conn.execute('PRAGMA table_info(sales)')}
        for column, declaration in (
            ('department_id', 'INTEGER REFERENCES hr_departments(id)'),
            ('org_unit_id', 'INTEGER REFERENCES org_units(id)'),
        ):
            if column not in sales_columns:
                conn.execute(f'ALTER TABLE sales ADD COLUMN {column} {declaration}')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_finance_entries_dimensions ON finance_entries(department_id, org_unit_id, entry_date)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_sales_dimensions ON sales(department_id, org_unit_id, sale_date)')
        conn.commit()


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f'scrypt$16384$8$1${salt.hex()}${digest.hex()}'


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, expected_hex = encoded.split('$')
        if algorithm != 'scrypt':
            return False
        digest = hashlib.scrypt(
            password.encode('utf-8'), salt=bytes.fromhex(salt_hex),
            n=int(n), r=int(r), p=int(p), dklen=len(bytes.fromhex(expected_hex)),
        )
        return hmac.compare_digest(digest.hex(), expected_hex)
    except (ValueError, TypeError):
        return False


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def audit_record(actor_id: int | None, action: str, entity: str, entity_id: int | None = None) -> None:
    with get_db() as conn:
        conn.execute(
            'INSERT INTO audit_log (actor_id, action, entity, entity_id) VALUES (?, ?, ?, ?)',
            (actor_id, action, entity, entity_id),
        )


def low_stock_default() -> int:
    try:
        return max(0, min(int(os.environ.get('PRODUCT_MANAGER_LOW_STOCK_DEFAULT', '5')), 1_000_000))
    except ValueError:
        return 5


def user_count() -> int:
    with get_db() as conn:
        return conn.execute('SELECT COUNT(*) FROM app_users WHERE active=1').fetchone()[0]


def login_rate_key(username: str, remote_address: str) -> str:
    normalized = username.strip().casefold().encode('utf-8')
    address_hash = hashlib.sha256(remote_address.encode('utf-8')).digest()
    return hashlib.sha256(b'product-manager-login:' + normalized + address_hash).hexdigest()


def login_is_limited(key: str) -> bool:
    with get_db() as conn:
        conn.execute('DELETE FROM auth_login_limits WHERE window_started < ?', (int(time.time()) - 3600,))
        row = conn.execute('SELECT locked_until FROM auth_login_limits WHERE username_hash=?', (key,)).fetchone()
        return bool(row and row['locked_until'] > int(time.time()))


def record_login_failure(key: str) -> None:
    now = int(time.time())
    with get_db() as conn:
        row = conn.execute('SELECT failed_count, window_started FROM auth_login_limits WHERE username_hash=?', (key,)).fetchone()
        if row is None or now - row['window_started'] > 900:
            conn.execute(
                'INSERT OR REPLACE INTO auth_login_limits (username_hash, failed_count, window_started, locked_until) VALUES (?, 1, ?, 0)',
                (key, now),
            )
            return
        failures = row['failed_count'] + 1
        locked_until = now + 900 if failures >= 8 else 0
        conn.execute(
            'UPDATE auth_login_limits SET failed_count=?, locked_until=? WHERE username_hash=?',
            (failures, locked_until, key),
        )


def issue_session(user_id: int) -> tuple[str, str]:
    raw_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    with get_db() as conn:
        conn.execute('DELETE FROM app_sessions WHERE expires_at <= ?', (int(time.time()),))
        conn.execute(
            'INSERT INTO app_sessions (token_hash, csrf_token, user_id, expires_at) VALUES (?, ?, ?, ?)',
            (token_digest(raw_token), csrf_token, user_id, int(time.time()) + SESSION_TTL_SECONDS),
        )
    return raw_token, csrf_token


def sanitize_text(value, field_name: str, max_length: int = 128) -> str:
    if value is None:
        raise ValueError(f'O campo {field_name} é obrigatório.')
    text = str(value).strip()
    text = ''.join(ch for ch in text if ch.isprintable() and ch not in {'\n', '\r', '\t'})
    if not text:
        raise ValueError(f'O campo {field_name} é obrigatório.')
    if len(text) > max_length:
        raise ValueError(f'O campo {field_name} excede o limite permitido.')
    return text


def sanitize_optional_text(value, field_name: str, max_length: int = 512) -> str:
    if value is None or str(value).strip() == '':
        return ''
    return sanitize_text(value, field_name, max_length)


def normalize_status(value, allowed: set[str], field_name: str) -> str:
    text = sanitize_text(value, field_name, 32).lower()
    if text not in allowed:
        raise ValueError(f'O campo {field_name} contém um valor inválido.')
    return text


def validate_email(email: str) -> str:
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.fullmatch(pattern, email):
        raise ValueError('E-mail inválido.')
    return email


def validate_phone(phone: str) -> str:
    cleaned = re.sub(r'[^0-9]', '', phone)
    if len(cleaned) < 10:
        raise ValueError('Telefone inválido.')
    return phone


def validate_cpf(cpf: str) -> str:
    cleaned = re.sub(r'[^0-9]', '', cpf)
    if len(cleaned) != 11:
        raise ValueError('CPF inválido.')
    return cpf


def validate_product_payload(payload: dict) -> tuple[str, str, str, str, str, str, float, int, str, str]:
    name = sanitize_text(payload.get('name'), 'nome', 128)
    category = sanitize_text(payload.get('category'), 'categoria', 64)
    sku = sanitize_text(payload.get('sku'), 'sku', 64)
    reference = sanitize_text(payload.get('reference'), 'referência', 64)
    brand = sanitize_text(payload.get('brand'), 'marca', 64)
    status = normalize_status(payload.get('status'), PRODUCT_ALLOWED_STATUS, 'status')
    price_value = payload.get('price')
    if price_value is None:
        raise ValueError('O campo preço é obrigatório.')
    price = float(price_value)
    if not math.isfinite(price) or price < 0:
        raise ValueError('O preço não pode ser negativo.')
    quantity_value = payload.get('quantity')
    if quantity_value is None:
        raise ValueError('O campo quantidade é obrigatório.')
    quantity = int(quantity_value)
    if isinstance(quantity_value, bool) or str(quantity) != str(quantity_value).strip():
        raise ValueError('A quantidade deve ser um número inteiro.')
    if quantity < 0:
        raise ValueError('A quantidade não pode ser negativa.')
    supplier = sanitize_text(payload.get('supplier'), 'fornecedor', 128)
    notes = sanitize_optional_text(payload.get('notes'), 'observações', 512)
    return name, category, sku, reference, brand, status, price, quantity, supplier, notes


def spreadsheet_safe(value) -> str:
    text = str(value if value is not None else '')
    if text.startswith(('=', '+', '-', '@')):
        return "'" + text
    return text


def dashboard_export_rows() -> list[list[object]]:
    with get_db() as conn:
        metrics = [
            ('Clientes', conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0]),
            ('Produtos', conn.execute('SELECT COUNT(*) FROM products WHERE active=1').fetchone()[0]),
            ('Clientes ativos', conn.execute("SELECT COUNT(*) FROM clients WHERE status = 'active'").fetchone()[0]),
            ('Estoque total', conn.execute('SELECT COALESCE(SUM(quantity), 0) FROM products WHERE active=1').fetchone()[0]),
        ]
        categories = conn.execute(
            'SELECT category, COUNT(*) AS total, COALESCE(SUM(quantity), 0) AS stock '
            'FROM products WHERE active=1 GROUP BY category ORDER BY category'
        ).fetchall()
        products = conn.execute(
            'SELECT id, name, category, sku, brand, price, quantity, status '
            'FROM products WHERE active=1 ORDER BY id'
        ).fetchall()

    rows: list[list[object]] = [
        ['Product Manager — Dashboard', f'Versão {APP_VERSION}'],
        [],
        ['Indicador', 'Valor'],
        *[[name, value] for name, value in metrics],
        [],
        ['Categoria', 'Produtos', 'Estoque'],
        *[[row['category'], row['total'], row['stock']] for row in categories],
        [],
        ['ID', 'Produto', 'Categoria', 'SKU', 'Marca', 'Preço', 'Quantidade', 'Status'],
        *[[row['id'], row['name'], row['category'], row['sku'], row['brand'], row['price'], row['quantity'], row['status']] for row in products],
    ]
    return rows


def _column_name(number: int) -> str:
    result = ''
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def build_dashboard_xlsx(rows: list[list[object]]) -> bytes:
    """Create a small dependency-free XLSX workbook using inline string cells."""
    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            if value is None or value == '':
                continue
            reference = f'{_column_name(col_index)}{row_index}'
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                cells.append(f'<c r="{reference}"><v>{value}</v></c>')
            else:
                escaped = xml_utils.escape(str(value))
                cells.append(f'<c r="{reference}" t="inlineStr"><is><t xml:space="preserve">{escaped}</t></is></c>')
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    worksheet = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>')
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Dashboard" sheetId="1" r:id="rId1"/></sheets></workbook>')
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>')
    package_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>')
    workbook_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '</Relationships>')
    output = io.BytesIO()
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', content_types)
        archive.writestr('_rels/.rels', package_rels)
        archive.writestr('xl/workbook.xml', workbook)
        archive.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
        archive.writestr('xl/worksheets/sheet1.xml', worksheet)
    return output.getvalue()


def google_sheets_configured() -> bool:
    spreadsheet_id = os.environ.get('PRODUCT_MANAGER_GOOGLE_SHEETS_SPREADSHEET_ID', '').strip()
    access_token = os.environ.get('PRODUCT_MANAGER_GOOGLE_SHEETS_ACCESS_TOKEN', '').strip()
    cell_range = os.environ.get('PRODUCT_MANAGER_GOOGLE_SHEETS_RANGE', 'Export!A1').strip() or 'Export!A1'
    valid_range = re.fullmatch(r"(?:'[A-Za-z0-9_ -]+'|[A-Za-z0-9_ -]+)!\$?[A-Z]{1,3}\$?[1-9][0-9]*(?::\$?[A-Z]{1,3}\$?[1-9][0-9]*)?", cell_range)
    valid_token = bool(access_token) and not any(character.isspace() or ord(character) < 32 for character in access_token)
    return bool(re.fullmatch(r'[A-Za-z0-9_-]+', spreadsheet_id) and valid_token and valid_range)


def seed_default_data() -> None:
    if os.environ.get('PRODUCT_MANAGER_DEMO_DATA', '').strip().lower() not in {'1', 'true', 'yes'}:
        return
    with get_db() as conn:
        clients_count = conn.execute('SELECT COUNT(*) AS total FROM clients').fetchone()['total']
        products_count = conn.execute('SELECT COUNT(*) AS total FROM products').fetchone()['total']

        if clients_count == 0:
            conn.execute(
                '''
                INSERT INTO clients (name, username, email, phone, cpf, status, city, role, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    'Ana Silva', 'ana.silva', 'ana.silva@empresa.com', '(11) 99988-7766', '12345678909', 'active', 'São Paulo', 'admin', 'Cliente principal do projeto.',
                    'Bruno Costa', 'bruno.costa', 'bruno.costa@empresa.com', '(21) 98877-6655', '98765432100', 'active', 'Rio de Janeiro', 'financeiro', 'Cliente com vencimentos mensais.',
                    'Carla Mendes', 'carla.mendes', 'carla.mendes@empresa.com', '(31) 97766-5544', '45678912310', 'pending', 'Belo Horizonte', 'suporte', 'Solicitou validação de acesso.'
                ),
            )

        if products_count == 0:
            conn.execute(
                '''
                INSERT INTO products (name, category, sku, reference, brand, status, price, quantity, supplier, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?, ?, ?, ?),
                       (?, ?, ?, ?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?, ?, ?, ?),
                       (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    'Monitor 24 polegadas', 'Hardware', 'MON-24-001', 'REF-MON-24', 'Acer', 'available', 1250.00, 18, 'Distribuidora Norte', 'Monitor corporativo com painel IPS.',
                    'Teclado mecânico', 'Periféricos', 'TEC-MEC-014', 'REF-TEC-01', 'Logitech', 'available', 440.00, 32, 'Tecno Supply', 'Layout ABNT2 com switches azuis.',
                    'Notebook Business', 'Computadores', 'NB-BIZ-220', 'REF-NB-220', 'Dell', 'reserved', 4999.90, 7, 'Alpha Tech', 'Equipamento para área administrativa.',
                    'SSD NVMe 1TB', 'Armazenamento', 'SSD-NVME-1TB', 'REF-SSD-1TB', 'Kingston', 'available', 690.00, 25, 'StorageHub', 'Leitura rápida para escritórios.',
                    'Webcam 4K', 'Acessórios', 'CAM-4K-031', 'REF-CAM-4K', 'Lenovo', 'out_of_stock', 820.00, 0, 'Vision Media', 'Webcam para videoconferência.',
                    'Licença Office Pro', 'Software', 'LIC-OFF-2026', 'REF-LIC-2026', 'Microsoft', 'available', 399.00, 60, 'SoftLayer', 'Licença anual renovável.',
                    'Roteador Wi-Fi 6', 'Rede', 'ROU-WIFI6-05', 'REF-ROU-06', 'TP-Link', 'available', 650.00, 12, 'Networks Plus', 'Cobertura de rede para ambientes híbridos.'
                ),
            )

        conn.commit()


ensure_database()
seed_default_data()


class AppHandler(BaseHTTPRequestHandler):
    server_version = 'ProductManager/1.0'

    def current_session(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
        except Exception:
            return None
        morsel = cookie.get('pm_session')
        if morsel is None:
            return None
        session_hash = token_digest(morsel.value)
        with get_db() as conn:
            row = conn.execute(
                '''SELECT s.token_hash, s.csrf_token, u.id, u.username, u.role
                   FROM app_sessions s JOIN app_users u ON u.id = s.user_id
                   WHERE s.token_hash = ? AND s.expires_at > ? AND u.active = 1''',
                (session_hash, int(time.time())),
            ).fetchone()
            if row is None:
                conn.execute('DELETE FROM app_sessions WHERE token_hash = ?', (session_hash,))
                return None
            return dict(row)

    def send_login_redirect(self):
        self.send_response(302)
        self.send_header('Location', '/login')
        self.send_security_headers()
        self.end_headers()

    def require_permission(self, user, permission: str) -> bool:
        if user['role'] == 'admin' or permission in ROLE_PERMISSIONS.get(user['role'], set()):
            return True
        self.send_json({'error': 'Você não tem permissão para esta ação.'}, status=403)
        return False

    @staticmethod
    def secure_cookie_enabled() -> bool:
        configured = os.environ.get('PRODUCT_MANAGER_COOKIE_SECURE')
        if configured is not None:
            return configured.strip().lower() in {'1', 'true', 'yes'}
        return os.environ.get('PRODUCT_MANAGER_HOST', '127.0.0.1') not in {'127.0.0.1', 'localhost', '::1'}

    def send_auth_cookie(self, token: str | None, clear: bool = False):
        parts = ['pm_session=', 'Path=/', 'HttpOnly', 'SameSite=Strict']
        if token:
            parts[0] = f'pm_session={token}'
        if clear:
            parts.append('Max-Age=0')
        else:
            parts.append(f'Max-Age={SESSION_TTL_SECONDS}')
        if self.secure_cookie_enabled():
            parts.append('Secure')
        self.send_header('Set-Cookie', '; '.join(parts))

    def send_json_with_session(self, payload, token: str):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_auth_cookie(token)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def login_user(self, username: str, password: str):
        username = username.strip()
        remote_address = getattr(self, 'client_address', ('unknown',))[0]
        key = login_rate_key(username, remote_address)
        if login_is_limited(key):
            self.send_json({'error': 'Muitas tentativas. Aguarde 15 minutos antes de tentar novamente.'}, status=429)
            return
        with get_db() as conn:
            user = conn.execute(
                'SELECT id, username, password_hash, role FROM app_users WHERE username=? AND active=1',
                (username,),
            ).fetchone()
        dummy_hash = 'scrypt$16384$8$1$00112233445566778899aabbccddeeff$' + ('0' * 64)
        password_ok = verify_password(password, user['password_hash'] if user else dummy_hash)
        if user is None or not password_ok:
            record_login_failure(key)
            self.send_json({'error': 'Usuário ou senha inválidos.'}, status=401)
            return
        with get_db() as conn:
            conn.execute('DELETE FROM auth_login_limits WHERE username_hash=?', (key,))
        token, csrf_token = issue_session(user['id'])
        audit_record(user['id'], 'login', 'session')
        self.send_json_with_session({
            'user': {'id': user['id'], 'username': user['username'], 'role': user['role']},
            'csrfToken': csrf_token,
        }, token)

    def handle_first_admin_setup(self, payload):
        setup_token = os.environ.get('PRODUCT_MANAGER_SETUP_TOKEN', '')
        provided_token = payload.get('setup_token', '')
        if not setup_token or not isinstance(provided_token, str) or not hmac.compare_digest(setup_token, provided_token):
            self.send_json({'error': 'Token de configuração inválido ou não configurado no servidor.'}, status=403)
            return
        username = payload.get('username', '')
        password = payload.get('password', '')
        if not isinstance(username, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{3,64}', username.strip()):
            self.send_json({'error': 'Usuário deve ter 3 a 64 caracteres: letras, números, ponto, hífen ou sublinhado.'}, status=400)
            return
        if not isinstance(password, str) or len(password) < 12 or len(password) > 256:
            self.send_json({'error': 'A senha deve ter entre 12 e 256 caracteres.'}, status=400)
            return
        try:
            with get_db() as conn:
                conn.execute('BEGIN IMMEDIATE')
                if conn.execute('SELECT COUNT(*) FROM app_users WHERE active=1').fetchone()[0] != 0:
                    conn.rollback()
                    self.send_json({'error': 'A configuração inicial já foi concluída.'}, status=409)
                    return
                cursor = conn.execute(
                    'INSERT INTO app_users (username, password_hash, role) VALUES (?, ?, ?)',
                    (username.strip(), hash_password(password), 'admin'),
                )
                admin_id = cursor.lastrowid
            audit_record(admin_id, 'create', 'user', admin_id)
        except sqlite3.IntegrityError:
            self.send_json({'error': 'Não foi possível criar o administrador inicial.'}, status=409)
            return
        os.environ.pop('PRODUCT_MANAGER_SETUP_TOKEN', None)
        token, csrf_token = issue_session(admin_id)
        self.send_json_with_session({
            'user': {'id': admin_id, 'username': username.strip(), 'role': 'admin'},
            'csrfToken': csrf_token,
        }, token)

    def validate_csrf(self, user) -> bool:
        origin = self.headers.get('Origin')
        if origin:
            parsed_origin = urllib.parse.urlparse(origin)
            if parsed_origin.netloc != self.headers.get('Host'):
                self.send_json({'error': 'Origem da requisição inválida.'}, status=403)
                return False
        csrf_token = self.headers.get('X-CSRF-Token', '')
        if not csrf_token or not hmac.compare_digest(user['csrf_token'], csrf_token):
            self.send_json({'error': 'Token CSRF ausente ou inválido.'}, status=403)
            return False
        return True

    def require_authenticated_request(self, path: str):
        user = self.current_session()
        if user is None:
            if path.startswith('/api/'):
                self.send_json({'error': 'Autenticação necessária.'}, status=401)
            else:
                self.send_login_redirect()
            return None
        return user

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Minimal public probes for container/platform orchestration. Never return
        # connection strings, filesystem paths, or exception details here.
        if path == '/healthz':
            self.send_json({'status': 'ok'})
            return

        if path == '/readyz':
            try:
                with get_db() as conn:
                    conn.execute('SELECT 1').fetchone()
            except sqlite3.Error:
                self.send_json({'status': 'unavailable'}, status=503)
                return
            self.send_json({'status': 'ready'})
            return

        if path == '/login':
            self.serve_file(UI_DIR / 'login.html', 'text/html; charset=utf-8')
            return

        if path in {'/', '/dashboard', '/products', '/finance', '/alerts', '/admin/users', '/work-items', '/purchasing', '/hr', '/reports'} or path.startswith('/api/'):
            if path == '/api/auth/setup-status':
                with get_db() as conn:
                    user_count = conn.execute('SELECT COUNT(*) FROM app_users WHERE active = 1').fetchone()[0]
                self.send_json({'setupRequired': user_count == 0, 'setupAvailable': bool(os.environ.get('PRODUCT_MANAGER_SETUP_TOKEN'))})
                return
            user = self.require_authenticated_request(path)
            if user is None:
                return
            self.current_user = user
            if path == '/hr' and user['role'] != 'admin':
                self.send_json({'error': 'Acesso restrito ao administrador.'}, status=403)
                return
            if path.startswith('/api/hr/') and user['role'] != 'admin':
                self.send_json({'error': 'Acesso restrito ao administrador.'}, status=403)
                return
            if path == '/finance' and not self.require_permission(user, 'finance:read'):
                return
            if path == '/alerts' and not self.require_permission(user, 'read'):
                return
            if path == '/admin/users' and user['role'] != 'admin':
                self.send_login_redirect()
                return
            if path.startswith('/api/auth/users') and user['role'] != 'admin':
                self.send_json({'error': 'Apenas administradores podem gerenciar usuários.'}, status=403)
                return
            if path.startswith('/api/finance') and not self.require_permission(user, 'finance:read'):
                return

        if path in ('/', '/dashboard'):
            self.serve_file(UI_DIR / 'index.html', 'text/html; charset=utf-8')
            return

        if path == '/products':
            self.serve_file(UI_DIR / 'products.html', 'text/html; charset=utf-8')
            return

        if path == '/finance':
            self.serve_file(UI_DIR / 'finance.html', 'text/html; charset=utf-8')
            return

        if path == '/alerts':
            self.serve_file(UI_DIR / 'alerts.html', 'text/html; charset=utf-8')
            return

        if path == '/admin/users':
            self.serve_file(UI_DIR / 'users.html', 'text/html; charset=utf-8')
            return

        if path == '/work-items':
            self.serve_file(UI_DIR / 'work-items.html', 'text/html; charset=utf-8')
            return

        if path == '/purchasing':
            self.serve_file(UI_DIR / 'purchasing.html', 'text/html; charset=utf-8')
            return

        if path == '/hr':
            self.serve_file(UI_DIR / 'hr.html', 'text/html; charset=utf-8')
            return

        if path == '/reports':
            self.serve_file(UI_DIR / 'reports.html', 'text/html; charset=utf-8')
            return

        if path == '/privacy.html':
            self.serve_file(UI_DIR / 'privacy.html', 'text/html; charset=utf-8')
            return

        if path == '/PRIVACY.md':
            self.serve_file(BASE_DIR / 'PRIVACY.md', 'text/markdown; charset=utf-8')
            return

        if path == '/styles.css':
            self.serve_file(UI_DIR / 'styles.css', 'text/css; charset=utf-8')
            return

        if path == '/manifest.webmanifest':
            self.serve_file(UI_DIR / 'manifest.webmanifest', 'application/manifest+json; charset=utf-8')
            return

        if path == '/service-worker.js':
            self.serve_file(UI_DIR / 'service-worker.js', 'application/javascript; charset=utf-8')
            return

        if path.startswith('/js/'):
            relative = path[len('/js/'):]
            resource = UI_DIR / 'js' / relative
            self.serve_file(resource, self._content_type_for(resource))
            return

        if path.startswith('/ui/'):
            resource = UI_DIR / path[len('/ui/'):]
            self.serve_file(resource, self._content_type_for(resource))
            return

        if path.startswith('/assets/'):
            resource = BASE_DIR / path.lstrip('/')
            self.serve_file(resource, self._content_type_for(resource))
            return

        if path == '/api/dashboard/export.csv':
            self.export_dashboard()
            return

        if path == '/api/dashboard/export.xlsx':
            self.export_dashboard_xlsx()
            return

        if path == '/api/dashboard':
            with get_db() as conn:
                clients_count = conn.execute('SELECT COUNT(*) AS total FROM clients').fetchone()['total']
                products_count = conn.execute('SELECT COUNT(*) AS total FROM products WHERE active=1').fetchone()['total']
                active_count = conn.execute("SELECT COUNT(*) AS total FROM clients WHERE status = 'active'").fetchone()['total']
                stock_total = conn.execute('SELECT COALESCE(SUM(quantity), 0) AS total FROM products WHERE active=1').fetchone()['total']
                categories = conn.execute(
                    'SELECT category, COUNT(*) AS total, COALESCE(SUM(quantity), 0) AS stock FROM products WHERE active=1 GROUP BY category ORDER BY total DESC'
                ).fetchall()
                recent_clients = conn.execute(
                    'SELECT * FROM clients ORDER BY id DESC LIMIT 5'
                ).fetchall()
                low_stock_products = conn.execute(
                    '''SELECT p.* FROM products p LEFT JOIN stock_thresholds t ON t.product_id=p.id
                       WHERE p.active=1 AND p.quantity <= COALESCE(t.minimum_quantity, ?)
                       ORDER BY p.quantity ASC, p.id ASC LIMIT 5''',
                    (low_stock_default(),),
                ).fetchall()

            self.send_json({
                'clients': clients_count,
                'products': products_count,
                'activeClients': active_count,
                'totalStock': stock_total,
                'categories': [dict(row) for row in categories],
                'recentClients': [dict(row) for row in recent_clients],
                'lowStockProducts': [dict(row) for row in low_stock_products],
            })
            return

        if path == '/api/categories':
            with get_db() as conn:
                rows = conn.execute('SELECT category, COUNT(*) AS total FROM products WHERE active=1 GROUP BY category ORDER BY category ASC').fetchall()
            self.send_json([dict(row) for row in rows])
            return

        if path == '/api/clients':
            with get_db() as conn:
                rows = conn.execute('SELECT * FROM clients ORDER BY id ASC').fetchall()
            self.send_json([dict(row) for row in rows])
            return

        if path == '/api/products':
            params = parse_qs(urlparse(self.path).query)
            category_filter = params.get('category', ['all'])[0]
            include_inactive = params.get('include_inactive', ['0'])[0] == '1' and self.current_user['role'] in {'admin', 'operator'}
            sql = 'SELECT * FROM products' if include_inactive else 'SELECT * FROM products WHERE active=1'
            values = []
            if category_filter and category_filter != 'all':
                sql += ' AND category = ?' if 'WHERE' in sql else ' WHERE category = ?'
                values.append(category_filter)
            sql += ' ORDER BY id ASC'
            with get_db() as conn:
                rows = conn.execute(sql, values).fetchall()
            self.send_json([dict(row) for row in rows])
            return

        if path == '/api/summary':
            with get_db() as conn:
                clients_count = conn.execute('SELECT COUNT(*) AS total FROM clients').fetchone()['total']
                products_count = conn.execute('SELECT COUNT(*) AS total FROM products WHERE active=1').fetchone()['total']
                active_count = conn.execute("SELECT COUNT(*) AS total FROM clients WHERE status = 'active'").fetchone()['total']
                stock_total = conn.execute('SELECT COALESCE(SUM(quantity), 0) AS total FROM products WHERE active=1').fetchone()['total']
            self.send_json({
                'clients': clients_count,
                'products': products_count,
                'activeClients': active_count,
                'totalStock': stock_total,
            })
            return

        if path == '/api/org-units':
            if user['role'] != 'admin':
                self.send_json({'error': 'Apenas administradores podem gerenciar unidades.'}, status=403)
                return
            try:
                name = sanitize_text(payload.get('name'), 'nome da unidade', 100)
                description = sanitize_optional_text(payload.get('description'), 'descrição', 300)
            except ValueError as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            try:
                with get_db() as conn:
                    cursor = conn.execute('INSERT INTO org_units (name, description) VALUES (?, ?)', (name, description))
            except sqlite3.IntegrityError:
                self.send_json({'error': 'Unidade já cadastrada.'}, status=409)
                return
            audit_record(user['id'], 'create', 'org_unit', cursor.lastrowid)
            self.send_json({'id': cursor.lastrowid, 'message': 'Unidade cadastrada.'}, status=201)
            return

        if path == '/api/reports/sales':
            if user['role'] not in {'admin', 'operator', 'finance'}:
                self.send_json({'error': 'Permissão para registrar vendas necessária.'}, status=403)
                return
            try:
                product_id = int(payload.get('product_id'))
                quantity = int(payload.get('quantity'))
                department_id = int(payload['department_id']) if payload.get('department_id') not in (None, '') else None
                org_unit_id = int(payload['org_unit_id']) if payload.get('org_unit_id') not in (None, '') else None
                unit_price = Decimal(str(payload.get('unit_price')))
                cents = unit_price * 100
                sale_date = date.fromisoformat(payload.get('sale_date', date.today().isoformat())).isoformat()
                status_value = payload.get('status', 'paid')
                if quantity < 1 or quantity > 1_000_000:
                    raise ValueError('Quantidade deve ficar entre 1 e 1.000.000.')
                if not unit_price.is_finite() or cents != cents.to_integral_value() or cents <= 0 or cents > 99_999_999_999:
                    raise ValueError('Preço unitário inválido.')
                if status_value not in {'paid', 'planned'}:
                    raise ValueError('Situação da venda inválida.')
                unit_cents = int(cents)
                total_cents = unit_cents * quantity
                if total_cents > 99_999_999_999_999:
                    raise ValueError('Valor total excede o limite permitido.')
            except (TypeError, ValueError, InvalidOperation) as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            with get_db() as conn:
                conn.execute('BEGIN IMMEDIATE')
                product = conn.execute("SELECT id, name, quantity, active FROM products WHERE id=?", (product_id,)).fetchone()
                if product is None or not product['active']:
                    self.send_json({'error': 'Produto ativo não encontrado.'}, status=404)
                    return
                if status_value == 'paid' and product['quantity'] < quantity:
                    self.send_json({'error': 'Estoque insuficiente para registrar a venda.'}, status=409)
                    return
                if department_id is not None and not conn.execute('SELECT 1 FROM hr_departments WHERE id=? AND active=1', (department_id,)).fetchone():
                    self.send_json({'error': 'Departamento ativo não encontrado.'}, status=400)
                    return
                if org_unit_id is not None and not conn.execute('SELECT 1 FROM org_units WHERE id=? AND active=1', (org_unit_id,)).fetchone():
                    self.send_json({'error': 'Unidade ativa não encontrada.'}, status=400)
                    return
                cursor = conn.execute('INSERT INTO sales (sale_date, status, total_cents, department_id, org_unit_id, recorded_by) VALUES (?, ?, ?, ?, ?, ?)',
                                      (sale_date, status_value, total_cents, department_id, org_unit_id, user['id']))
                sale_id = cursor.lastrowid
                conn.execute('INSERT INTO sales_items (sale_id, product_id, quantity, unit_price_cents, line_total_cents) VALUES (?, ?, ?, ?, ?)',
                             (sale_id, product_id, quantity, unit_cents, total_cents))
                if status_value == 'paid':
                    conn.execute('UPDATE products SET quantity=quantity-? WHERE id=?', (quantity, product_id))
                conn.execute('INSERT INTO finance_entries (entry_type, category, description, amount_cents, entry_date, status, department_id, org_unit_id, created_by) VALUES (?,?,?,?,?,?,?,?,?)',
                             ('income', 'Vendas', f'Venda #{sale_id} — {product["name"]}', total_cents, sale_date, status_value, department_id, org_unit_id, user['id']))
            audit_record(user['id'], 'create', 'sale', sale_id)
            self.send_json({'id': sale_id, 'total_cents': total_cents, 'message': 'Venda registrada e estoque atualizado.'}, status=201)
            return

        if path == '/api/hr/payroll-export.csv':
            params = parse_qs(parsed.query)
            try:
                start_date = date.fromisoformat(params.get('from', [date.today().replace(day=1).isoformat()])[0]).isoformat()
                end_date = date.fromisoformat(params.get('to', [date.today().isoformat()])[0]).isoformat()
                if end_date < start_date:
                    raise ValueError('O período final deve ser igual ou posterior ao inicial.')
            except ValueError as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            with get_db() as conn:
                rows = conn.execute("""SELECT e.employee_code, e.full_name, e.job_title,
                    COALESCE(d.name, '') AS department, w.work_date, w.minutes_worked, w.notes
                    FROM hr_work_time w JOIN hr_employees e ON e.id=w.employee_id
                    LEFT JOIN hr_departments d ON d.id=e.department_id
                    WHERE w.work_date BETWEEN ? AND ? ORDER BY e.employee_code, w.work_date""",
                    (start_date, end_date)).fetchall()
            output = io.StringIO(newline='')
            writer = csv.writer(output)
            writer.writerow(['employee_code', 'full_name', 'job_title', 'department', 'work_date', 'minutes_worked', 'notes'])
            for row in rows:
                writer.writerow([spreadsheet_safe(str(value)) if isinstance(value, str) else value for value in row])
            body = ('\\ufeff' + output.getvalue()).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="payroll-hours-export.csv"')
            self.send_header('Content-Length', str(len(body)))
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        if path.startswith('/api/hr/'):
            if user['role'] != 'admin':
                self.send_json({'error': 'Acesso restrito ao administrador.'}, status=403)
                return
            if path == '/api/hr/departments':
                try:
                    name = sanitize_text(payload.get('name'), 'departamento', 100)
                    description = sanitize_optional_text(payload.get('description'), 'descrição', 300)
                except ValueError as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                try:
                    with get_db() as conn:
                        cursor = conn.execute('INSERT INTO hr_departments (name, description) VALUES (?, ?)', (name, description))
                except sqlite3.IntegrityError:
                    self.send_json({'error': 'Departamento já cadastrado.'}, status=409)
                    return
                audit_record(user['id'], 'create', 'hr_department', cursor.lastrowid)
                self.send_json({'id': cursor.lastrowid, 'message': 'Departamento cadastrado.'}, status=201)
                return
            if path == '/api/hr/employees':
                try:
                    employee_code = sanitize_text(payload.get('employee_code'), 'matrícula', 32)
                    full_name = sanitize_text(payload.get('full_name'), 'nome completo', 160)
                    email = sanitize_optional_text(payload.get('email'), 'e-mail', 128)
                    if email:
                        email = validate_email(email)
                    job_title = sanitize_text(payload.get('job_title'), 'cargo', 100)
                    hire_date = date.fromisoformat(payload.get('hire_date')).isoformat()
                    department_id = payload.get('department_id')
                    department_id = int(department_id) if department_id not in (None, '') else None
                    notes = sanitize_optional_text(payload.get('notes'), 'observações', 512)
                except (TypeError, ValueError) as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                with get_db() as conn:
                    if department_id is not None and not conn.execute('SELECT 1 FROM hr_departments WHERE id=? AND active=1', (department_id,)).fetchone():
                        self.send_json({'error': 'Departamento ativo não encontrado.'}, status=400)
                        return
                    try:
                        cursor = conn.execute('''INSERT INTO hr_employees
                            (employee_code, full_name, email, job_title, department_id, hire_date, notes, created_by)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (employee_code, full_name, email, job_title, department_id, hire_date, notes, user['id']))
                    except sqlite3.IntegrityError:
                        self.send_json({'error': 'Matrícula já cadastrada.'}, status=409)
                        return
                audit_record(user['id'], 'create', 'hr_employee', cursor.lastrowid)
                self.send_json({'id': cursor.lastrowid, 'message': 'Colaborador cadastrado.'}, status=201)
                return
            if path == '/api/hr/absences':
                try:
                    employee_id = int(payload.get('employee_id'))
                    absence_type = payload.get('absence_type')
                    start_date = date.fromisoformat(payload.get('start_date')).isoformat()
                    end_date = date.fromisoformat(payload.get('end_date')).isoformat()
                    notes = sanitize_optional_text(payload.get('notes'), 'observações', 512)
                    if absence_type not in {'vacation', 'sick_leave', 'personal', 'other'} or end_date < start_date:
                        raise ValueError('Tipo ou período de ausência inválido.')
                except (TypeError, ValueError) as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                with get_db() as conn:
                    if not conn.execute('SELECT 1 FROM hr_employees WHERE id=? AND status != "inactive"', (employee_id,)).fetchone():
                        self.send_json({'error': 'Colaborador não encontrado ou inativo.'}, status=404)
                        return
                    cursor = conn.execute('INSERT INTO hr_absences (employee_id, absence_type, start_date, end_date, notes, recorded_by) VALUES (?, ?, ?, ?, ?, ?)',
                                          (employee_id, absence_type, start_date, end_date, notes, user['id']))
                audit_record(user['id'], 'create', 'hr_absence', cursor.lastrowid)
                self.send_json({'id': cursor.lastrowid, 'message': 'Ausência registrada para aprovação.'}, status=201)
                return
            absence_decision = re.fullmatch(r'/api/hr/absences/(\\d+)/decision', path)
            if absence_decision:
                absence_id = int(absence_decision.group(1))
                decision = payload.get('decision')
                if decision not in {'approved', 'rejected'}:
                    self.send_json({'error': 'Decisão inválida.'}, status=400)
                    return
                with get_db() as conn:
                    cursor = conn.execute("UPDATE hr_absences SET status=? WHERE id=? AND status='requested'", (decision, absence_id))
                    if not cursor.rowcount:
                        self.send_json({'error': 'Ausência não encontrada ou já decidida.'}, status=409)
                        return
                audit_record(user['id'], decision, 'hr_absence', absence_id)
                self.send_json({'message': 'Decisão registrada.'})
                return
            if path == '/api/hr/documents':
                try:
                    employee_id = int(payload.get('employee_id'))
                    document_type = sanitize_text(payload.get('document_type'), 'tipo de documento', 80)
                    title = sanitize_text(payload.get('title'), 'título', 160)
                    storage_reference = sanitize_optional_text(payload.get('storage_reference'), 'referência de armazenamento', 256)
                    expires_on = payload.get('expires_on') or None
                    if expires_on:
                        expires_on = date.fromisoformat(expires_on).isoformat()
                except (TypeError, ValueError) as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                with get_db() as conn:
                    if not conn.execute('SELECT 1 FROM hr_employees WHERE id=?', (employee_id,)).fetchone():
                        self.send_json({'error': 'Colaborador não encontrado.'}, status=404)
                        return
                    cursor = conn.execute('INSERT INTO hr_documents (employee_id, document_type, title, storage_reference, expires_on, created_by) VALUES (?, ?, ?, ?, ?, ?)',
                                          (employee_id, document_type, title, storage_reference, expires_on, user['id']))
                audit_record(user['id'], 'create', 'hr_document', cursor.lastrowid)
                self.send_json({'id': cursor.lastrowid, 'message': 'Metadados do documento registrados.'}, status=201)
                return
            if path == '/api/hr/work-time':
                try:
                    employee_id = int(payload.get('employee_id'))
                    work_date = date.fromisoformat(payload.get('work_date')).isoformat()
                    minutes_worked = int(payload.get('minutes_worked'))
                    notes = sanitize_optional_text(payload.get('notes'), 'observações', 256)
                    if not 0 <= minutes_worked <= 1440:
                        raise ValueError('Jornada deve ficar entre 0 e 1440 minutos.')
                except (TypeError, ValueError) as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                try:
                    with get_db() as conn:
                        if not conn.execute('SELECT 1 FROM hr_employees WHERE id=?', (employee_id,)).fetchone():
                            self.send_json({'error': 'Colaborador não encontrado.'}, status=404)
                            return
                        cursor = conn.execute('INSERT INTO hr_work_time (employee_id, work_date, minutes_worked, notes, recorded_by) VALUES (?, ?, ?, ?, ?)',
                                              (employee_id, work_date, minutes_worked, notes, user['id']))
                except sqlite3.IntegrityError:
                    self.send_json({'error': 'Já existe jornada registrada para esse colaborador e data.'}, status=409)
                    return
                audit_record(user['id'], 'create', 'hr_work_time', cursor.lastrowid)
                self.send_json({'id': cursor.lastrowid, 'message': 'Jornada registrada.'}, status=201)
                return
            self.send_json({'error': 'Rota de RH não encontrada.'}, status=404)
            return

        if path.startswith('/api/purchasing/'):
            if self.current_user['role'] not in {'admin', 'operator', 'finance', 'viewer'}:
                self.send_json({'error': 'Permissão de consulta necessária.'}, status=403)
                return
            with get_db() as conn:
                if path == '/api/purchasing/suppliers':
                    rows = conn.execute("SELECT id, name, tax_id, email, phone, status, created_at FROM suppliers ORDER BY name").fetchall()
                    self.send_json([dict(row) for row in rows])
                    return
                if path == '/api/purchasing/requests':
                    rows = conn.execute("""SELECT r.*, u.username AS requester
                        FROM purchase_requests r JOIN app_users u ON u.id=r.requested_by
                        ORDER BY r.created_at DESC, r.id DESC""").fetchall()
                    self.send_json([dict(row) for row in rows])
                    return
                if path == '/api/purchasing/orders':
                    rows = conn.execute("""SELECT o.*, s.name AS supplier_name
                        FROM purchase_orders o JOIN suppliers s ON s.id=o.supplier_id
                        ORDER BY o.created_at DESC, o.id DESC""").fetchall()
                    self.send_json([dict(row) for row in rows])
                    return
                order_match = re.fullmatch(r'/api/purchasing/orders/(\\d+)', path)
                if order_match:
                    order_id = int(order_match.group(1))
                    order = conn.execute("""SELECT o.*, s.name AS supplier_name FROM purchase_orders o
                        JOIN suppliers s ON s.id=o.supplier_id WHERE o.id=?""", (order_id,)).fetchone()
                    if order is None:
                        self.send_json({'error': 'Pedido não encontrado.'}, status=404)
                        return
                    items = conn.execute('SELECT * FROM purchase_order_items WHERE order_id=? ORDER BY id', (order_id,)).fetchall()
                    self.send_json({'order': dict(order), 'items': [dict(item) for item in items]})
                    return
                request_match = re.fullmatch(r'/api/purchasing/requests/(\\d+)', path)
                if request_match:
                    request_id = int(request_match.group(1))
                    request_row = conn.execute('SELECT * FROM purchase_requests WHERE id=?', (request_id,)).fetchone()
                    if request_row is None:
                        self.send_json({'error': 'Solicitação de compra não encontrada.'}, status=404)
                        return
                    items = conn.execute('SELECT * FROM purchase_request_items WHERE request_id=? ORDER BY id', (request_id,)).fetchall()
                    quotes = conn.execute("""SELECT q.*, s.name AS supplier_name FROM supplier_quotes q
                        JOIN suppliers s ON s.id=q.supplier_id WHERE q.request_id=? ORDER BY q.total_cents, q.id""", (request_id,)).fetchall()
                    self.send_json({'request': dict(request_row), 'items': [dict(x) for x in items], 'quotes': [dict(x) for x in quotes]})
                    return
            self.send_json({'error': 'Rota de compras não encontrada.'}, status=404)
            return

        if path.startswith('/api/hr/'):
            if self.current_user['role'] != 'admin':
                self.send_json({'error': 'Acesso restrito ao administrador.'}, status=403)
                return
            with get_db() as conn:
                if path == '/api/hr/departments':
                    rows = conn.execute('SELECT id, name, description, active, created_at FROM hr_departments ORDER BY name').fetchall()
                    self.send_json([dict(row) for row in rows])
                    return
                if path == '/api/hr/employees':
                    rows = conn.execute("""SELECT e.id, e.employee_code, e.full_name, e.email, e.job_title,
                        e.department_id, d.name AS department_name, e.hire_date, e.status, e.notes, e.created_at
                        FROM hr_employees e LEFT JOIN hr_departments d ON d.id=e.department_id
                        ORDER BY e.full_name""").fetchall()
                    self.send_json([dict(row) for row in rows])
                    return
                if path == '/api/hr/absences':
                    rows = conn.execute("""SELECT a.*, e.full_name AS employee_name FROM hr_absences a
                        JOIN hr_employees e ON e.id=a.employee_id ORDER BY a.start_date DESC, a.id DESC""").fetchall()
                    self.send_json([dict(row) for row in rows])
                    return
                if path == '/api/hr/documents':
                    rows = conn.execute("""SELECT d.id, d.employee_id, e.full_name AS employee_name, d.document_type,
                        d.title, d.expires_on, d.created_at FROM hr_documents d JOIN hr_employees e ON e.id=d.employee_id
                        ORDER BY d.created_at DESC""").fetchall()
                    self.send_json([dict(row) for row in rows])
                    return
                if path == '/api/hr/work-time':
                    rows = conn.execute("""SELECT w.*, e.full_name AS employee_name FROM hr_work_time w
                        JOIN hr_employees e ON e.id=w.employee_id ORDER BY w.work_date DESC, w.id DESC LIMIT 500""").fetchall()
                    self.send_json([dict(row) for row in rows])
                    return
            self.send_json({'error': 'Rota de RH não encontrada.'}, status=404)
            return

        if path == '/api/reports/dimensions':
            with get_db() as conn:
                departments = conn.execute("SELECT id, name FROM hr_departments WHERE active=1 ORDER BY name").fetchall()
                units = conn.execute("SELECT id, name FROM org_units WHERE active=1 ORDER BY name").fetchall()
            self.send_json({'departments': [dict(row) for row in departments], 'units': [dict(row) for row in units]})
            return

        if path == '/api/reports/summary':
            params = parse_qs(parsed.query)
            try:
                start_date = date.fromisoformat(params.get('from', [date.today().replace(day=1).isoformat()])[0]).isoformat()
                end_date = date.fromisoformat(params.get('to', [date.today().isoformat()])[0]).isoformat()
                if end_date < start_date:
                    raise ValueError('O período final deve ser igual ou posterior ao inicial.')
            except ValueError as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            with get_db() as conn:
                totals = conn.execute("""SELECT
                    COALESCE(SUM(CASE WHEN entry_type='income' AND status='paid' THEN amount_cents ELSE 0 END),0) AS revenue_cents,
                    COALESCE(SUM(CASE WHEN entry_type='expense' AND status='paid' THEN amount_cents ELSE 0 END),0) AS expenses_cents,
                    COALESCE(SUM(CASE WHEN entry_type='income' AND status='planned' THEN amount_cents ELSE 0 END),0) AS planned_income_cents,
                    COALESCE(SUM(CASE WHEN entry_type='expense' AND status='planned' THEN amount_cents ELSE 0 END),0) AS planned_expenses_cents
                    FROM finance_entries WHERE entry_date BETWEEN ? AND ?""", (start_date, end_date)).fetchone()
                overdue = conn.execute("""SELECT entry_type, COUNT(*) AS count, COALESCE(SUM(amount_cents),0) AS amount_cents
                    FROM finance_entries WHERE status='planned' AND entry_date < ? GROUP BY entry_type""", (date.today().isoformat(),)).fetchall()
                top_products = conn.execute("""SELECT p.id, p.name, p.sku, SUM(si.quantity) AS units_sold,
                    SUM(si.line_total_cents) AS revenue_cents FROM sales_items si
                    JOIN sales s ON s.id=si.sale_id JOIN products p ON p.id=si.product_id
                    WHERE s.status='paid' AND s.sale_date BETWEEN ? AND ? GROUP BY p.id, p.name, p.sku
                    ORDER BY units_sold DESC, revenue_cents DESC LIMIT 10""", (start_date, end_date)).fetchall()
                monthly = conn.execute("""SELECT substr(entry_date,1,7) AS period,
                    COALESCE(SUM(CASE WHEN entry_type='income' AND status='paid' THEN amount_cents ELSE 0 END),0) AS revenue_cents,
                    COALESCE(SUM(CASE WHEN entry_type='expense' AND status='paid' THEN amount_cents ELSE 0 END),0) AS expenses_cents
                    FROM finance_entries WHERE entry_date BETWEEN ? AND ? GROUP BY substr(entry_date,1,7) ORDER BY period""",
                    (start_date, end_date)).fetchall()
                category = conn.execute("""SELECT category,
                    COALESCE(SUM(CASE WHEN entry_type='income' AND status='paid' THEN amount_cents ELSE 0 END),0) AS revenue_cents,
                    COALESCE(SUM(CASE WHEN entry_type='expense' AND status='paid' THEN amount_cents ELSE 0 END),0) AS expenses_cents
                    FROM finance_entries WHERE entry_date BETWEEN ? AND ? GROUP BY category ORDER BY category""",
                    (start_date, end_date)).fetchall()
                by_department = conn.execute("""SELECT COALESCE(d.name, 'Sem departamento') AS department,
                    COALESCE(SUM(CASE WHEN f.entry_type='income' AND f.status='paid' THEN f.amount_cents ELSE 0 END),0) AS revenue_cents,
                    COALESCE(SUM(CASE WHEN f.entry_type='expense' AND f.status='paid' THEN f.amount_cents ELSE 0 END),0) AS expenses_cents
                    FROM finance_entries f LEFT JOIN hr_departments d ON d.id=f.department_id
                    WHERE f.entry_date BETWEEN ? AND ? GROUP BY d.name ORDER BY department""", (start_date, end_date)).fetchall()
                by_unit = conn.execute("""SELECT COALESCE(u.name, 'Sem unidade') AS unit,
                    COALESCE(SUM(CASE WHEN f.entry_type='income' AND f.status='paid' THEN f.amount_cents ELSE 0 END),0) AS revenue_cents,
                    COALESCE(SUM(CASE WHEN f.entry_type='expense' AND f.status='paid' THEN f.amount_cents ELSE 0 END),0) AS expenses_cents
                    FROM finance_entries f LEFT JOIN org_units u ON u.id=f.org_unit_id
                    WHERE f.entry_date BETWEEN ? AND ? GROUP BY u.name ORDER BY unit""", (start_date, end_date)).fetchall()
                stock = conn.execute('SELECT COALESCE(SUM(quantity),0) FROM products WHERE active=1').fetchone()[0]
                sold = conn.execute("""SELECT COALESCE(SUM(si.quantity),0) FROM sales_items si JOIN sales s ON s.id=si.sale_id
                    WHERE s.status='paid' AND s.sale_date BETWEEN ? AND ?""", (start_date, end_date)).fetchone()[0]
            totals = dict(totals)
            profit = totals['revenue_cents'] - totals['expenses_cents']
            totals['profit_cents'] = profit
            totals['profit_margin_percent'] = round((profit / totals['revenue_cents']) * 100, 2) if totals['revenue_cents'] else None
            totals['projected_cash_cents'] = profit + totals['planned_income_cents'] - totals['planned_expenses_cents']
            totals['stock_turnover_proxy'] = round(sold / stock, 4) if stock else None
            overdue_summary = {row['entry_type']: {'count': row['count'], 'amount_cents': row['amount_cents']} for row in overdue}
            self.send_json({'period': {'from': start_date, 'to': end_date}, 'totals': totals,
                'overdue': overdue_summary, 'topProducts': [dict(row) for row in top_products],
                'monthly': [dict(row) for row in monthly], 'byCategory': [dict(row) for row in category],
                'byDepartment': [dict(row) for row in by_department], 'byUnit': [dict(row) for row in by_unit]})
            return

        if path == '/api/reports/sales':
            with get_db() as conn:
                rows = conn.execute("""SELECT s.id, s.sale_date, s.status, s.total_cents,
                    u.username AS recorded_by, p.name AS product_name, p.sku, si.quantity,
                    si.unit_price_cents, si.line_total_cents FROM sales s
                    JOIN sales_items si ON si.sale_id=s.id JOIN products p ON p.id=si.product_id
                    LEFT JOIN app_users u ON u.id=s.recorded_by ORDER BY s.sale_date DESC, s.id DESC LIMIT 500""").fetchall()
            self.send_json([dict(row) for row in rows])
            return

        if path == '/api/health':
            self.send_json({'status': 'ok', 'database': 'connected'})
            return

        if path == '/api/telemetry/status':
            self.send_json({'available': telemetry_endpoint_configured()})
            return

        if path == '/api/integrations/google-sheets/status':
            self.send_json({'available': google_sheets_configured()})
            return

        if path == '/api/auth/me':
            self.send_json({
                'user': {key: self.current_user[key] for key in ('id', 'username', 'role')},
                'csrfToken': self.current_user['csrf_token'],
            })
            return

        if path == '/api/auth/users':
            with get_db() as conn:
                users = conn.execute('SELECT id, username, role, active, created_at FROM app_users ORDER BY id').fetchall()
            self.send_json([dict(row) for row in users])
            return

        if path == '/api/work-items':
            with get_db() as conn:
                items = conn.execute(
                    '''SELECT w.*, u.username AS reporter FROM work_items w
                       LEFT JOIN app_users u ON u.id=w.created_by ORDER BY w.updated_at DESC, w.id DESC'''
                ).fetchall()
            self.send_json([dict(row) for row in items])
            return

        if path == '/api/finance/summary':
            with get_db() as conn:
                totals = conn.execute(
                    """SELECT
                        COALESCE(SUM(CASE WHEN entry_type='income' AND status='paid' THEN amount_cents ELSE 0 END),0) income,
                        COALESCE(SUM(CASE WHEN entry_type='expense' AND status='paid' THEN amount_cents ELSE 0 END),0) expenses,
                        COALESCE(SUM(CASE WHEN entry_type='income' AND status='planned' THEN amount_cents ELSE 0 END),0) planned_income,
                        COALESCE(SUM(CASE WHEN entry_type='expense' AND status='planned' THEN amount_cents ELSE 0 END),0) planned_expenses
                        FROM finance_entries"""
                ).fetchone()
            result = dict(totals)
            for key in ('income', 'expenses', 'planned_income', 'planned_expenses'):
                result[key] = result[key] / 100
            result['balance'] = result['income'] - result['expenses']
            result['projectedBalance'] = result['balance'] + result['planned_income'] - result['planned_expenses']
            self.send_json(result)
            return

        if path.startswith('/api/purchasing/'):
            if user['role'] not in {'admin', 'operator', 'finance'}:
                self.send_json({'error': 'Permissão de compras necessária.'}, status=403)
                return
            if path == '/api/purchasing/suppliers':
                if user['role'] not in {'admin', 'operator'}:
                    self.send_json({'error': 'Apenas administração ou operação pode cadastrar fornecedores.'}, status=403)
                    return
                try:
                    name = sanitize_text(payload.get('name'), 'nome do fornecedor', 160)
                    tax_id = sanitize_optional_text(payload.get('tax_id'), 'documento fiscal', 32)
                    email = sanitize_optional_text(payload.get('email'), 'e-mail', 128)
                    phone = sanitize_optional_text(payload.get('phone'), 'telefone', 32)
                except ValueError as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                try:
                    with get_db() as conn:
                        cursor = conn.execute('INSERT INTO suppliers (name, tax_id, email, phone, created_by) VALUES (?, ?, ?, ?, ?)',
                                              (name, tax_id, email, phone, user['id']))
                except sqlite3.IntegrityError:
                    self.send_json({'error': 'Já existe fornecedor com esse documento fiscal.'}, status=409)
                    return
                audit_record(user['id'], 'create', 'supplier', cursor.lastrowid)
                self.send_json({'id': cursor.lastrowid, 'message': 'Fornecedor cadastrado.'}, status=201)
                return
            if path == '/api/purchasing/requests':
                if user['role'] not in {'admin', 'operator'}:
                    self.send_json({'error': 'Apenas administração ou operação pode abrir solicitações.'}, status=403)
                    return
                try:
                    description = sanitize_text(payload.get('description'), 'descrição', 256)
                    items = payload.get('items')
                    if not isinstance(items, list) or not items or len(items) > 100:
                        raise ValueError('Informe de 1 a 100 itens.')
                    normalized = []
                    total = 0
                    for item in items:
                        if not isinstance(item, dict):
                            raise ValueError('Item de compra inválido.')
                        item_description = sanitize_text(item.get('description'), 'descrição do item', 160)
                        quantity = int(item.get('quantity'))
                        unit_cents = int(item.get('estimated_unit_cents', 0))
                        product_id = item.get('product_id')
                        product_id = int(product_id) if product_id is not None else None
                        if quantity < 1 or quantity > 1_000_000 or unit_cents < 0 or unit_cents > 99_999_999_999:
                            raise ValueError('Quantidade ou valor estimado inválido.')
                        normalized.append((product_id, item_description, quantity, unit_cents))
                        total += quantity * unit_cents
                    if total > 99_999_999_999_999:
                        raise ValueError('Valor total excede o limite permitido.')
                except (TypeError, ValueError) as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                with get_db() as conn:
                    conn.execute('BEGIN IMMEDIATE')
                    for product_id, item_description, quantity, unit_cents in normalized:
                        if product_id is not None and not conn.execute('SELECT 1 FROM products WHERE id=? AND active=1', (product_id,)).fetchone():
                            self.send_json({'error': 'Produto vinculado ativo não encontrado.'}, status=400)
                            return
                    cursor = conn.execute('INSERT INTO purchase_requests (description, requested_by, estimated_total_cents) VALUES (?, ?, ?)',
                                          (description, user['id'], total))
                    request_id = cursor.lastrowid
                    for product_id, item_description, quantity, unit_cents in normalized:
                        conn.execute('INSERT INTO purchase_request_items (request_id, product_id, description, quantity, estimated_unit_cents) VALUES (?, ?, ?, ?, ?)',
                                     (request_id, product_id, item_description, quantity, unit_cents))
                audit_record(user['id'], 'create', 'purchase_request', request_id)
                self.send_json({'id': request_id, 'message': 'Solicitação de compra criada.'}, status=201)
                return
            if path == '/api/purchasing/quotes':
                if user['role'] not in {'admin', 'operator'}:
                    self.send_json({'error': 'Apenas administração ou operação pode registrar cotações.'}, status=403)
                    return
                try:
                    request_id = int(payload.get('request_id'))
                    supplier_id = int(payload.get('supplier_id'))
                    total_cents = int(payload.get('total_cents'))
                    lead_days = int(payload.get('lead_days', 0))
                    notes = sanitize_optional_text(payload.get('notes'), 'observações', 512)
                    if total_cents < 0 or total_cents > 99_999_999_999_999 or lead_days < 0 or lead_days > 3650:
                        raise ValueError('Valor da cotação ou prazo inválido.')
                except (TypeError, ValueError) as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                with get_db() as conn:
                    request_row = conn.execute('SELECT status FROM purchase_requests WHERE id=?', (request_id,)).fetchone()
                    supplier = conn.execute("SELECT id FROM suppliers WHERE id=? AND status='active'", (supplier_id,)).fetchone()
                    if request_row is None or supplier is None:
                        self.send_json({'error': 'Solicitação ou fornecedor ativo não encontrado.'}, status=404)
                        return
                    if request_row['status'] not in {'requested', 'quoted'}:
                        self.send_json({'error': 'A solicitação não aceita novas cotações neste estado.'}, status=409)
                        return
                    try:
                        cursor = conn.execute('INSERT INTO supplier_quotes (request_id, supplier_id, total_cents, lead_days, notes, quoted_by) VALUES (?, ?, ?, ?, ?, ?)',
                                              (request_id, supplier_id, total_cents, lead_days, notes, user['id']))
                    except sqlite3.IntegrityError:
                        self.send_json({'error': 'Já existe cotação desse fornecedor para a solicitação.'}, status=409)
                        return
                    conn.execute("UPDATE purchase_requests SET status='quoted', updated_at=CURRENT_TIMESTAMP WHERE id=?", (request_id,))
                audit_record(user['id'], 'quote', 'purchase_request', request_id)
                self.send_json({'id': cursor.lastrowid, 'message': 'Cotação registrada.'}, status=201)
                return
            approve_match = re.fullmatch(r'/api/purchasing/requests/(\\d+)/approve', path)
            if approve_match:
                if user['role'] not in {'admin', 'finance'}:
                    self.send_json({'error': 'Aprovação exige perfil financeiro ou administrador.'}, status=403)
                    return
                request_id = int(approve_match.group(1))
                decision = payload.get('decision')
                comments = payload.get('comments', '')
                try:
                    comments = sanitize_optional_text(comments, 'comentários', 512)
                    if decision not in {'approved', 'rejected'}:
                        raise ValueError('Decisão deve ser approved ou rejected.')
                except ValueError as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                with get_db() as conn:
                    conn.execute('BEGIN IMMEDIATE')
                    request_row = conn.execute('SELECT * FROM purchase_requests WHERE id=?', (request_id,)).fetchone()
                    if request_row is None:
                        self.send_json({'error': 'Solicitação não encontrada.'}, status=404)
                        return
                    if request_row['status'] not in {'requested', 'quoted'}:
                        self.send_json({'error': 'Solicitação já processada ou fora da etapa de aprovação.'}, status=409)
                        return
                    limit = int(os.environ.get('PRODUCT_MANAGER_FINANCE_APPROVAL_LIMIT_CENTS', '10000000'))
                    if user['role'] == 'finance' and request_row['estimated_total_cents'] > limit:
                        self.send_json({'error': 'Valor excede a alçada do perfil financeiro; aprovação de administrador necessária.'}, status=403)
                        return
                    conn.execute('INSERT INTO purchase_approvals (request_id, approver_id, decision, comments) VALUES (?, ?, ?, ?)',
                                 (request_id, user['id'], decision, comments))
                    status_value = 'approved' if decision == 'approved' else 'rejected'
                    conn.execute('UPDATE purchase_requests SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', (status_value, request_id))
                audit_record(user['id'], decision, 'purchase_request', request_id)
                self.send_json({'message': 'Decisão registrada.', 'status': status_value})
                return
            order_match = re.fullmatch(r'/api/purchasing/requests/(\\d+)/order', path)
            if order_match:
                if user['role'] not in {'admin', 'operator'}:
                    self.send_json({'error': 'Apenas administração ou operação pode emitir pedidos.'}, status=403)
                    return
                request_id = int(order_match.group(1))
                try:
                    quote_id = int(payload.get('quote_id'))
                except (TypeError, ValueError):
                    self.send_json({'error': 'Cotação inválida.'}, status=400)
                    return
                with get_db() as conn:
                    conn.execute('BEGIN IMMEDIATE')
                    request_row = conn.execute("SELECT * FROM purchase_requests WHERE id=? AND status='approved'", (request_id,)).fetchone()
                    quote = conn.execute('SELECT * FROM supplier_quotes WHERE id=? AND request_id=?', (quote_id, request_id)).fetchone()
                    if request_row is None or quote is None:
                        self.send_json({'error': 'Solicitação aprovada ou cotação não encontrada.'}, status=409)
                        return
                    approver = conn.execute("""SELECT u.role FROM purchase_approvals a JOIN app_users u ON u.id=a.approver_id
                        WHERE a.request_id=? AND a.decision='approved' ORDER BY a.id DESC LIMIT 1""", (request_id,)).fetchone()
                    limit = int(os.environ.get('PRODUCT_MANAGER_FINANCE_APPROVAL_LIMIT_CENTS', '10000000'))
                    if approver and approver['role'] == 'finance' and quote['total_cents'] > limit:
                        self.send_json({'error': 'A cotação selecionada excede a alçada financeira; solicite aprovação administrativa.'}, status=403)
                        return
                    cursor = conn.execute("INSERT INTO purchase_orders (request_id, supplier_id, quote_id, total_cents, approved_by, approved_at, created_by) VALUES (?, ?, ?, ?, (SELECT approver_id FROM purchase_approvals WHERE request_id=? AND decision='approved' ORDER BY id DESC LIMIT 1), CURRENT_TIMESTAMP, ?)",
                                          (request_id, quote['supplier_id'], quote_id, quote['total_cents'], request_id, user['id']))
                    order_id = cursor.lastrowid
                    items = conn.execute('SELECT * FROM purchase_request_items WHERE request_id=? ORDER BY id', (request_id,)).fetchall()
                    total_weight = sum(item['quantity'] * item['estimated_unit_cents'] for item in items)
                    allocated = 0
                    for index, item in enumerate(items):
                        if index == len(items) - 1:
                            line_total = quote['total_cents'] - allocated
                        elif total_weight > 0:
                            line_total = quote['total_cents'] * item['quantity'] * item['estimated_unit_cents'] // total_weight
                        else:
                            total_quantity = max(1, sum(x['quantity'] for x in items))
                            line_total = quote['total_cents'] * item['quantity'] // total_quantity
                        allocated += line_total
                        unit_cents = line_total // item['quantity']
                        conn.execute('INSERT INTO purchase_order_items (order_id, product_id, description, ordered_quantity, unit_cents) VALUES (?, ?, ?, ?, ?)',
                                     (order_id, item['product_id'], item['description'], item['quantity'], unit_cents))
                    conn.execute("UPDATE purchase_requests SET status='ordered', updated_at=CURRENT_TIMESTAMP WHERE id=?", (request_id,))
                audit_record(user['id'], 'create', 'purchase_order', order_id)
                self.send_json({'id': order_id, 'message': 'Pedido de compra emitido.'}, status=201)
                return
            receive_match = re.fullmatch(r'/api/purchasing/orders/(\\d+)/receive', path)
            if receive_match:
                if user['role'] not in {'admin', 'operator'}:
                    self.send_json({'error': 'Apenas administração ou operação pode receber mercadorias.'}, status=403)
                    return
                order_id = int(receive_match.group(1))
                try:
                    received_items = payload.get('items')
                    if not isinstance(received_items, list) or not received_items:
                        raise ValueError('Informe os itens recebidos.')
                    received = []
                    for item in received_items:
                        if not isinstance(item, dict):
                            raise ValueError('Item recebido inválido.')
                        received.append((int(item.get('item_id')), int(item.get('quantity'))))
                    if any(item_id < 1 or quantity < 1 for item_id, quantity in received):
                        raise ValueError('Identificadores e quantidades devem ser positivos.')
                except (TypeError, ValueError) as exc:
                    self.send_json({'error': str(exc)}, status=400)
                    return
                with get_db() as conn:
                    conn.execute('BEGIN IMMEDIATE')
                    order = conn.execute("SELECT * FROM purchase_orders WHERE id=? AND status IN ('ordered','partially_received')", (order_id,)).fetchone()
                    if order is None:
                        self.send_json({'error': 'Pedido não encontrado ou já recebido/cancelado.'}, status=409)
                        return
                    aggregate_received = {}
                    for item_id, quantity in received:
                        aggregate_received[item_id] = aggregate_received.get(item_id, 0) + quantity
                    for item_id, quantity in aggregate_received.items():
                        item = conn.execute('SELECT * FROM purchase_order_items WHERE id=? AND order_id=?', (item_id, order_id)).fetchone()
                        if item is None or item['received_quantity'] + quantity > item['ordered_quantity']:
                            self.send_json({'error': 'Item inválido ou quantidade recebida excede o pedido.'}, status=400)
                            return
                    received = list(aggregate_received.items())
                    for item_id, quantity in received:
                        item = conn.execute('SELECT * FROM purchase_order_items WHERE id=?', (item_id, order_id)).fetchone()
                        conn.execute('UPDATE purchase_order_items SET received_quantity=received_quantity+? WHERE id=?', (quantity, item_id))
                        if item['product_id'] is not None:
                            conn.execute('UPDATE products SET quantity=quantity+? WHERE id=?', (quantity, item['product_id']))
                    remaining = conn.execute('SELECT COUNT(*) FROM purchase_order_items WHERE received_quantity < ordered_quantity AND order_id=?', (order_id,)).fetchone()[0]
                    status_value = 'partially_received' if remaining else 'received'
                    conn.execute('UPDATE purchase_orders SET status=? WHERE id=?', (status_value, order_id))
                    if not remaining:
                        conn.execute("UPDATE purchase_requests SET status='received', updated_at=CURRENT_TIMESTAMP WHERE id=?", (order['request_id'],))
                audit_record(user['id'], 'receive', 'purchase_order', order_id)
                self.send_json({'message': 'Recebimento registrado e estoque atualizado.', 'status': status_value})
                return
            self.send_json({'error': 'Rota de compras não encontrada.'}, status=404)
            return

        if path == '/api/finance/entries':
            with get_db() as conn:
                rows = conn.execute(
                    '''SELECT e.id, e.entry_type, e.category, e.description, e.entry_date,
                              e.status, e.created_at, u.username AS created_by,
                              e.amount_cents / 100.0 AS amount
                       FROM finance_entries e LEFT JOIN app_users u ON u.id=e.created_by
                       ORDER BY e.entry_date DESC, e.id DESC LIMIT 500'''
                ).fetchall()
            self.send_json([dict(row) for row in rows])
            return

        if path == '/api/alerts/stock':
            threshold = low_stock_default()
            with get_db() as conn:
                rows = conn.execute(
                    '''SELECT p.id, p.name, p.sku, p.category, p.quantity,
                              COALESCE(t.minimum_quantity, ?) AS minimum_quantity,
                              CASE WHEN p.quantity = 0 THEN 'critical' ELSE 'warning' END AS severity,
                              a.acknowledged_at
                       FROM products p
                       LEFT JOIN stock_thresholds t ON t.product_id=p.id
                       LEFT JOIN stock_alert_acknowledgements a
                         ON a.product_id=p.id AND a.acknowledged_quantity=p.quantity
                       WHERE p.active=1 AND p.quantity <= COALESCE(t.minimum_quantity, ?) AND a.product_id IS NULL
                       ORDER BY CASE WHEN p.quantity=0 THEN 0 ELSE 1 END, p.quantity ASC, p.name ASC''',
                    (threshold, threshold),
                ).fetchall()
            self.send_json([dict(row) for row in rows])
            return

        if path == '/api/alerts/config':
            self.send_json({'defaultMinimumQuantity': low_stock_default()})
            return

        self.send_json({'error': 'Rota não encontrada.'}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            self.send_json({'error': 'Content-Length inválido.'}, status=400)
            return
        if length < 0 or length > MAX_BODY_BYTES:
            self.send_json({'error': 'Requisição excede o limite permitido.'}, status=413)
            return
        raw = self.rfile.read(length) if length else b''

        try:
            payload = json.loads(raw.decode('utf-8')) if raw else {}
        except json.JSONDecodeError:
            self.send_json({'error': 'JSON inválido.'}, status=400)
            return
        if not isinstance(payload, dict):
            self.send_json({'error': 'O corpo deve ser um objeto JSON.'}, status=400)
            return

        if path == '/api/auth/login':
            username = payload.get('username', '')
            password = payload.get('password', '')
            if not isinstance(username, str) or not isinstance(password, str):
                self.send_json({'error': 'Usuário ou senha inválidos.'}, status=401)
                return
            self.login_user(username, password)
            return

        if path == '/api/auth/setup':
            self.handle_first_admin_setup(payload)
            return

        user = self.require_authenticated_request(path)
        if user is None:
            return
        self.current_user = user
        if not self.validate_csrf(user):
            return

        if path == '/api/auth/logout':
            with get_db() as conn:
                conn.execute('DELETE FROM app_sessions WHERE token_hash=?', (user['token_hash'],))
            audit_record(user['id'], 'logout', 'session')
            body = json.dumps({'message': 'Sessão encerrada'}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_auth_cookie(None, clear=True)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        if path == '/api/auth/users':
            if user['role'] != 'admin':
                self.send_json({'error': 'Apenas administradores podem criar usuários.'}, status=403)
                return
            username = payload.get('username', '')
            password = payload.get('password', '')
            role = payload.get('role', '')
            if not isinstance(username, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{3,64}', username.strip()):
                self.send_json({'error': 'Nome de usuário inválido.'}, status=400)
                return
            if not isinstance(password, str) or len(password) < 12 or len(password) > 256:
                self.send_json({'error': 'A senha deve ter entre 12 e 256 caracteres.'}, status=400)
                return
            if not isinstance(role, str) or role not in USER_ROLES:
                self.send_json({'error': 'Papel de usuário inválido.'}, status=400)
                return
            try:
                with get_db() as conn:
                    cursor = conn.execute(
                        'INSERT INTO app_users (username, password_hash, role) VALUES (?, ?, ?)',
                        (username.strip(), hash_password(password), role),
                    )
                    new_user_id = cursor.lastrowid
            except sqlite3.IntegrityError:
                self.send_json({'error': 'Esse nome de usuário já existe.'}, status=409)
                return
            audit_record(user['id'], 'create', 'user', new_user_id)
            self.send_json({'message': 'Usuário criado.', 'id': new_user_id}, status=201)
            return

        deactivate_match = re.fullmatch(r'/api/auth/users/(\d+)/deactivate', path)
        if deactivate_match:
            if user['role'] != 'admin':
                self.send_json({'error': 'Apenas administradores podem desativar usuários.'}, status=403)
                return
            target_id = int(deactivate_match.group(1))
            if target_id == user['id']:
                self.send_json({'error': 'Não é possível desativar a própria sessão administrativa.'}, status=400)
                return
            with get_db() as conn:
                conn.execute('BEGIN IMMEDIATE')
                target = conn.execute('SELECT id, role, active FROM app_users WHERE id=?', (target_id,)).fetchone()
                if target is None or not target['active']:
                    self.send_json({'error': 'Usuário não encontrado ou já desativado.'}, status=404)
                    return
                if target['role'] == 'admin' and conn.execute(
                    "SELECT COUNT(*) FROM app_users WHERE role='admin' AND active=1"
                ).fetchone()[0] <= 1:
                    self.send_json({'error': 'O último administrador ativo não pode ser desativado.'}, status=409)
                    return
                conn.execute('UPDATE app_users SET active=0 WHERE id=?', (target_id,))
                conn.execute('DELETE FROM app_sessions WHERE user_id=?', (target_id,))
            audit_record(user['id'], 'deactivate', 'user', target_id)
            self.send_json({'message': 'Usuário desativado.'})
            return

        if path == '/api/finance/entries':
            if not self.require_permission(user, 'finance:write'):
                return
            entry_type = payload.get('entry_type')
            category = payload.get('category')
            description = payload.get('description')
            status = payload.get('status', 'paid')
            try:
                if entry_type not in {'income', 'expense'} or status not in {'planned', 'paid'}:
                    raise ValueError('Tipo ou situação financeira inválida.')
                category = sanitize_text(category, 'categoria', 64)
                description = sanitize_text(description, 'descrição', 256)
                amount = Decimal(str(payload.get('amount')))
                cents = amount * 100
                if not amount.is_finite() or cents != cents.to_integral_value() or cents <= 0 or cents > 999_999_999_999_99:
                    raise ValueError('O valor deve ser maior que zero.')
                amount_cents = int(cents)
                entry_date = date.fromisoformat(payload.get('entry_date', date.today().isoformat())).isoformat()
            except (TypeError, ValueError, InvalidOperation) as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            with get_db() as conn:
                cursor = conn.execute(
                    '''INSERT INTO finance_entries (entry_type, category, description, amount_cents, entry_date, status, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (entry_type, category, description, amount_cents, entry_date, status, user['id']),
                )
                entry_id = cursor.lastrowid
            audit_record(user['id'], 'create', 'finance_entry', entry_id)
            self.send_json({'message': 'Lançamento financeiro criado.', 'id': entry_id}, status=201)
            return

        if path == '/api/work-items':
            item_type = payload.get('item_type')
            severity = payload.get('severity')
            try:
                if item_type not in {'bug', 'risk'} or severity not in {'low', 'medium', 'high', 'critical'}:
                    raise ValueError('Tipo ou prioridade inválida.')
                title = sanitize_text(payload.get('title'), 'título', 160)
                description = sanitize_text(payload.get('description'), 'descrição', 2000)
                owner = sanitize_optional_text(payload.get('owner'), 'responsável', 64)
                due_date = payload.get('due_date') or None
                if due_date:
                    due_date = date.fromisoformat(due_date).isoformat()
                probability = int(payload.get('probability')) if item_type == 'risk' else None
                impact = int(payload.get('impact')) if item_type == 'risk' else None
                if item_type == 'risk' and (probability not in range(1, 6) or impact not in range(1, 6)):
                    raise ValueError('Probabilidade e impacto devem ficar entre 1 e 5.')
            except (TypeError, ValueError) as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            with get_db() as conn:
                cursor = conn.execute(
                    '''INSERT INTO work_items (item_type, title, description, severity, probability, impact,
                                              owner, due_date, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (item_type, title, description, severity, probability, impact, owner, due_date, user['id']),
                )
                item_id = cursor.lastrowid
            audit_record(user['id'], 'create', item_type, item_id)
            self.send_json({'message': 'Registro criado.', 'id': item_id}, status=201)
            return

        work_item_update = re.fullmatch(r'/api/work-items/(\d+)', path)
        if work_item_update:
            if not self.require_permission(user, 'catalog:write'):
                return
            item_id = int(work_item_update.group(1))
            try:
                status_value = normalize_status(payload.get('status'), {'open', 'in_progress', 'resolved', 'closed'}, 'status')
                owner = sanitize_optional_text(payload.get('owner'), 'responsável', 64)
            except ValueError as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            with get_db() as conn:
                cursor = conn.execute(
                    'UPDATE work_items SET status=?, owner=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                    (status_value, owner, item_id),
                )
                if not cursor.rowcount:
                    self.send_json({'error': 'Registro não encontrado.'}, status=404)
                    return
            audit_record(user['id'], 'update', 'work_item', item_id)
            self.send_json({'message': 'Registro atualizado.'})
            return

        delete_finance_match = re.fullmatch(r'/api/finance/entries/(\d+)/delete', path)
        if delete_finance_match:
            if user['role'] not in {'admin', 'finance'}:
                self.send_json({'error': 'Permissão financeira necessária.'}, status=403)
                return
            entry_id = int(delete_finance_match.group(1))
            with get_db() as conn:
                result = conn.execute('DELETE FROM finance_entries WHERE id=?', (entry_id,))
                if not result.rowcount:
                    self.send_json({'error': 'Lançamento não encontrado.'}, status=404)
                    return
            audit_record(user['id'], 'delete', 'finance_entry', entry_id)
            self.send_json({'message': 'Lançamento removido.'})
            return

        threshold_match = re.fullmatch(r'/api/alerts/stock/(\d+)/threshold', path)
        if threshold_match:
            if not self.require_permission(user, 'alerts:write'):
                return
            product_id = int(threshold_match.group(1))
            try:
                minimum = int(payload.get('minimum_quantity'))
                if minimum < 0 or minimum > 1_000_000:
                    raise ValueError('Limite deve estar entre 0 e 1.000.000.')
            except (TypeError, ValueError) as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            with get_db() as conn:
                if not conn.execute('SELECT 1 FROM products WHERE id=?', (product_id,)).fetchone():
                    self.send_json({'error': 'Produto não encontrado.'}, status=404)
                    return
                conn.execute(
                    '''INSERT INTO stock_thresholds (product_id, minimum_quantity, updated_by, updated_at)
                       VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                       ON CONFLICT(product_id) DO UPDATE SET minimum_quantity=excluded.minimum_quantity,
                         updated_by=excluded.updated_by, updated_at=CURRENT_TIMESTAMP''',
                    (product_id, minimum, user['id']),
                )
                conn.execute('DELETE FROM stock_alert_acknowledgements WHERE product_id=?', (product_id,))
            audit_record(user['id'], 'set_threshold', 'product', product_id)
            self.send_json({'message': 'Limite de estoque atualizado.'})
            return

        acknowledge_match = re.fullmatch(r'/api/alerts/stock/(\d+)/acknowledge', path)
        if acknowledge_match:
            product_id = int(acknowledge_match.group(1))
            with get_db() as conn:
                product = conn.execute('SELECT quantity FROM products WHERE id=?', (product_id,)).fetchone()
                if product is None:
                    self.send_json({'error': 'Produto não encontrado.'}, status=404)
                    return
                conn.execute(
                    '''INSERT INTO stock_alert_acknowledgements (product_id, acknowledged_quantity, acknowledged_by)
                       VALUES (?, ?, ?)
                       ON CONFLICT(product_id) DO UPDATE SET acknowledged_quantity=excluded.acknowledged_quantity,
                         acknowledged_by=excluded.acknowledged_by, acknowledged_at=CURRENT_TIMESTAMP''',
                    (product_id, product['quantity'], user['id']),
                )
            audit_record(user['id'], 'acknowledge', 'stock_alert', product_id)
            self.send_json({'message': 'Alerta marcado como visto.'})
            return

        product_action = re.fullmatch(r'/api/products/(\d+)/(deactivate|activate|delete)', path)
        if product_action:
            if not self.require_permission(user, 'catalog:write'):
                return
            product_id = int(product_action.group(1))
            action = product_action.group(2)
            if action == 'delete' and user['role'] != 'admin':
                self.send_json({'error': 'A remoção definitiva exige perfil administrador.'}, status=403)
                return
            with get_db() as conn:
                exists = conn.execute('SELECT id FROM products WHERE id=?', (product_id,)).fetchone()
                if exists is None:
                    self.send_json({'error': 'Produto não encontrado.'}, status=404)
                    return
                if action == 'delete':
                    conn.execute('DELETE FROM products WHERE id=?', (product_id,))
                    audit_action = 'delete'
                    message = 'Produto removido definitivamente.'
                else:
                    active = 0 if action == 'deactivate' else 1
                    conn.execute('UPDATE products SET active=? WHERE id=?', (active, product_id))
                    audit_action = action
                    message = 'Produto desativado.' if not active else 'Produto reativado.'
            audit_record(user['id'], audit_action, 'product', product_id)
            self.send_json({'message': message})
            return

        product_update = re.fullmatch(r'/api/products/(\d+)', path)
        if product_update:
            if not self.require_permission(user, 'catalog:write'):
                return
            product_id = int(product_update.group(1))
            try:
                values = validate_product_payload(payload)
            except (TypeError, ValueError) as exc:
                self.send_json({'error': str(exc)}, status=400)
                return
            try:
                with get_db() as conn:
                    cursor = conn.execute(
                        '''UPDATE products SET name=?, category=?, sku=?, reference=?, brand=?, status=?, price=?,
                                  quantity=?, supplier=?, notes=? WHERE id=?''',
                        (*values, product_id),
                    )
                    if not cursor.rowcount:
                        self.send_json({'error': 'Produto não encontrado.'}, status=404)
                        return
            except sqlite3.IntegrityError as exc:
                self.send_json({'error': f'Outro produto já usa esse SKU: {exc}'}, status=409)
                return
            audit_record(user['id'], 'update', 'product', product_id)
            self.send_json({'message': 'Produto atualizado.'})
            return

        if path == '/api/telemetry':
            event_name = payload.get('event')
            if not isinstance(event_name, str) or event_name not in TELEMETRY_EVENTS:
                self.send_json({'error': 'Evento de diagnóstico não permitido.'}, status=400)
                return
            if send_telemetry_event(event_name):
                self.send_json({'received': True}, status=202)
            else:
                self.send_json({'received': False}, status=503)
            return

        if path == '/api/integrations/google-sheets/export':
            if user['role'] != 'admin':
                self.send_json({'error': 'Apenas administradores podem exportar diretamente para a planilha configurada.'}, status=403)
                return
            if not google_sheets_configured():
                self.send_json({'error': 'A integração Google Sheets não está configurada pelo administrador.'}, status=503)
                return
            self.export_to_google_sheets()
            return

        if path == '/api/clients':
            if not self.require_permission(user, 'catalog:write'):
                return
            self.create_client(payload)
            return

        if path == '/api/products':
            if not self.require_permission(user, 'catalog:write'):
                return
            self.create_product(payload)
            return

        self.send_json({'error': 'Rota não encontrada.'}, status=404)

    def create_client(self, payload):
        try:
            name = sanitize_text(payload.get('name'), 'nome', 128)
            username = sanitize_text(payload.get('username'), 'username', 64)
            email = validate_email(sanitize_text(payload.get('email'), 'email', 128))
            phone = validate_phone(sanitize_text(payload.get('phone'), 'telefone', 32))
            cpf = validate_cpf(sanitize_text(payload.get('cpf'), 'cpf', 20))
            status = normalize_status(payload.get('status'), CLIENT_ALLOWED_STATUS, 'status')
            city = sanitize_text(payload.get('city'), 'cidade', 128)
            role = sanitize_text(payload.get('role'), 'perfil', 64)
            notes = sanitize_optional_text(payload.get('notes'), 'observações', 512)
        except ValueError as exc:
            self.send_json({'error': str(exc)}, status=400)
            return

        try:
            with get_db() as conn:
                cursor = conn.execute(
                    '''INSERT INTO clients (name, username, email, phone, cpf, status, city, role, notes, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (name, username, email, phone, cpf, status, city, role, notes, self.current_user['id']),
                )
                conn.commit()
        except sqlite3.IntegrityError as exc:
            self.send_json({'error': f'Usuário duplicado ou campo único já existente: {exc}'}, status=409)
            return

        audit_record(self.current_user['id'], 'create', 'client', cursor.lastrowid)
        self.send_json({'message': 'Cliente criado com sucesso.', 'id': cursor.lastrowid}, status=201)

    def create_product(self, payload):
        try:
            values = validate_product_payload(payload)
        except (TypeError, ValueError) as exc:
            self.send_json({'error': str(exc)}, status=400)
            return

        try:
            with get_db() as conn:
                cursor = conn.execute(
                    '''INSERT INTO products (name, category, sku, reference, brand, status, price, quantity, supplier, notes, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (*values, self.current_user['id']),
                )
                conn.commit()
        except sqlite3.IntegrityError as exc:
            self.send_json({'error': f'Produto duplicado ou campo único já existente: {exc}'}, status=409)
            return

        audit_record(self.current_user['id'], 'create', 'product', cursor.lastrowid)
        self.send_json({'message': 'Produto criado com sucesso.', 'id': cursor.lastrowid}, status=201)

    def export_dashboard(self):
        rows = dashboard_export_rows()
        output = io.StringIO(newline='')
        writer = csv.writer(output)
        for row in rows:
            writer.writerow([spreadsheet_safe(value) if isinstance(value, str) else value for value in row])

        body = ('\ufeff' + output.getvalue()).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/csv; charset=utf-8')
        self.send_header('Content-Disposition', 'attachment; filename="dashboard-product-manager.csv"')
        self.send_header('Content-Length', str(len(body)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def export_dashboard_xlsx(self):
        body = build_dashboard_xlsx(dashboard_export_rows())
        self.send_response(200)
        self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.send_header('Content-Disposition', 'attachment; filename="product-manager-dashboard.xlsx"')
        self.send_header('Content-Length', str(len(body)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def export_to_google_sheets(self):
        spreadsheet_id = os.environ['PRODUCT_MANAGER_GOOGLE_SHEETS_SPREADSHEET_ID'].strip()
        access_token = os.environ['PRODUCT_MANAGER_GOOGLE_SHEETS_ACCESS_TOKEN'].strip()
        cell_range = os.environ.get('PRODUCT_MANAGER_GOOGLE_SHEETS_RANGE', 'Export!A1').strip() or 'Export!A1'
        if not re.fullmatch(r'[A-Za-z0-9_-]+', spreadsheet_id):
            self.send_json({'error': 'O ID da planilha Google configurado é inválido.'}, status=503)
            return

        encoded_range = urllib.parse.quote(cell_range, safe="!:$'")
        query = urllib.parse.urlencode({'valueInputOption': 'RAW'})
        url = (f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/'
               f'{encoded_range}?{query}')
        body = json.dumps({'majorDimension': 'ROWS', 'values': dashboard_export_rows()}, ensure_ascii=False).encode('utf-8')
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json; charset=utf-8',
            },
            method='PUT',
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                if not 200 <= response.status < 300:
                    self.send_json({'error': 'O Google Sheets recusou a exportação.'}, status=502)
                    return
        except urllib.error.HTTPError as error:
            status = 401 if error.code == 401 else 403 if error.code == 403 else 502
            message = 'Credencial Google Sheets inválida ou expirada.' if status == 401 else 'Não foi possível gravar na planilha configurada.'
            self.send_json({'error': message}, status=status)
            return
        except (urllib.error.URLError, TimeoutError, ValueError):
            self.send_json({'error': 'Falha de conexão com o Google Sheets.'}, status=502)
            return

        self.send_json({
            'message': 'Dashboard exportado para Google Sheets.',
            'spreadsheetUrl': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit',
        }, status=200)

    @staticmethod
    def _content_type_for(file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == '.css':
            return 'text/css; charset=utf-8'
        if suffix == '.js':
            return 'application/javascript; charset=utf-8'
        if suffix == '.json':
            return 'application/json; charset=utf-8'
        if suffix == '.webmanifest':
            return 'application/manifest+json; charset=utf-8'
        if suffix == '.svg':
            return 'image/svg+xml; charset=utf-8'
        if suffix == '.html':
            return 'text/html; charset=utf-8'
        return 'application/octet-stream'

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_security_headers(self):
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        self.send_header(
            'Content-Security-Policy',
            "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
        )
        self.send_header('Cache-Control', 'no-store')

    def serve_file(self, file_path: Path, content_type: str, allow_missing: bool = False):
        try:
            resolved = file_path.resolve()
            resolved.relative_to(BASE_DIR)
        except ValueError:
            self.send_json({'error': 'Caminho inválido.'}, status=400)
            return

        if allow_missing and not resolved.exists():
            self.send_json({'error': 'Arquivo não encontrado.'}, status=404)
            return

        if not resolved.exists():
            self.send_json({'error': 'Arquivo não encontrado.'}, status=404)
            return

        if not resolved.is_file():
            self.send_json({'error': 'Recurso inválido.'}, status=400)
            return

        body = resolved.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    host = os.environ.get('PRODUCT_MANAGER_HOST', '127.0.0.1')
    port = int(os.environ.get('PRODUCT_MANAGER_PORT', '8000'))
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f'Product Manager disponível em http://{host}:{port}')
    server.serve_forever()
