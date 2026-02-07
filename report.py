# Create a way collect data from each worker/scraper instance

from queue import Queue
from bs4 import BeautifulSoup, Comment
from collections import defaultdict
import re
from urllib import parse

#--------------Report stuff-----------------------
# 1. Unique pages counted after fragment removal done
# 2. Longest page? done
# 3. Top 50 words sorted by frequency (most common words) WIP
# 4. Subdomains sorted alphabetically done
# 5. Subdomain counts are unique pages per subdomain, not raw visits (subdomain count) done
# 6. Stopwords explicitly mentioned in report WIP

class Report:
    # class Queue to handle multithreading
    report_queue = Queue()
    unique_pages = set()
    subdomain_page_count = defaultdict(int)
    sorted_subdomains = dict()
    max_length = -1
    max_page = str()
    combined_word_frequencies = defaultdict(int)
    top_50_words = list(())

    def __init__(self, url: str, soup: BeautifulSoup):
        self.report = dict()
        self.url = url
        self.soup = soup
        self.words = list()

    def report_page_url(self, url: str):
        # urllib.parse.urldefrag should work
        self.report["url"] = parse.urldefrag(url)

    def report_page_length(self, words: list[str]):
        self.report["page length"] = len(words)

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
        return words

    def report_word_frequencies(self, words: list[str]):
        frequencies = defaultdict(int)
        for word in words:
            frequencies[word] += 1
        self.report["word frequencies"] = frequencies

    def run(self):
        self.report_page_url(self.url)
        self.words = self.get_words(self.soup)
        self.report_page_length(self.words)
        self.report_word_frequencies(self.words)
        # Queue report
        Report.report_queue.put(self.report)

    @classmethod
    # Call this in main thread (launch.py)
    def aggregate_reports(cls):
        while not Report.report_queue.empty():
            # get the report from the queue
            report = Report.report_queue.get()
            # Add url to set and then count the length of the set
            Report.unique_pages.add(report["url"])
            # Update url of longest page length
            if report["page length"] > Report.max_length:
                Report.max_length = report["page length"]
                Report.max_page = report["url"]
            # Add/update word frequencies
            for word, frequency in report["word frequencies"].items():
                Report.combined_word_frequencies[word] += frequency
        # get the 50 most common words
        Report.top_50_words = sorted(Report.combined_word_frequencies,
                             key = Report.combined_word_frequencies.get,
                             reverse = True)[:50]
        # count the pages in each subdomain
        for page in Report.unique_pages:
            Report.subdomain_page_count[parse.urlparse(page).hostname] += 1
        # sort them alphabetically into a new dict
        Report.sorted_subdomains = dict(sorted(Report.subdomain_page_count.items()))

    @classmethod
    def write_results(cls, file_name = "report.txt"):
        with open(file_name, 'w') as out_file:
            out_file.write(f"Number of pages found: {len(Report.unique_pages)}")

