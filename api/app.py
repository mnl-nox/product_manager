from __future__ import annotations

import json
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db' / 'login_term.db'
SCHEMA_PATH = BASE_DIR / 'db' / 'schema.sql'
FIELD_MAPPING_PATH = BASE_DIR / 'config' / 'field-mapping.json'
UI_DIR = BASE_DIR / 'ui'

CLIENT_ALLOWED_STATUS = {'active', 'inactive', 'pending'}
PRODUCT_ALLOWED_STATUS = {'available', 'reserved', 'out_of_stock'}


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        schema_sql = SCHEMA_PATH.read_text(encoding='utf-8')
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(schema_sql)


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


def seed_default_data() -> None:
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
    server_version = 'login_term/1.0'

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/':
            self.serve_file(UI_DIR / 'index.html', 'text/html; charset=utf-8')
            return

        if path.startswith('/ui/'):
            asset_path = UI_DIR / path[len('/ui/'):]
            self.serve_file(asset_path, 'text/css; charset=utf-8' if asset_path.suffix == '.css' else 'application/javascript; charset=utf-8' if asset_path.suffix == '.js' else 'text/html; charset=utf-8')
            return

        if path in ('/styles.css', '/app.js'):
            asset_path = UI_DIR / path.lstrip('/')
            self.serve_file(asset_path, 'text/css; charset=utf-8' if path.endswith('.css') else 'application/javascript; charset=utf-8')
            return

        if path == '/api/field-mapping':
            self.send_json(json.loads(FIELD_MAPPING_PATH.read_text(encoding='utf-8')))
            return

        if path == '/api/summary':
            with get_db() as conn:
                clients_count = conn.execute('SELECT COUNT(*) AS total FROM clients').fetchone()['total']
                products_count = conn.execute('SELECT COUNT(*) AS total FROM products').fetchone()['total']
                active_count = conn.execute("SELECT COUNT(*) AS total FROM clients WHERE status = 'active'").fetchone()['total']
                stock_total = conn.execute('SELECT COALESCE(SUM(quantity), 0) AS total FROM products').fetchone()['total']
            self.send_json({
                'clients': clients_count,
                'products': products_count,
                'activeClients': active_count,
                'totalStock': stock_total,
            })
            return

        if path == '/api/clients':
            with get_db() as conn:
                rows = conn.execute('SELECT * FROM clients ORDER BY id ASC').fetchall()
            self.send_json([dict(row) for row in rows])
            return

        if path == '/api/products':
            with get_db() as conn:
                rows = conn.execute('SELECT * FROM products ORDER BY id ASC').fetchall()
            self.send_json([dict(row) for row in rows])
            return

        if path == '/api/health':
            self.send_json({'status': 'ok', 'database': str(DB_PATH)})
            return

        self.serve_file(UI_DIR / path.lstrip('/'), 'application/octet-stream', allow_missing=True)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length) if length else b''

        try:
            payload = json.loads(raw.decode('utf-8')) if raw else {}
        except json.JSONDecodeError:
            self.send_json({'error': 'JSON inválido.'}, status=400)
            return

        if path == '/api/clients':
            self.create_client(payload)
            return

        if path == '/api/products':
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
            notes = sanitize_text(payload.get('notes') or '', 'observações', 512)
        except ValueError as exc:
            self.send_json({'error': str(exc)}, status=400)
            return

        try:
            with get_db() as conn:
                cursor = conn.execute(
                    '''INSERT INTO clients (name, username, email, phone, cpf, status, city, role, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (name, username, email, phone, cpf, status, city, role, notes),
                )
                conn.commit()
        except sqlite3.IntegrityError as exc:
            self.send_json({'error': f'Usuário duplicado ou campo único já existente: {exc}'}, status=409)
            return

        self.send_json({'message': 'Cliente criado com sucesso.', 'id': cursor.lastrowid}, status=201)

    def create_product(self, payload):
        try:
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
            if price < 0:
                raise ValueError('O preço não pode ser negativo.')
            quantity_value = payload.get('quantity')
            if quantity_value is None:
                raise ValueError('O campo quantidade é obrigatório.')
            quantity = int(quantity_value)
            if quantity < 0:
                raise ValueError('A quantidade não pode ser negativa.')
            supplier = sanitize_text(payload.get('supplier'), 'fornecedor', 128)
            notes = sanitize_text(payload.get('notes') or '', 'observações', 512)
        except (TypeError, ValueError) as exc:
            self.send_json({'error': str(exc)}, status=400)
            return

        try:
            with get_db() as conn:
                cursor = conn.execute(
                    '''INSERT INTO products (name, category, sku, reference, brand, status, price, quantity, supplier, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (name, category, sku, reference, brand, status, price, quantity, supplier, notes),
                )
                conn.commit()
        except sqlite3.IntegrityError as exc:
            self.send_json({'error': f'Produto duplicado ou campo único já existente: {exc}'}, status=409)
            return

        self.send_json({'message': 'Produto criado com sucesso.', 'id': cursor.lastrowid}, status=201)

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        self.send_header(
            'Content-Security-Policy',
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'",
        )
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, file_path: Path, content_type: str, allow_missing: bool = False):
        resolved = file_path.resolve()
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
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        self.send_header(
            'Content-Security-Policy',
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'",
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8000), AppHandler)
    print('Servidor login_term em http://127.0.0.1:8000')
    server.serve_forever()
