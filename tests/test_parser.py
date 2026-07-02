import unittest
from bs4 import BeautifulSoup
from omnicrawl.parser import extract_internal_links, parse_page_data
from omnicrawl.constants import MODE_CLASSIC, MODE_UI_COMPONENTS

class TestParser(unittest.TestCase):
    def setUp(self):
        self.domain = "example.com"
        self.actual_url = "https://example.com/page"
        
    def test_extract_internal_links_same_domain(self):
        html = '''
        <html><body>
            <a href="/internal">Internal</a>
            <a href="https://example.com/other">Other</a>
            <a href="https://external.com/out">External</a>
        </body></html>
        '''
        soup = BeautifulSoup(html, "html.parser")
        
        # Test staying in domain
        links = extract_internal_links(soup, self.actual_url, self.domain, stay_in_domain=True)
        self.assertEqual(len(links), 2)
        self.assertIn("https://example.com/internal", links)
        self.assertIn("https://example.com/other", links)
        self.assertNotIn("https://external.com/out", links)
        
        # Test cross-domain
        links_cross = extract_internal_links(soup, self.actual_url, self.domain, stay_in_domain=False)
        self.assertEqual(len(links_cross), 3)
        self.assertIn("https://external.com/out", links_cross)

    def test_parse_page_data_ui_deduplication(self):
        html = '''
        <html><body>
            <div class="nav"><a href="/login">Login</a></div>
            <div class="footer"><a href="/login">Login</a></div>
            <div class="nav"><a href="/login">Login</a></div>
        </body></html>
        '''
        soup = BeautifulSoup(html, "html.parser")
        collected_data = {}
        
        parse_page_data(MODE_UI_COMPONENTS, soup, self.actual_url, collected_data)
        
        # Should collect exactly 2 distinct components based on HTML hash
        self.assertEqual(len(collected_data), 2)
        
    def test_parse_page_data_classic_mode(self):
        html = '''
        <html><body>
            <a href="/login">Login</a>
            <a href="/login">Login Duplicate</a>
        </body></html>
        '''
        soup = BeautifulSoup(html, "html.parser")
        collected_data = {}
        
        parse_page_data(MODE_CLASSIC, soup, self.actual_url, collected_data)
        
        # Should collect exactly 1 item based on href
        self.assertEqual(len(collected_data), 1)

if __name__ == "__main__":
    unittest.main()
