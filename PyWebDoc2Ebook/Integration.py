import re
import Converter

class PluginData:
    url: str
    
    def __init__(self, url) -> None:
        self.url = url
        pass

class Plugin:

    map = {
        'title': 'title',
        'uri': 'href',
        'children': 'contents',
        'content': '#main-col-body'
    }

    def __init__(self) -> None:
        pass

    def mapping(self, key) -> str:
        return self.map.get(key)

    def toc(self, response):
        if self.mapping('children') not in response:
            return []

        items = []
        for item in response[self.mapping('children')]:
            items.append(Converter.TocItem(
                item[self.mapping('title')],
                item[self.mapping('uri')],
                self.toc(item)
            ))

        return items

    def html(self, html):
        html = re.sub(r'[\ \n]{2,}', ' ', str())
        html = re.sub(r'<p>[\ \n]{1,}', '<p>', html)
        html = re.sub(r'[\ \n]{1,}</p>', '</p>', html)
        html = re.sub(r'</ul>', '</ul>\n\n', html)
        return html

    def markdown(self, md, data: PluginData):

        # Remove excess new lines
        md = re.sub(r'[\n]{4,}\t\+', '\n\t+', md)

        # Replace relative ./ paths with absolute
        md = re.sub(r'\.\/', data.url, md)

        return md

    def __str__(self) -> str:
        return f'<{self.__class__.__name__}>'