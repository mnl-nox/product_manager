from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PwaAssetTests(unittest.TestCase):
    def test_manifest_points_to_existing_install_icons(self):
        manifest = json.loads((ROOT / 'ui' / 'manifest.webmanifest').read_text(encoding='utf-8'))
        self.assertEqual(manifest['display'], 'standalone')
        self.assertEqual(manifest['start_url'], '/dashboard')
        for icon in manifest['icons']:
            icon_path = ROOT / icon['src'].lstrip('/')
            self.assertTrue(icon_path.is_file(), icon_path)

    def test_service_worker_keeps_api_responses_out_of_cache(self):
        worker = (ROOT / 'ui' / 'service-worker.js').read_text(encoding='utf-8')
        self.assertIn("url.pathname.startsWith('/api/')", worker)
        self.assertIn("request.mode === 'navigate'", worker)


if __name__ == '__main__':
    unittest.main()
