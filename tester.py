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

if __name__ == "__main__":
    unittest.main()