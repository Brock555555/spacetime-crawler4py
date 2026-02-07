#tester to be implemented to test certain sections
import unittest
from scraper import is_valid
from configparser import ConfigParser
from utils.config import Config
from utils.server_registration import get_cache_server
from utils import get_logger
from utils.download import download
import scraper
from bs4 import BeautifulSoup
from report import Report

"""
class TestisValid(unittest.TestCase):
    #According to Nam
    You need to crawl *.ics.uci.edu/* . The asterisk (*) is a quantifier that applies to
    the preceding regular expression element. It specifies that the preceding element may 
    occur zero or more times. 
    Essentially anything of the kind www.ics or just ics is valid
    def test_valid_url(self):
        url = "https://www.ics.uci.edu/"
        self.assertTrue(is_valid(url))

        url = "https://ics.uci.edu/"
        self.assertTrue(is_valid(url))

        url = "https://ics.uci.edu/events/list/?tribe__ecp_custom_49%5B0%5D=Alumni"
        self.assertTrue(is_valid(url))

        url = "https://cs.ics.uci.edu/research-areas/"
        self.assertTrue(is_valid(url))

        url = "https://www.informatics.uci.edu/"
        self.assertTrue(is_valid(url))

        url = "https://www.informatics.uci.edu/undergrad/policies/"
        self.assertTrue(is_valid(url))

        url = "https://stat.ics.uci.edu/"
        self.assertTrue(is_valid(url))

        url = "https://stat.ics.uci.edu/what-is-statistics/"
        self.assertTrue(is_valid(url))

        url = "https://vision.ics.uci.edu/"
        self.assertTrue(is_valid(url))

    def test_Invalid_url(self):
        url = "https://www.reg.uci.edu/perl/EnrollHist.pl"
        self.assertFalse(is_valid(url))

        url = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"
        self.assertFalse(is_valid(url))

        url = "https://w3schools.tech/tutorial/html/html_basic_tags"
        self.assertFalse(is_valid(url))

        url = 'https://vim.rtorr.com/'
        self.assertFalse(is_valid(url))

        url = 'https://www.ics.uci.edu.com.virus/'
        self.assertFalse(is_valid(url))

        url = 'mailto:abc@test.com'
        self.assertFalse(is_valid(url))

        url = "https://www.www.vision.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "https://123.vision.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "https://123.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "https://123.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "https://x7p9q2z8.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "https://one.two.three.four.five.six.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "http://mail.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "https://admin.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "http://dev.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "https://staging.ics.uci.edu/"
        self.assertFalse(is_valid(url))

        url = "https://cs.ics.uci.edu.evil/"
        self.assertFalse(is_valid(url))

        url = "https://192-168-1-2.ics.uci.edu"
        self.assertFalse(is_valid(url))

        url = "https://host07.ics.uci.edu"
        self.assertFalse(is_valid(url))

        url = "https://test.test.test.ics.uci.edu"
        self.assertFalse(is_valid(url))

        url = "https://test.test.ics.uci.edu"
        self.assertFalse(is_valid(url))
"""

class TestHtmlParsing(unittest.TestCase):
    '''
    def test_get_link_locations(self):
        with open("example.txt", "r", encoding = "utf-8") as test_file:
            text = test_file.read()
        indices = scraper.get_link_locations(text)
        for index in indices:
            self.assertTrue(isinstance(index, int))
            self.assertEqual(text[index-5], "h")
    def test_get_links(self):
        with open("example.txt", "r", encoding = "utf-8") as test_file:
            text = test_file.read()
        links = scraper.get_links_from(text)
        self.assertEqual(len(links), 59)
        for link in links:
            self.assertTrue(isinstance(link, str))
            self.assertTrue("http" in link)
            print(link)
    '''



'''class TestDownloadUrl(unittest.TestCase):
    def setUp(self):
        # same config startup as in launch.py
        cparser = ConfigParser()
        cparser.read("config.ini")
        self.config = Config(cparser)
        self.config.cache_server = get_cache_server(self.config, False)
        #self.config.cache_server = ("localhost", 8080) #fake cache server for testing purposes, doesnt work
        self.logger = get_logger(f"Tester-{0}", "Tester")
    def test_what_does_resp_look_like(self):
        tbd_url = "https://www.ics.uci.edu/"
        resp = download(tbd_url, self.config, self.logger)
        print(resp)
        #scraped_urls = scraper.scraper(tbd_url, resp)
        pass
        #we somehow need to access their cache server to test this, its done in launch.py'''

class Test_report(unittest.TestCase):
    def test_report(self):
        html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
        <h1>Hello World!</h1>
        <p>This is a test page with some content. Testing, testing, 123.</p>
        <a href="https://ics.uci.edu/page1">Link1</a>
        <a href="https://ics.uci.edu/page2">Link2</a>
        <script>var x = 1;</script>
        <style>p {color:red;}</style>
        </body>
        </html>
        """

        soup = BeautifulSoup(html, "html.parser")
        url = "https://ics.uci.edu/test-page"

        report = Report(url, soup)
        report.run()
        Report.aggregate_reports()
        print("Unique pages:", Report.unique_pages)
        print("Longest page URL:", Report.longest_page)
        print("Longest page length:", Report.longest_length)
        print("Top 50 words:", Report.top_50_words)
        print("Word frequencies:", Report.combined_word_frequencies)
        report.write_results("test_report.txt")

if __name__ == "__main__":
    unittest.main()