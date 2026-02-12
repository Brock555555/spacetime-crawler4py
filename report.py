
from queue import Queue
from bs4 import BeautifulSoup, Comment
from collections import defaultdict
import re
from urllib import parse

#--------------Report stuff-----------------------
# 1. Unique pages counted after fragment removal done
# 2. Longest page? done
# 3. Top 50 words sorted by frequency (most common words) done
# 4. Subdomains sorted alphabetically done
# 5. Subdomain counts are unique pages per subdomain, not raw visits (subdomain count) done
# 6. Stopwords explicitly mentioned in report done

class Report:
    # class Queue to handle multithreading
    report_queue = Queue() # Shared queue for multithreaded reporting of pages
    unique_pages = set() # Set to track URLs of unique pages (avoid duplicates)
    subdomain_page_count = defaultdict(int) # Count of pages per subdomain
    longest_length = -1 # Track the length of the longest page processed
    longest_page = str() # Track the URL of the longest page
    combined_word_frequencies = defaultdict(int) # Aggregate word frequencies across all pages
    top_50_words = list() # List to store the top 50 most frequent words

    def __init__(self, url: str, soup: BeautifulSoup):
        self.report = dict() # Dictionary to store individual page report data
        self.url = url
        self.soup = soup  # Parsed HTML of this page (BeautifulSoup object)
        self.words = list()

    def report_page_url(self, url: str):
        # urllib.parse.urldefrag should work
        url, frag = parse.urldefrag(url) # Remove the fragment part of the URL (anything after '#')
        url = url.lower().rstrip('/')
        self.report["url"] = url # Store the cleaned URL in this page's report dictionary

    def report_page_length(self, words: list[str]):
        # Store the number of words on the page in the report
        self.report["page length"] = len(words)

    def is_comment(self, element):
        # Check if a BeautifulSoup element is an HTML comment, An HTML comment is a section of HTML code that is ignored by the browser and does not appear on the rendered page.
        # Returns True if element is a Comment, False otherwise
        return isinstance(element, Comment)

    def get_words(self, soup: BeautifulSoup):
        # THIS IS DESTRUCTIVE SO IT HAS TO BE RUN AFTER EVERYTHING ELSE
        # Remove unwanted HTML tags that do not contain page content
        # These tags often include code, styling, metadata, or the document root
        for tag in soup(["script", "style", "head", "title", "meta", "[document]"]):
            tag.decompose()
        for comment in soup.find_all(string = self.is_comment):
            comment.decompose() # permanently removes the tag and its content from the soup
        # finally gets text
        # Extract visible text from the remaining soup
        # separator=' ' ensures spaces between text from different tags
        # strip=True removes leading and trailing whitespace
        text = soup.get_text(separator=' ', strip=True)
        # tokenize by letters and apostrophes only
        # Tokenize the text into words
        # Only letters (a-z, A-Z) and apostrophes in contractions are kept
        # Example: "don't" becomes "don't", "O'Reilly" becomes "O'Reilly"
        # Converts all words to lowercase for normalization
        words = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)*", text.lower())
        return words

    def report_word_frequencies(self, words: list[str]):
        # Initialize a dictionary to count word occurrences
        # defaultdict(int) automatically sets missing keys to 0
        frequencies = defaultdict(int)
        for word in words:
            # Don't report stop words
            # Only count words that are:
            # 1. Longer than 1 character
            # 2. Not in the STOP_WORDS list (common words like "the", "and", etc.)
            if len(word) > 1 and word not in STOP_WORDS:
                frequencies[word] += 1
        self.report["word frequencies"] = frequencies

    def run(self): # Process a single page and generate its report
        self.report_page_url(self.url)
        self.words = self.get_words(self.soup)
        self.report_page_length(self.words)
        self.report_word_frequencies(self.words)
        # Queue report
        Report.report_queue.put(self.report) # Add the report to the shared report queue for aggregation when the crawler ends

    @classmethod
    # Call this in main thread (launch.py)
    def aggregate_reports(cls):
        while not Report.report_queue.empty():
            # get the report from the queue
            report = Report.report_queue.get()
            # Add url to set and then count the length of the set
            Report.unique_pages.add(report["url"])
            # Update url of longest page length
            if report["page length"] > Report.longest_length:
                Report.longest_length = report["page length"]
                Report.longest_page = report["url"]
            # Add/update word frequencies
            for word, frequency in report["word frequencies"].items():
                Report.combined_word_frequencies[word] += frequency
        # get the 50 most common words
        Report.top_50_words = sorted(Report.combined_word_frequencies,
                             key = Report.combined_word_frequencies.get,
                             reverse = True)[:50]
        # count the pages in each subdomain
        for page in Report.unique_pages:
            host = parse.urlparse(page).hostname
            if host:
                Report.subdomain_page_count[host] += 1
        # sort them alphabetically into a new dict
        Report.subdomain_page_count = dict(sorted(Report.subdomain_page_count.items()))

    @classmethod
    def write_results(cls, file_name = "report.txt"):
        # Write the final aggregated report to a file
        with open(file_name, 'w') as out_file:
            out_file.write(f"Number of unique pages found: {len(Report.unique_pages)}\n")
            out_file.write(f"Longest page in terms of word count: {Report.longest_page}\n")
            out_file.write(f"Word count: {Report.longest_length}\n")
            out_file.write("50 most common words (ignoring stop words):\n")
            # Print 10 words per line for readability
            print(*Report.top_50_words[0:10], sep=", ", file = out_file)
            print(*Report.top_50_words[10:20], sep=", ", file = out_file)
            print(*Report.top_50_words[20:30], sep=", ", file = out_file)
            print(*Report.top_50_words[30:40], sep=", ", file = out_file)
            print(*Report.top_50_words[40:50], sep=", ", file = out_file)
            out_file.write(f"Number of subdomains: {len(Report.subdomain_page_count)}\n")
            out_file.write("Subdomain page count:\n")
            for subdomain, page_count in Report.subdomain_page_count.items():
                out_file.write(f"{subdomain}\t{page_count}\n")

STOP_WORDS = set("""
a
about
above
after
again
against
all
am
an
and
any
are
aren't
as
at
be
because
been
before
being
below
between
both
but
by
can't
cannot
could
couldn't
did
didn't
do
does
doesn't
doing
don't
down
during
each
few
for
from
further
had
hadn't
has
hasn't
have
haven't
having
he
he'd
he'll
he's
her
here
here's
hers
herself
him
himself
his
how
how's
i
i'd
i'll
i'm
i've
if
in
into
is
isn't
it
it's
its
itself
let's
me
more
most
mustn't
my
myself
no
nor
not
of
off
on
once
only
or
other
ought
our
ours
ourselves
out
over
own
same
shan't
she
she'd
she'll
she's
should
shouldn't
so
some
such
than
that
that's
the
their
theirs
them
themselves
then
there
there's
these
they
they'd
they'll
they're
they've
this
those
through
to
too
under
until
up
very
was
wasn't
we
we'd
we'll
we're
we've
were
weren't
what
what's
when
when's
where
where's
which
while
who
who's
whom
why
why's
with
won't
would
wouldn't
you
you'd
you'll
you're
you've
your
yours
yourself
yourselves
""".split())