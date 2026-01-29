import re
from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    url = resp.url
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    if resp.status != 200:
        #check error
        error = resp.error
        """
        details regarding error codes can be found at https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
        Detailing individual codes got too lengthy so I moved them to a text file called 'QuickErrorLookup.txt'
        """

    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    #testing git setup
    return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        #domain parsing here, 
        #from urlparse documentation scheme://netloc/path;parameters?query#fragment.
        #from slides scheme://domain:port/path?query_string#fragment_id
        allowed_domains = {"ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"} #waiting to hear back on ed
        domain = parsed.hostname #returns the entire domain, does not include the /before path, this does however include www.
        #domain should already be lowercase
        if not domain:
            return False #if domain is None
        if not any(domain == d or domain.endswith("." + d) for d in allowed_domains):
            return False #its crude but gets it in around O(1) - O(n) for larger string domains
        #implemented this way also prevents traps in the suffix of the domain like ics.uci.edu.com.virus
        #now for the prefix check, we have a valid domain suffix but the subdomain needs to be checked
        return not re.match(
            r"^(www\.){2,}" #block www.www.
            + r"|^[a-z0-9]{8,}\."# random nonsense strings
            + r"|^([a-z0-9-]+\.){5,}"# too many subdomains
            + r"|^(mail|admin|ftp|test|dev|staging|beta|preview|sandbox|demo|qa|srv|node|host|lb)\." #junk, can be added to
            + r"|^(srv|node|host|lb)\d+\." #junk followed by a number, more for servers and hosting platforms
            + r"|^([a-z0-9-]+)\.\1\." # repeated subdomains
            + r"|^v\d+(\.|-)" #version number subdomain
            + r"|^(\d+-){3}\d+\." #IP address subdomains
            + r"|^\d+\.", domain #all numbers
        )
        #this is the file type checker, was in the project from the start - might need to be added to
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
