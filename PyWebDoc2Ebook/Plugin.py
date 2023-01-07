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

    title: str

    uri: str

    def add(self, title: str, uri: str):
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
        'content': '#main-col-body'
    }

    remove_html_selectors = []

    _items = TocItems()

    def mapping(self, key) -> str:
        return self.map.get(key)

    def add(self, item):
        if self.mapping('title') not in item:
            return
        if self.mapping('uri') not in item:
            return
        self._items.add(
            item[self.mapping('title')],
            item[self.mapping('uri')]
        )

    def toc(self, response):

        self.add(response)

        if self.mapping('children') not in response:
            return self._items

        for child in response[self.mapping('children')]:
            self.toc(child)

        return self._items

    def html(self, html: str) -> str:
        html = re.sub(r'[\ \n]{2,}', ' ', html)
        html = re.sub(r'<p>[\ \n]{1,}', '<p>', html)
        html = re.sub(r'[\ \n]{1,}</p>', '</p>', html)
        html = re.sub(r'</ul>', '</ul>\n\n', html)
        return html

    def html_remove(self):
        return self.remove_html_selectors

    def markdown(self, md) -> str:
        # Remove excess new lines
        return re.sub(r'[\n]{4,}\t\+', '\n\t+', md)

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} domain="{self.domain}"/>'
