from Plugin import Plugin

class AWSPlugin(Plugin):
    
    domain = 'docs.aws.amazon.com'   
    
    remove_html_selectors = [
        'awsdocs-page-header',
        'awsdocs-copyright',
        'awsdocs-thumb-feedback',
        'awsdocs-language-banner',
        'awsdocs-filter-selector',
    ]
    
