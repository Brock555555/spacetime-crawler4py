import os
import shelve

from threading import Thread, Lock
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize
from urllib.parse import urlparse
from scraper import is_valid, allowed_domains

frontier_lock = Lock()

class Frontier(object):
    def __init__(self, config, restart, thread_count):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list() # Primary queue -- Should be empty almost perpetually as new links get distributed immediately
        self.thread_count = thread_count

        # Buckets for subdomains
        self.buckets = list() # Distributed queue
        for i in range(self.thread_count):
            self.buckets.append(list())

        # Check for save file and restart option
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)

        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
            self.distribute_urls()
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)
                self.distribute_urls()

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self, worker_id):
        try:
            # return self.to_be_downloaded.pop()
            return self.buckets[worker_id].pop()
        except IndexError:
            return None

    def distribute_urls(self):
        """
        Should be called each time a worker adds a set of urls to the frontier
        """

        print(f"TO BE DOWNLOADED: {self.to_be_downloaded}")

        while self.to_be_downloaded:
            current_url = self.to_be_downloaded.pop()
            bucket = None

            # Parse domain
            domain = urlparse(current_url)
            domain = domain.hostname.lower() if domain.hostname else ""
            print(f"DISTRIBUTION: URL - {current_url}, Domain - {domain}")

            if not domain:
                print("DISTRIBUTION ERROR: NO DOMAIN FROM PARSE")
            else:
                # cond = (domain == d or domain.endswith("." + d) for d in allowed_domains)

                for i, allowed_domain in enumerate(allowed_domains):
                    if domain == allowed_domain or domain.endswith("." + allowed_domain):
                        bucket = self.buckets[i % self.thread_count]
                        break

                if bucket is None:
                    print("DISTRIBUTION ERROR: NO BUCKET FITTED")
                else:
                    bucket.append(current_url)

        print(self.buckets)
        for i, bucket in enumerate(self.buckets):
            print(f"Bucket {i}: {bucket}")

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            self.save[urlhash] = (url, False)
            self.save.sync()
            self.to_be_downloaded.append(url)
    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.save[urlhash] = (url, True)
        self.save.sync()
