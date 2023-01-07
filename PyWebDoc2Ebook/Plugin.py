import re


class TocItem:

    title: str
    uri: str

    def __init__(self, title: str, uri: str) -> None:
        self.title = title
        self.uri = uri

    def __str__(self) -> str:
        return f'<TocItem uri="{self.uri}"/>'


class TocItems:

    items = []

    title = 'Untitled'

    uri: str

    def add(self, title, uri):
        if type(title) != str or type(uri) != str:
            return
        if len(self.items) == 0:
            self.title = title
            self.uri = uri
        self.items.append(TocItem(title, uri))

    def __str__(self) -> str:

        output = f'<TocItems count="{len(self.items)}">\n'

        for item in self.items:
            output += f' {str(item)}\n'

        output += f'</TocItems>\n'

        return output


class Plugin:

    domain: str

    absolute_url_regex = r"^(http|https)://(.*)"

    image_regex = r'\((/images/.*\.\w+)\)'

    link_regex = r"^(\/|https://|http://)(.*)"

    language = 'en-US'

    html_content_selector = 'body'

    html_toc_selector = ''

    html_remove_selectors = []

    # Alternate filename for TOC.
    # Defaults to find the TOC in the initial URL as HTML content.
    toc_filename = ''

    # The expected TOC content format
    # Values: html | json
    toc_format = 'html'

    _items = TocItems()

    def add(self, title, uri):
        self._items.add(title, uri)

    def toc(self, response):
        if self.toc_format == 'json':
            return self.toc_json(response)
        else:
            return self.toc_html(response)

    def toc_html(self, soup):
        links = soup.findAll('a', attrs={
            'href': re.compile(self.link_regex)
        })

        for link in links:
            self.add(link.get_text(), link.get('href'))

        return self.items()

    def toc_json(self, json):

        print(f'{self.__class__.__name__}.toc_json() not implemented.')

        return self.items()

    def html(self, html: str) -> str:
        html = re.sub(r'[\ \n]{2,}', ' ', html)
        html = re.sub(r'<p>[\ \n]{1,}', '<p>', html)
        html = re.sub(r'[\ \n]{1,}</p>', '</p>', html)
        html = re.sub(r'</ul>', '</ul>\n\n', html)
        return html

    def html_remove(self):
        return self.html_remove_selectors

    def markdown(self, md) -> str:
        # Remove excess new lines
        return re.sub(r'[\n]{4,}\t\+', '\n\t+', md)

    def url(self, item, base_url: str):
        if re.search(self.absolute_url_regex, item.uri):
            return item.uri

        if base_url.endswith('/'):
            base_url = base_url[:-1]

        uri = item.uri

        if uri.startswith('/'):
            uri = uri[1:]

        return f'{base_url}/{uri}'

    def toc_url(self, url):
        return None

    def items(self) -> TocItems:
        return self._items

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} domain="{self.domain}"/>'
