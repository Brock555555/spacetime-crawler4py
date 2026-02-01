from urllib.parse import urlparse
from utils.download import download
from utils import get_logger
from utils.config import Config
from utils.server_registration import get_cache_server
from configparser import ConfigParser

class TemuWorker:#creating a temporary worker
    def __init__(self, config, worker_id="robots"):
        self.config = config
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")

def robots(url, config_file="config.ini"):
    #needs to use cache server so we are not directly accessing the website
    #returns exists, blacklisted, whitelisted, site_map_links
    #exists is a boolean to check if the robots file existed
    #blacklisted is set of paths where are not allowed to go in
    #whitelisted is a set of paths we are only allowed in
    #site_map_links is a set of links from robots
    #loads the config, same as launch.py
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)

    #access the cache server and dont restart the crawler
    config.cache_server = get_cache_server(config, restart=False)

    #create a temporary worker just for reading robot files
    worker = TemuWorker(config)

    # Build robots.txt URL
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    # Fetch using download()
    resp = download(robots_url, worker.config, worker.logger)
    
    if resp.status == 200 and resp.raw_response:
        blacklisted = set()
        whitelisted = set()
        Site_map_links = set()
        start_blacklist = False
        start_whitelist = False
        Precedence = False
        try:
            text = resp.raw_response.content.decode("utf-8", errors="ignore") #turns the entire file into a string
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
                return False, blacklisted, whitelisted, Site_map_links #not allowed to crawl
            else:
                return True, blacklisted, whitelisted, Site_map_links #we are allowed to crawl
        except:
            return False, blacklisted, whitelisted, Site_map_links
    return False, blacklisted, whitelisted, Site_map_links
    #return sitemap list of links and parse file if were allowed to or not