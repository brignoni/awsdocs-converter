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

    image_regex = r'\((/images/.*\.\w+)\)'

    language = 'en-US'

    map = {
        'title': 'title',
        'uri': 'href',
        'children': 'contents',
    }

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

    def mapping(self, key) -> str:
        return self.map.get(key)

    def add(self, title, uri):
        self._items.add(title, uri)

    def toc(self, response):
        if self.toc_format == 'json':
            return self.toc_json(response)
        else:
            return self.toc_html(response)

    def toc_html(self, soup):

        starting_with = f"https://{self.domain}"

        links = self.html_links(soup, starting_with)

        for link in links:
            self.add(link.get_text(), link.get('href'))

        return self.items()

    def toc_json(self, json):

        if self.mapping('title') in json and self.mapping('uri') in json:
            self.add(
                json[self.mapping('title')],
                json[self.mapping('uri')]
            )

        if self.mapping('children') not in json:
            return self.items()

        for child in json[self.mapping('children')]:
            self.toc(child)

        return self.items()

    def html(self, html: str) -> str:
        html = re.sub(r'[\ \n]{2,}', ' ', html)
        html = re.sub(r'<p>[\ \n]{1,}', '<p>', html)
        html = re.sub(r'[\ \n]{1,}</p>', '</p>', html)
        html = re.sub(r'</ul>', '</ul>\n\n', html)
        return html

    def html_remove(self):
        return self.html_remove_selectors

    def html_links(self, soup, starting_with=None):
        attrs = {}
        if type(starting_with) == str:
            attrs = {
                'href': re.compile(f"^{starting_with}")
            }
        return soup.findAll('a', attrs=attrs)

    def markdown(self, md) -> str:
        # Remove excess new lines
        return re.sub(r'[\n]{4,}\t\+', '\n\t+', md)

    def url(self, item, base_url: str):
        if re.search(base_url, item.uri):
            return item.uri
        return f'{base_url}/{item.uri}'

    def items(self) -> TocItems:
        return self._items

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} domain="{self.domain}"/>'
