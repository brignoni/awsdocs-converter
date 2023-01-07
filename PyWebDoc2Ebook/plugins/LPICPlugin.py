from Plugin import Plugin


class LPICPlugin(Plugin):

    domain = 'learning.lpi.org'

    html_content_selector = '.page-content__container'

    html_toc_selector = '.hierarchy'
