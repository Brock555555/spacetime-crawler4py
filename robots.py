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
        try:
            return resp.raw_response.content.decode("utf-8", errors="ignore")
        except AttributeError:
            return str(resp.raw_response)
    return None
    #return sitemap list of links and parse file if were allowed to or not