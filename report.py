# Create a way collect data from each worker/scraper instance

from queue import Queue
from bs4 import BeautifulSoup, Comment
from collections import defaultdict
import re
from urllib import parse

#--------------Report stuff-----------------------
# 1. Unique pages counted after fragment removal done
# 2. Longest page? done
# 3. Top 50 words sorted by frequency (most common words) WIP
# 4. Subdomains sorted alphabetically done
# 5. Subdomain counts are unique pages per subdomain, not raw visits (subdomain count) done
# 6. Stopwords explicitly mentioned in report WIP

class Report:
    # class Queue to handle multithreading
    report_queue = Queue()
    unique_pages = set()
    subdomain_page_count = defaultdict(int)
    longest_length = -1
    longest_page = str()
    combined_word_frequencies = defaultdict(int)
    top_50_words = list()

    def __init__(self, url: str, soup: BeautifulSoup):
        self.report = dict()
        self.url = url
        self.soup = soup
        self.words = list()

    def report_page_url(self, url: str):
        # urllib.parse.urldefrag should work
        url, frag = parse.urldefrag(url)
        url = url.lower().rstrip('/')
        self.report["url"] = url

    def report_page_length(self, words: list[str]):
        self.report["page length"] = len(words)

    def is_comment(self, element):
        return isinstance(element, Comment)

    def get_words(self, soup: BeautifulSoup):
        # THIS IS DESTRUCTIVE SO IT HAS TO BE RUN AFTER EVERYTHING ELSE
        # filter out tags and comments
        for tag in soup(["script", "style", "head", "title", "meta", "[document]"]):
            tag.decompose()
        for comment in soup.find_all(string = self.is_comment):
            comment.decompose()
        # finally gets text
        text = soup.get_text(separator=' ', strip=True)
        # tokenize by letters and apostrophes only
        words = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)*", text.lower())
        return words

    def report_word_frequencies(self, words: list[str]):
        frequencies = defaultdict(int)
        for word in words:
            # Don't report stop words
            if len(word) > 1 and word not in STOP_WORDS:
                frequencies[word] += 1
        self.report["word frequencies"] = frequencies

    def run(self):
        self.report_page_url(self.url)
        self.words = self.get_words(self.soup)
        self.report_page_length(self.words)
        self.report_word_frequencies(self.words)
        # Queue report
        Report.report_queue.put(self.report)

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
        with open(file_name, 'w') as out_file:
            out_file.write(f"Number of unique pages found: {len(Report.unique_pages)}\n")
            out_file.write(f"Longest page in terms of word count: {Report.longest_page}\n")
            out_file.write("50 most common words (ignoring stop words):\n")
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