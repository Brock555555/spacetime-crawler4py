import re
from urllib.parse import urlparse, urldefrag, urljoin, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
from hashlib import md5

from PartA import computeWordFrequencies
from report import Report
from shared import error_urls, error_lock, unique_urls

#------------------LIST OF THINGS LEFT TO DO-------------------------------- In order of importance
# Finish Report so we can turn in our data
# . Finalize large-file avoidance:
#    - either add Content-Length heuristic
#    - or document why extension + content filters suffice
# 5. Handle Ctrl+C KeyboardException

#----------------Extra Credit stuff, to be done if we have time-----------------
# 1. Implement exact and near webpage similarity detection
# 2. Make the crawler multithreaded.

#these two here are NOT thread safe
unique_urls = set() # can still include for now? this currently prevents us from running duplicate urls
error_urls = set() # will never add a url of this set again # TODO: Move this into worker (to make it persistent) and make sure worker doesn't use the error URLS as well (those that returned error status)
allowed_domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]

def scraper(url, resp, blacklist, whitelist, site_map):
    #print(blacklist, whitelist, site_map)
    links = extract_next_links(url, resp, site_map)
    return [link for link in links if is_valid(link, blacklist, whitelist)]

def extract_next_links(url, resp, site_map):
    # site_map, a set of more links from robots
    XML = False

    #only process successful 200 OK responses
    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:#further error checking
        with error_lock:
            error_urls.add(url)
        return []

    unique = urldefrag(url)[0]

    with error_lock:   # reuse existing lock
        if unique in unique_urls:
            return []  # already processed
        unique_urls.add(unique)

    links = []
    try:
        if site_map:
            #just add the site_map links, it will get parsed when the frontier reaches it later
            for site_map_url in site_map:
                clean = urldefrag(site_map_url)[0]
                links.append(clean)
        
        #parse raw bytes of page content into soup obj
        if resp.url.endswith(".xml") or "application/xml" in resp.raw_response.headers.get("Content-Type", ""):
            soup = BeautifulSoup(resp.raw_response.content, "xml")
            XML = True
        else:
            soup = BeautifulSoup(resp.raw_response.content, "html.parser")

        #remove script and style elements from word count
        for ss in soup(["script", "style"]):
            ss.decompose()

        text = soup.get_text(separator=' ') #get all text on page, remove HTML tags
        words = re.findall(r'[a-zA-Z0-9]{2,}', text.lower()) #finds sequence of 1/+ alpha character
        #convert everything to lowercase so upper and lower same words count as 1
        #[a-zA-Z0-9]+: ignores symbols

        if len(words) < 50 and len(soup.find_all('a')) > 20: #detect low info content (avoids traps)
            return links


        if XML:
            for loc in soup.find_all("loc"):
                links.append(loc.text)
        else:
            #look for all <a> tags with "href" to find out where to go next
            for a in soup.find_all("a", href=True):
                #if raw_href is index.html, urljoin joins it together with resp.url
                absolute_url = urljoin(url, a["href"])
                #separate same pages with urldefrag and keep base part
                base_url = urldefrag(absolute_url)[0]
                links.append(base_url)

        # Call report module.  Lmk if this is a suitable place to put this.
        report = Report(url, soup)
        report.run()

    except Exception as e:
        #log error if page is malformed and return empty list so cralwer doesn't crash
        print(f"Error parsing content for {url}: {e}")
        return []
    return links #return final list of discovered URLS to crawler


def normalize_url(url: str) -> str:
    """Remove ephemeral query parameters that don't change main page content."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    # Remove parameters that change frequently
    for key in ["version", "format", "action"]:
        qs.pop(key, None)

    new_query = urlencode(qs, doseq=True)
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    return urldefrag(normalized)[0]  # remove fragment

def is_valid(url, blacklist, whitelist):
    #blacklist: a set of paths the crawler is not allowed to go into
    #whitelist: a set of paths the crawler is allowed into from disallowed paths
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        with error_lock:
            if url in error_urls:
                return False #dont do any further checking

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        #domain parsing here, 
        #from urlparse documentation scheme://netloc/path;parameters?query#fragment.
        #from slides scheme://domain:port/path?query_string#fragment_id
        domain = parsed.hostname.lower() if parsed.hostname else "" #returns the entire domain, does not include the /before path, this does however include www.
        #domain should already be lowercase
        
        if not any(domain == d or domain.endswith("." + d) for d in allowed_domains):
            return False #its crude but gets it in around O(1) - O(n) for larger string domains

        #implemented this way also prevents traps in the suffix of the domain like ics.uci.edu.com.virus
        #now for the prefix check, we have a valid domain suffix but the subdomain needs to be checked
        if re.match(
            r"^(www\.){2,}" #block www.www.
            + r"|^[a-z0-9]{8,}\."# random nonsense strings
            + r"|^([a-z0-9-]+\.){5,}"# too many subdomains
            + r"|^(mail|admin|ftp|test|dev|staging|beta|preview|sandbox|demo|qa|srv|node|host|lb)\." #junk, can be added to
            + r"|^(srv|node|host|lb)\d+\." #junk followed by a number, more for servers and hosting platforms
            + r"|^([a-z0-9-]+)\.\1\." # repeated subdomains
            + r"|^v\d+(\.|-)" #version number subdomain
            + r"|^(\d+-){3}\d+\." #IP address subdomains
            + r"|^\d+\.", domain #all numbers
        ):
            return False
        
            
        path = parsed.path.lower()
        query = parsed.query.lower()

        #avoid malformed URL patterns seen in logs
        if '"' in path or "\\" in path:
            return False

        # Filter out timeline pages
        if "/timeline" in path:
            return False

        if path.startswith("/wiki/") and "version=" in query:
            return False

        #add ml or dataset check
        dataset_keywords = ("/data/", "/dataset/", "/downloads/")
        if any(keyword in path for keyword in dataset_keywords):
            return False

        #updated whitelist vs blacklist logic so that it will check specific paths
        for bl in blacklist:
            if path.startswith(bl):
                if not any(path.startswith(w1) for w1 in whitelist):
                    return False


        if path.count('/') > 10: #avoide infinite directory recursion
            return False

        if re.search(r"(/[^/]+)\1{2,}", path): #repeating directories trap
            return False 

        calendar_patterns = [
            "calendar", "events", "day=", "month=", "year=", 
            "outlook-ical", "action=download", "share="
        ] #calendar trap

        if any(p in path or p in query for p in calendar_patterns):
            #block specific date queries
            if re.search(r"\d{4}-\d{2}-\d{2}", path) or query != "":
                return False
        if len(url) > 200:
            return False #long urls usually traps

        if "/wiki/" in path:
            return False
        if "/cropped" in path:
            return False
        if "~epstein" in path:
            return False
        
        if domain.startswith("wiki."):
            return False

        if re.search(r"/page/\d+", path):
            page_num = int(re.search(r"/page/(\d+)", path).group(1))
            if page_num > 5:
                return False

        if (
            path.startswith("/events")
            or "/event/" in path
            or "/calendar/" in path
            or re.search(r"/day/\d{4}-\d{2}-\d{2}", path)
        ):
            return False
        
        if "doku.php" in path:
            return False
        
        if re.search(r"do=media|tab_|image=|ical=|outlook-ical=|tribe_", query):
            return False
            
        if "seminar-series" in path and re.search(r"\d{4}-\d{4}", path):
            return False

        if re.search(r"(/[^/]+)\1{2,}", path): #detects repeated path segments
            return False
    
            
        #this is the file type checker, was in the project from the start - might need to be added to
        #re added for xml
        return not re.match(
            r".*.(css|js|bmp|gif|jpe?g|ico|png|tiff?|svg|heic|webp|avif"
            r"|mid|mp2|mp3|mp4|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|flac|aac|webm"
            r"|pdf|ps|eps|tex|ppt|pptx|pptm|doc|docx|docm|xls|xlsx|xlsm|odt|ods|odp"
            r"|data|dat|exe|bz2|tar|tgz|xz|lzma|msi|bin|7z|7zip|psd|dmg|iso"
            r"|c|h|cpp|hpp|java|py|ipynb|sh|pl|rb|php|bat|ps1|Makefile|emacs"
            r"|epub|dll|cnf|cfg|conf|ini|thmx|mso|arff|rtf|jar|csv|log|md|txt|json|yaml|yml"
            r"|rm|smil|wmv|swf|wma|zip|rar|gz|torrent|pem|crt|key|htm|sql|shtml|png|jpg|img|html)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", url)
        return False

# # TODO: Is this the right place to put this function?
# def simhash(words1, words2):
#     hashes1 = []
#     hashes2 = []
#
#     # Count words
#     counts1 = computeWordFrequencies(words1)
#     counts2 = computeWordFrequencies(words2)
#
#     # Hash the words
#     for word in words1:
#         binary_hash = md5(word.encode()).digest()
#
#         # TODO: Insert XOR business here
#
#         hashes1.append(binary_hash)
#
#     # TODO: Repeat for words2
#     for word in words2:
#         md5(word.encode()).digest()