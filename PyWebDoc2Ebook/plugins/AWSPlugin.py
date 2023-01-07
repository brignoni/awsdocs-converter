from Plugin import Plugin


class AWSPlugin(Plugin):

    domain = 'docs.aws.amazon.com'

    html_content_selector = '#main-col-body'

    html_remove_selectors = [
        'awsdocs-page-header',
        'awsdocs-copyright',
        'awsdocs-thumb-feedback',
        'awsdocs-language-banner',
        'awsdocs-filter-selector',
    ]

    toc_filename = 'toc-contents.json'

    toc_format = 'json'

    def toc_json(self, json):
        
        if 'title' in json and 'href' in json:
            self.add(json['title'], json['href'])

        if 'contents' not in json:
            return self.items()

        for child in json['contents']:
            self.toc(child)

        return self.items()
