# Create a way collect data from each worker/scraper instance

from queue import Queue
from bs4 import BeautifulSoup, Comment
import re

#--------------Report stuff-----------------------
# 1. Unique Pages
# 2. Longest page
# 3. Most common words
# 4. Subdomain count

class Report():
    WORD_COUNT = 50
    # class variable to handle multithreading
    report_queue = Queue()
    word_bank = defaultdict()

    def __init__(self, url: str, soup: BeautifulSoup):
        self.report = {}
        self.soup = soup

    def report_page_url(self, url: str):
        self.report["url"] = url
        # TODO: remove fragments from url

    def report_page_length(self, word_count: int):
        self.report["length"] = word_count

    def is_comment(self, element):
        return isinstance(element, Comment)

    def get_words(self, soup: BeautifulSoup):
        # THIS IS DESTRUCTIVE SO IT HAS TO BE RUN AFTER EVERYTHING ELSE
        # filter out tags and comments
        for tag in soup(["script", "style", "head", "title", "meta", "[document]"]):
            tag.decompose()
        for comment in soup.find_all(string = self.is_comment):
            comment.decompose()
        # finally gets text
        text = soup.get_text(separator=' ', strip=True)
        # tokenize by letters and apostrophes only
        words = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)*", text.lower())

    def run(self):
        self.words = self.get_words(self.soup)
        self.report_page_url(self.url)
        self.report_page_length(len(self.words))
        # TODO: self.report_word_frequencies(words)
        

        # Queue report
        Report.report_queue.put(self.report)

    @classmethod
    # Call this in main thread (launch.py)
    def aggregate_reports(cls):
        while not Report.report_queue.empty():
            report = Report.report_queue.get()
            # TODO: unpack report and process

