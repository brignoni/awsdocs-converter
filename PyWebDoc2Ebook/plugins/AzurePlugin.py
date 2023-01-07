from Plugin import Plugin

# @todo - plugin in development
class AzurePlugin(Plugin):

    domain = 'learn.microsoft.com'

    html_content_selector = '.content'

    toc_format = 'json'

    def toc_url(self, url):
        return '/'.join(url.split('/')[:6]) + '/toc.json'

    def toc_json(self, json):

        def valid_href(href):
            if href.startswith('https://'):
                return False
            if href.startswith('./'):
                return False
            if href.startswith('../'):
                return False
            return True

        if 'toc_title' in json and 'href' in json and valid_href(json['href']):
            self.add(json['toc_title'], json['href'])

        children = []

        if 'items' in json:
            children = json['items']
        elif 'children' in json:
            children = json['children']

        if len(children) == 0:
            return self.items()

        # recursively look for children
        for child in children:
            self.toc_json(child)

        return self.items()
