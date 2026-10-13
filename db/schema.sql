PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS app_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin','operator','finance','viewer')),
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_sessions (
    token_hash TEXT PRIMARY KEY,
    csrf_token TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    expires_at INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_app_sessions_expiry ON app_sessions(expires_at);

CREATE TABLE IF NOT EXISTS auth_login_limits (
    username_hash TEXT PRIMARY KEY,
    failed_count INTEGER NOT NULL DEFAULT 0,
    window_started INTEGER NOT NULL,
    locked_until INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS finance_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_type TEXT NOT NULL CHECK(entry_type IN ('income','expense')),
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
    entry_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'paid' CHECK(status IN ('planned','paid','cancelled')),
    department_id INTEGER REFERENCES hr_departments(id),
    org_unit_id INTEGER REFERENCES org_units(id),
    created_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_finance_entries_date ON finance_entries(entry_date, id);

CREATE TABLE IF NOT EXISTS stock_thresholds (
    product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    minimum_quantity INTEGER NOT NULL CHECK(minimum_quantity >= 0),
    updated_by INTEGER REFERENCES app_users(id),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_alert_acknowledgements (
    product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    acknowledged_quantity INTEGER NOT NULL,
    acknowledged_by INTEGER REFERENCES app_users(id),
    acknowledged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER REFERENCES app_users(id),
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS work_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL CHECK(item_type IN ('bug','risk')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('low','medium','high','critical')),
    probability INTEGER CHECK(probability BETWEEN 1 AND 5),
    impact INTEGER CHECK(impact BETWEEN 1 AND 5),
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','in_progress','resolved','closed')),
    owner TEXT NOT NULL DEFAULT '',
    due_date TEXT,
    created_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status, item_type, id);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('active','inactive','pending')),
    city TEXT NOT NULL,
    role TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES app_users(id)
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    reference TEXT NOT NULL,
    brand TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('available','reserved','out_of_stock')),
    price REAL NOT NULL CHECK(price >= 0),
    quantity INTEGER NOT NULL CHECK(quantity >= 0),
    supplier TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES app_users(id),
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tax_id TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','inactive')),
    created_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_suppliers_tax_id ON suppliers(tax_id) WHERE tax_id <> '';

CREATE TABLE IF NOT EXISTS purchase_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    requested_by INTEGER NOT NULL REFERENCES app_users(id),
    status TEXT NOT NULL DEFAULT 'requested' CHECK(status IN ('requested','quoted','approved','rejected','ordered','received','cancelled')),
    estimated_total_cents INTEGER NOT NULL DEFAULT 0 CHECK(estimated_total_cents >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS purchase_request_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL REFERENCES purchase_requests(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    estimated_unit_cents INTEGER NOT NULL DEFAULT 0 CHECK(estimated_unit_cents >= 0)
);
CREATE TABLE IF NOT EXISTS supplier_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL REFERENCES purchase_requests(id) ON DELETE CASCADE,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    total_cents INTEGER NOT NULL CHECK(total_cents >= 0),
    lead_days INTEGER NOT NULL DEFAULT 0 CHECK(lead_days >= 0),
    notes TEXT NOT NULL DEFAULT '',
    quoted_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(request_id, supplier_id)
);
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL UNIQUE REFERENCES purchase_requests(id),
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    quote_id INTEGER REFERENCES supplier_quotes(id),
    total_cents INTEGER NOT NULL CHECK(total_cents >= 0),
    status TEXT NOT NULL DEFAULT 'ordered' CHECK(status IN ('ordered','partially_received','received','cancelled')),
    approved_by INTEGER REFERENCES app_users(id),
    approved_at TEXT,
    created_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    description TEXT NOT NULL,
    ordered_quantity INTEGER NOT NULL CHECK(ordered_quantity > 0),
    received_quantity INTEGER NOT NULL DEFAULT 0 CHECK(received_quantity >= 0 AND received_quantity <= ordered_quantity),
    unit_cents INTEGER NOT NULL CHECK(unit_cents >= 0)
);
CREATE TABLE IF NOT EXISTS purchase_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL REFERENCES purchase_requests(id) ON DELETE CASCADE,
    approver_id INTEGER NOT NULL REFERENCES app_users(id),
    decision TEXT NOT NULL CHECK(decision IN ('approved','rejected')),
    comments TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_purchase_requests_status ON purchase_requests(status, created_at);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status, created_at);

CREATE TABLE IF NOT EXISTS hr_departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS hr_employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    job_title TEXT NOT NULL,
    department_id INTEGER REFERENCES hr_departments(id),
    hire_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','leave','inactive')),
    notes TEXT NOT NULL DEFAULT '',
    created_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_hr_employees_department ON hr_employees(department_id, status);
CREATE TABLE IF NOT EXISTS hr_absences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    absence_type TEXT NOT NULL CHECK(absence_type IN ('vacation','sick_leave','personal','other')),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'requested' CHECK(status IN ('requested','approved','rejected','cancelled')),
    notes TEXT NOT NULL DEFAULT '',
    recorded_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK(end_date >= start_date)
);
CREATE TABLE IF NOT EXISTS hr_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL,
    title TEXT NOT NULL,
    storage_reference TEXT NOT NULL DEFAULT '',
    expires_on TEXT,
    created_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS hr_work_time (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    work_date TEXT NOT NULL,
    minutes_worked INTEGER NOT NULL CHECK(minutes_worked BETWEEN 0 AND 1440),
    notes TEXT NOT NULL DEFAULT '',
    recorded_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, work_date)
);
CREATE INDEX IF NOT EXISTS idx_hr_absences_dates ON hr_absences(start_date, end_date, status);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'paid' CHECK(status IN ('paid','planned')),
    total_cents INTEGER NOT NULL CHECK(total_cents > 0),
    department_id INTEGER REFERENCES hr_departments(id),
    org_unit_id INTEGER REFERENCES org_units(id),
    recorded_by INTEGER REFERENCES app_users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sales_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents > 0),
    line_total_cents INTEGER NOT NULL CHECK(line_total_cents > 0)
);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date, status);
CREATE INDEX IF NOT EXISTS idx_sales_items_product ON sales_items(product_id, sale_id);

CREATE TABLE IF NOT EXISTS org_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

