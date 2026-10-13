from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest

TEMP_DIR = tempfile.TemporaryDirectory(prefix='product-manager-tests-')
os.environ['PRODUCT_MANAGER_DB'] = os.path.join(TEMP_DIR.name, 'test.db')

from api import app  # noqa: E402


class ProductManagerApiTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        TEMP_DIR.cleanup()

    def setUp(self):
        with app.get_db() as conn:
            # This fixture resets a disposable test database between cases. The
            # production ledger remains append-only; only test setup drops guards.
            conn.execute('DROP TRIGGER IF EXISTS stock_movements_no_update')
            conn.execute('DROP TRIGGER IF EXISTS stock_movements_no_delete')
            conn.execute('DELETE FROM stock_movements')
            conn.execute('''CREATE TRIGGER stock_movements_no_update
                            BEFORE UPDATE ON stock_movements
                            BEGIN SELECT RAISE(ABORT, 'stock movements are immutable'); END''')
            conn.execute('''CREATE TRIGGER stock_movements_no_delete
                            BEFORE DELETE ON stock_movements
                            BEGIN SELECT RAISE(ABORT, 'stock movements are immutable'); END''')
            conn.execute('DELETE FROM products')
            conn.execute('DELETE FROM clients')
            conn.execute(
                "INSERT OR IGNORE INTO app_users (username, password_hash, role) VALUES (?, ?, ?)",
                ('api-test-admin', 'unused-test-hash', 'admin'),
            )
            self.user = dict(conn.execute(
                'SELECT id, username, role FROM app_users WHERE username=?',
                ('api-test-admin',),
            ).fetchone())

    def handler(self, path='/', authenticated=True):
        handler = app.AppHandler.__new__(app.AppHandler)
        handler.path = path
        handler.result = None
        handler.send_json = lambda payload, status=200: setattr(handler, 'result', (status, payload))
        handler.headers = {}
        handler.client_address = ('127.0.0.1', 0)
        if authenticated:
            handler.current_user = self.user
            handler.require_authenticated_request = lambda request_path: self.user
            handler.require_permission = lambda user, permission: True
        return handler

    def request_json(self, path, payload=None):
        handler = self.handler(path)
        if path == '/api/health' or path == '/api/dashboard':
            handler.do_GET()
        elif path == '/api/products':
            handler.create_product(payload)
        else:
            raise AssertionError(f'Unexpected test route: {path}')
        return handler.result

    def product_payload(self, **overrides):
        payload = {
            'name': 'Notebook Pro', 'category': 'Computadores', 'sku': 'NB-PRO-1',
            'reference': 'REF-1', 'brand': 'Acme', 'status': 'available',
            'price': 4200, 'quantity': 4, 'supplier': 'Fornecedor Exemplo', 'notes': '',
        }
        return payload | overrides

    def test_health_reports_service_and_database(self):
        status, body = self.request_json('/api/health')
        self.assertEqual(status, 200)
        self.assertEqual(body, {'status': 'ok', 'database': 'connected'})

    def test_liveness_probe_is_public_and_minimal(self):
        handler = self.handler('/healthz', authenticated=False)
        handler.do_GET()
        self.assertEqual(handler.result, (200, {'status': 'ok'}))

    def test_readiness_probe_checks_database_without_authentication(self):
        handler = self.handler('/readyz', authenticated=False)
        handler.do_GET()
        self.assertEqual(handler.result, (200, {'status': 'ready'}))

    def test_readiness_probe_returns_unavailable_without_database_details(self):
        original_get_db = app.get_db
        def unavailable_database():
            raise sqlite3.OperationalError('private database path')
        app.get_db = unavailable_database
        try:
            handler = self.handler('/readyz', authenticated=False)
            handler.do_GET()
            self.assertEqual(handler.result, (503, {'status': 'unavailable'}))
            self.assertNotIn('private database path', str(handler.result))
        finally:
            app.get_db = original_get_db

    def test_health_requires_authentication(self):
        handler = self.handler('/api/health', authenticated=False)
        handler.do_GET()
        self.assertEqual(handler.result[0], 401)
        self.assertIn('Autenticação necessária', handler.result[1]['error'])

    def test_pwa_resources_are_served_with_installable_content_types(self):
        for path, content_type in (
            ('/manifest.webmanifest', 'application/manifest+json; charset=utf-8'),
            ('/service-worker.js', 'application/javascript; charset=utf-8'),
        ):
            handler = self.handler(path)
            handler.served = None
            handler.serve_file = lambda file_path, mime: setattr(handler, 'served', (file_path, mime))
            handler.do_GET()
            self.assertEqual(handler.served[1], content_type)
            self.assertTrue(handler.served[0].is_file())

    def test_product_can_be_created_and_listed(self):
        status, created = self.request_json('/api/products', self.product_payload())
        self.assertEqual(status, 201)
        self.assertGreater(created['id'], 0)
        with app.get_db() as conn:
            product = conn.execute('SELECT sku FROM products').fetchone()
        self.assertEqual(product['sku'], 'NB-PRO-1')

    def test_duplicate_sku_returns_conflict(self):
        self.assertEqual(self.request_json('/api/products', self.product_payload())[0], 201)
        status, _ = self.request_json('/api/products', self.product_payload(name='Outro produto'))
        self.assertEqual(status, 409)

    def test_negative_quantity_is_rejected(self):
        status, body = self.request_json('/api/products', self.product_payload(quantity=-1))
        self.assertEqual(status, 400)
        self.assertIn('negativa', body['error'])

    def test_dashboard_reflects_created_product(self):
        self.request_json('/api/products', self.product_payload())
        status, dashboard = self.request_json('/api/dashboard')
        self.assertEqual(status, 200)
        self.assertEqual(dashboard['products'], 1)
        self.assertEqual(dashboard['totalStock'], 4)




if __name__ == '__main__':
    unittest.main()
