from threading import Lock

error_urls = set()      # shared global set of URLs that errored
error_lock = Lock()     # optional lock for thread safety
unique_urls = set()