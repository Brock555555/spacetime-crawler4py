# Create a way collect data from each worker/scraper instance

from queue import Queue

#--------------Report stuff-----------------------
# 1. Unique Pages
# 2. Longest page
# 3. Most common words
# 4. Subdomain count

class Report(object):
    # class variable to handle multithreading
    report_queue = Queue()

    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.report = {}

    def get_unique_pages(self, unique_pages: list):
        self.report["unique"] = unique_pages

    def get_longest_page(self, longest_page: str, word_count: int):
        self.report["longest"] = (longest_page, word_count)

    def run(self):
        self.report{"worker_id"] = worker_id
        Report.report_queue.put(self.report)
        

