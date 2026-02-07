from threading import Thread, Lock

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from urllib.parse import urlparse, urldefrag

from crawler.frontier import lock
from shared import error_urls, error_lock, unique_urls
class Worker(Thread):

    robots_cache = {} #for checking already seen robots files info dict[str, dict]
    seen_robots = set() #for already downloaded files seen_robots = {"https://ics.uci.edu", "https://cs.uci.edu", "https://informatics.uci.edu",}
    robots_lock = Lock()
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
    
    def robots(self, resp):
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
                # Return empty sitemap on subsequent calls
                return (info["allowed"], info["blacklist"], info["whitelist"], set())

        if resp.status == 200 and resp.raw_response:
            blacklisted = set()
            whitelisted = set()
            Site_map_links = set()
            start_blacklist = False
            start_whitelist = False
            Precedence = False
            try:
                text = resp.raw_response.content.decode("utf-8", errors="ignore")
                for line in text.splitlines():
                    if line.startswith("Sitemap: "):
                        link = line[9:]
                        Site_map_links.add(link)
                        continue
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
                    if line.startswith("Disallow: ") and start_blacklist:
                        path = line[10:]
                        blacklisted.add(path)
                        continue
                    if line.startswith("Allow: ") and start_whitelist:
                        path = line[7:]
                        whitelisted.add(path)
                        continue
                    if not line:
                        start_blacklist = False
                        start_whitelist = False
                if "/" in blacklisted:
                    result = False, blacklisted, whitelisted, Site_map_links
                else:
                    result = True, blacklisted, whitelisted, Site_map_links
            except:
                result = True, blacklisted, whitelisted, Site_map_links
        else:
            result = True, set(), set(), set()

        # store in cache
        with Worker.robots_lock:
            Worker.robots_cache[domain] = {
                "allowed": result[0],
                "blacklist": result[1],
                "whitelist": result[2],
                "sitemap_links": result[3],}
        return result


    def get_robots_info(self, domain):
        with Worker.robots_lock:
            need_download = domain not in Worker.seen_robots

        if need_download:
            robots_url = f"{domain}/robots.txt"
            resp = download(robots_url, self.config, self.logger)

            self.robots(resp)

            with Worker.robots_lock:
                Worker.seen_robots.add(domain)

        with Worker.robots_lock:
            return Worker.robots_cache[domain]

    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            tbd_url, _ = urldefrag(tbd_url)
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            # Skip forbidden URLs
            with error_lock:
                if tbd_url in error_urls or tbd_url in unique_urls:
                    self.logger.info(f"Skipping forbidden URL {tbd_url}")
                    with lock:
                        self.frontier.mark_url_complete(tbd_url)
                    continue
            #check robots
            parsed = urlparse(tbd_url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            
            # Only download robots.txt once per domain/subdomain
            robots_info = self.get_robots_info(domain)
            Allowed = robots_info["allowed"]
            Blacklisted = robots_info["blacklist"]
            Whitelisted = robots_info["whitelist"]
            Site_map = robots_info["sitemap_links"]

            if Allowed:
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                if resp.status != 200:
                    with error_lock:
                        error_urls.add(tbd_url)
                    with lock:
                        self.frontier.mark_url_complete(tbd_url)
                    continue  # skip scraper, go to next URL
               
                scraped_urls = scraper.scraper(tbd_url, resp, Blacklisted, Whitelisted, Site_map)
                with lock:
                    for scraped_url in scraped_urls:
                        self.frontier.add_url(scraped_url)

            with lock:
                self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
