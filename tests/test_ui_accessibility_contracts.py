from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


INDEX_PATH = Path(__file__).resolve().parents[1] / "ui" / "index.html"


class AccessibilityContractParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.html_language = None
        self.viewport_found = False
        self.ids = set()
        self.skip_link_targets = []
        self.live_regions = []
        self.main_landmarks = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "html":
            self.html_language = attributes.get("lang")
        if tag == "meta" and attributes.get("name", "").lower() == "viewport":
            self.viewport_found = bool(attributes.get("content"))
        element_id = attributes.get("id")
        if element_id:
            self.ids.add(element_id)
        if tag == "a" and "skip-link" in attributes.get("class", "").split():
            self.skip_link_targets.append(attributes.get("href", ""))
        if attributes.get("aria-live") in {"polite", "assertive"}:
            self.live_regions.append((tag, attributes.get("role"), attributes.get("aria-live")))
        if tag == "main":
            self.main_landmarks.append(attributes.get("id"))


class UiAccessibilityContractTests(unittest.TestCase):
    def test_main_document_declares_brazilian_portuguese(self):
        parser = AccessibilityContractParser()
        parser.feed(INDEX_PATH.read_text(encoding="utf-8"))
        self.assertEqual(parser.html_language, "pt-BR")

    def test_document_has_responsive_viewport_metadata(self):
        parser = AccessibilityContractParser()
        parser.feed(INDEX_PATH.read_text(encoding="utf-8"))
        self.assertTrue(parser.viewport_found)

    def test_skip_link_points_to_existing_main_landmark(self):
        parser = AccessibilityContractParser()
        parser.feed(INDEX_PATH.read_text(encoding="utf-8"))
        self.assertIn("#main-content", parser.skip_link_targets)
        self.assertIn("main-content", parser.ids)
        self.assertIn("main-content", parser.main_landmarks)

    def test_document_exposes_at_least_one_live_region(self):
        parser = AccessibilityContractParser()
        parser.feed(INDEX_PATH.read_text(encoding="utf-8"))
        self.assertTrue(parser.live_regions)


if __name__ == "__main__":
    unittest.main()
