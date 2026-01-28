from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler


def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)

"""
Your crawler's log file is under Logs/Worker.log. Make sure that you inspect that Log file in order to understand what happened during the test crawls.

Server Cache status codes
These are all the cache server error codes:

600: Request Malformed

601: Download Exception {error}

602: Spacetime Server Failure

603: Scheme has to be either http or https

604: Domain must be within spec

605: Not an appropriate file extension

606: Exception in parsing url

607: Content too big. {resp.headers['content-length']}

608: Denied by domain robot rules

You may ignore some of them, but not all.
"""