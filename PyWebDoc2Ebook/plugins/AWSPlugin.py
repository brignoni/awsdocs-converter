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
