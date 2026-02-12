from threading import Thread, Lock

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from urllib.parse import urlparse, urldefrag

from crawler.frontier import frontier_lock
from shared import error_urls, error_lock, unique_urls

class Worker(Thread):
    robots_cache = {} #for checking already seen robots files info dict[str, dict]
    seen_robots = set() #for already downloaded files seen_robots = {"https://ics.uci.edu", "https://cs.uci.edu", "https://informatics.uci.edu",}
    robots_lock = Lock()
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.worker_id = worker_id
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
    
    def robots(self, resp):
        """
        Given a response from download that refers to the downloading of the robots.txt
        from the current url, parse and build the cache to store robots.txt information
        and return it for scraper to add links or forbid links from it.
        """
        self.logger.info(
            f"Downloaded {resp.url}, status <{resp.status}>, "
            f"using cache {self.config.cache_server}."
        )

        # extract domain for caching
        parsed = urlparse(resp.url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

       # return cached robots info if already seen
        with Worker.robots_lock:
            if domain in Worker.robots_cache:
                info = Worker.robots_cache[domain]
                # Return empty sitemap on subsequent calls to prevent adding infinite links
                return (info["allowed"], info["blacklist"], info["whitelist"], set())

        if resp.status == 200 and resp.raw_response: #url was successfully downloaded
            #establish robots.txt sets
            blacklisted = set()
            whitelisted = set()
            Site_map_links = set()
            #flags to denote when to start and stop reading certain lines
            start_blacklist = False
            start_whitelist = False
            Precedence = False #precedence rule if our specifially named bot shows up in the rules
            try:
                text = resp.raw_response.content.decode("utf-8", errors="ignore") #the entire page has already been downloaded to memory so just decode it into a string/file
                for line in text.splitlines():#one line at a time
                    #add sitemap links provided in robots and filter out sitemaps that only contain image types
                    if line.startswith("Sitemap: "):
                        link = line[9:].strip().lower()
                        if any(x in link for x in ["image", "img", "media", "video", "photo"]):
                            continue
                        Site_map_links.add(link)
                        continue
                    #Find either our named bot or the all bots rule to build the blacklist and whitelist
                    if line.startswith("User-agent: "):
                        start_list = False
                        agent = line[12:]
                        if agent == "IR UW26 32604390, 35929312, 91364596, 65007616":
                            start_blacklist = True
                            start_whitelist = True
                            Precedence = True
                            continue
                        if agent == "*" and not Precedence:
                            start_blacklist = True
                            start_whitelist = True
                            continue
                    #only adds to the set if we have already seen a user-agent
                    if line.startswith("Disallow: ") and start_blacklist:
                        path = line[10:]
                        blacklisted.add(path)
                        continue
                    if line.startswith("Allow: ") and start_whitelist:
                        path = line[7:]
                        whitelisted.add(path)
                        continue
                    #restarts the rule checking if an empty line is detected
                    if not line:
                        start_blacklist = False
                        start_whitelist = False
                if "/" in blacklisted: #essentially if we are disallowed from all directories we shouldnt be going into this link
                    result = False, blacklisted, whitelisted, Site_map_links
                else:
                    result = True, blacklisted, whitelisted, Site_map_links #we are allowed to go into this link
            except:
                result = True, blacklisted, whitelisted, Site_map_links #allowed to go into link but robots doesnt exist
        else:
            result = True, set(), set(), set() #allowed to go into link but robots doesnt exist

        # store in cache, stores based on new subdomains - which could have a different robots
        with Worker.robots_lock:
            Worker.robots_cache[domain] = {
                "allowed": result[0],
                "blacklist": result[1],
                "whitelist": result[2],
                "sitemap_links": result[3],}
        return result

    def get_robots_info(self, domain):
        downloaded_file = False

        with Worker.robots_lock:
            need_download = domain not in Worker.seen_robots #checks to see if the domain has been seen before

        if need_download:
            robots_url = f"{domain}/robots.txt"
            resp = download(robots_url, self.config, self.logger) #downloads robots.txt for parsing
            downloaded_file = True

            self.robots(resp) #calld robots to parse robots.txt

            with Worker.robots_lock:
                Worker.seen_robots.add(domain) #weve seen this robots before, dont parse next time

        with Worker.robots_lock:
            return Worker.robots_cache[domain], downloaded_file #return the robots info and a flag for detection

    def run(self):
        while True:
            # Check for a new URL to process
            with frontier_lock:
                tbd_url = self.frontier.get_tbd_url(self.worker_id)

                # Do this while holding the lock
                if tbd_url is not None:
                    tbd_url, _ = urldefrag(tbd_url)
                    self.frontier.active_workers += 1
                else:
                    # Check if finished crawling
                    if self.frontier.active_workers == 0 and self.frontier.is_empty():
                        self.logger.info("Frontier is empty. Stopping Crawler.")
                        self.frontier.condition.notify_all()
                        break

                    # If not finished crawling, wait for condition to change
                    self.frontier.condition.wait()

            # Skip forbidden URLs
            with error_lock:
                if tbd_url in error_urls or tbd_url in unique_urls: #disallow urls weve seen before that have been already crawled or error
                    self.logger.info(f"Skipping forbidden URL {tbd_url}")
                    with frontier_lock:
                        self.frontier.mark_url_complete(tbd_url)
                        self.frontier.active_workers -= 1
                        self.frontier.condition.notify_all()
                    continue

            # If there is a URL to process
            if tbd_url is not None:
                #check robots
                parsed = urlparse(tbd_url)
                domain = f"{parsed.scheme}://{parsed.netloc}"

                # Only download robots.txt once per domain/subdomain
                robots_info, robots_sleep = self.get_robots_info(domain)

                if robots_sleep:
                    time.sleep(self.config.time_delay)  # Sleep after downloading robots info

                Allowed = robots_info["allowed"]
                Blacklisted = robots_info["blacklist"]
                Whitelisted = robots_info["whitelist"]
                Site_map = robots_info["sitemap_links"]

                if Allowed: #if allowed to crawl lets download this link
                    resp = download(tbd_url, self.config, self.logger)
                    self.logger.info(
                        f"Downloaded {tbd_url}, status <{resp.status}>, "
                        f"using cache {self.config.cache_server}.")

                    if resp.status != 200:
                        with error_lock:
                            error_urls.add(tbd_url)
                        with frontier_lock:
                            self.frontier.mark_url_complete(tbd_url)
                            self.frontier.active_workers -= 1
                            self.frontier.condition.notify_all()
                        continue  # skip scraper, go to next URL

                    scraped_urls = scraper.scraper(tbd_url, resp, Blacklisted, Whitelisted, Site_map) #call scraper with content parsed from robots
                    with frontier_lock:
                        for scraped_url in scraped_urls:
                            self.frontier.add_url(scraped_url)
                        self.frontier.condition.notify_all()
                        self.frontier.distribute_urls()

                with frontier_lock:
                    self.frontier.mark_url_complete(tbd_url)
                    self.frontier.active_workers -= 1
                    self.frontier.condition.notify_all()

                time.sleep(self.config.time_delay)