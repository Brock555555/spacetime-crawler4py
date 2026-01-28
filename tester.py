#tester to be implemented to test certain sections
import unittest
from scraper import is_valid

class TestisValid(unittest.TestCase):

    def test_valid_url(self): #waiting to hear back on ed
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

        url = "192-168-1-2.ics.uci.edu"
        self.assertFalse(is_valid(url))

        url = "host07.ics.uci.edu"
        self.assertFalse(is_valid(url))

if __name__ == "__main__":
    unittest.main()