# Create a way collect data from each worker/scraper instance

from queue import Queue

#--------------Report stuff-----------------------
# 1. Unique Pages
# 2. Longest page
# 3. Most common words
# 4. Subdomain count

class Report(object):
    # class variable
    report_queue = Queue()

    def __init__(self, worker_id):
        self.worker_id = worker_id

