from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from report import Report

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        try:
            self.start_async()
            self.join()
            Report.aggregate_reports()
            Report.write_results()
        except KeyboardInterrupt:
            print("Crawler interrupted. Aggregating reports...")

        finally:
            # Always aggregate whatever is in the report queue
            Report.aggregate_reports()
            Report.write_results("report_interrupted_run.txt")

    def join(self):
        for worker in self.workers:
            worker.join()
