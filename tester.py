#tester to be implemented to test certain sections
import unittest
from scraper import is_valid
from configparser import ConfigParser
from utils.config import Config
from utils.server_registration import get_cache_server
from utils import get_logger
from utils.download import download
import scraper

class TestisValid(unittest.TestCase):
    #According to Nam
    """
    You need to crawl *.ics.uci.edu/* . The asterisk (*) is a quantifier that applies to
    the preceding regular expression element. It specifies that the preceding element may 
    occur zero or more times. 
    Essentially anything of the kind www.ics or just ics is valid
    """
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

class TestDownloadUrl(unittest.TestCase):
    def setUp(self):
        cparser = ConfigParser()
        cparser.read("config.ini")
        self.config = Config(cparser)
        self.config.cache_server = get_cache_server(self.config, True)
        #self.config.cache_server = ("localhost", 8080) #fake cache server for testing purposes, doesnt work
        self.logger = get_logger(f"Tester-{0}", "Tester")
    def test_what_does_resp_look_like(self):
        # tbd_url = "https://www.ics.uci.edu/"
        # resp = download(tbd_url, self.config, self.logger)
        # print(resp)
        #scraped_urls = scraper.scraper(tbd_url, resp)
        pass
        #we somehow need to access their cache server to test this, its done in launch.py

if __name__ == "__main__":
    unittest.main()