# Create a way collect data from each worker/scraper instance

from queue import Queue
from collections import defaultdict

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

    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.report = {}

    def get_url(self, url: str):
        self.report["url"] = url

    def get_page_length(self, url: str, word_count: int):
        self.report["length"] = (url, word_count)

    def get_most_common_words(self, text):
        common_words = defaultdict()
        # tokenize???
        # 50 most common words per page
        for i in range(Report.WORD_COUNT):
            if common_words:
                most_common = max(my_dict, key=my_dict.get)
                k, v = commonwords.pop(most_common)
            else:
                break
        self.report["words"] = common_words

    def send_report(self):
        self.report{"worker_id"] = worker_id
        Report.report_queue.put(self.report)

    @classmethod
    def aggregate_reports(cls):
        while not Report.report_queue.empty():
            report = Report.report_queue.get()
            # unpack report and process

