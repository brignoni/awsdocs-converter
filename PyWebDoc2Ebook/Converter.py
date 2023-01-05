import bs4
import json
import markdownify
import sys
import os
import re
import requests
from Integration import PluginData
from plugins.AWSPlugin import AWSPlugin
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

CALIBRE_CLI_PATH = '/Applications/calibre.app/Contents/MacOS/ebook-convert'
OUTPUT_EBOOK = '.output_ebook/'
OUTPUT_MD = '.output_markdown/'
ENTER_DOC_URL = 'Enter AWS Documentation URL: '
REGEX_DOC_URL = r'^https://docs.aws.amazon.com/.*'
REGEX_MD_IMAGE = r'\((/images/.*\.\w+)\)'
RESOURCES_DIR = '/resources'
REMOVE_HTML_TAGS = [
    'awsdocs-page-header',
    'awsdocs-copyright',
    'awsdocs-thumb-feedback',
    'awsdocs-language-banner',
    'awsdocs-filter-selector',
]

ADAPTERS = [
    AWSPlugin()
]


class TocItem:

    title: str
    uri: str
    children = []

    def __init__(self, title, uri, children=[]) -> None:
        self.title = title
        self.uri = uri
        self.children = children

    def __str__(self) -> str:
        return f'<TocItem title="{self.title}" uri="{self.uri}" childrenCount={len(self.children)}>'


class Docs:

    _content = None
    _toc = None

    def __init__(self, url, plugin, toc={'root': True}) -> None:
        self._url = url
        self._plugin = plugin
        pass

    def to_epub(self):

        self.process()

        # path_ebook = f'{OUTPUT_EBOOK}{self.id()}'
        # path_md = f'{OUTPUT_MD}{self.id()}'
        # path_id = f'{OUTPUT_MD}{self.id()}/{self.id()}'

        # metadata = [
        #     f'title="{self.title()}"',
        #     'author="AWS"',
        #     'language="en-US"',
        # ]

        # metadata_args = ' --metadata '.join(map(str, metadata))

        # epub_command = f'pandoc --resource-path {path_md}{RESOURCES_DIR} --metadata {metadata_args} -o {path_ebook}.epub {path_id}.md'

        # print(epub_command)

        # os.system(epub_command)

        # return self

    def to_mobi(self):

        self.to_epub()

        # path_ebook = f'{OUTPUT_EBOOK}{self.id()}'

        # mobi_args = [
        #     '--mobi-file-type new',
        #     '--personal-doc',
        #     '--prefer-author-sort',
        # ]

        # mobi_args_str = ' '.join(map(str, mobi_args))

        # mobi_command = f'{CALIBRE_CLI_PATH} {path_ebook}.epub {path_ebook}.mobi {mobi_args_str}'

        # print(mobi_command)

        # os.system(mobi_command)

    def base_url(self) -> str:
        return re.sub("/[\w+\-\_]*.html", "/", self._url.split('?')[0])

    def url(self):

        if 'href' not in self._toc:
            return self._url

        return self.base_url() + '/' + self._toc['href']

    def id(self) -> str:
        return self.base_url().split('/')[len(self.base_url().split('/'))-2]

    def content_title(self):
        return self.content().h1.text.strip()

    def title(self):

        # if 'title' not in self._toc:
        #     return self.content_title()

        return self._toc['title']

    def items(self):

        res = requests.get(self.base_url() + 'toc-contents.json')

        self._toc = self._plugin.toc(json.loads(res.text))

        return self._toc

    def process(self):

        if not os.path.exists(OUTPUT_MD + self.id()):
            os.makedirs(OUTPUT_MD + self.id())

        # Flatten all items to a single markdown string
        md = '\n'.join(list(map(self.item, self.items())))

        # Process markdown images
        md = self.images(md)

        # filename = self.id() + '/' + self.id()
        # file = open(OUTPUT_MD + filename + '.md', 'w+')
        # file.write(md)
        # file.close()

    def images(self, md) -> str:

        images = re.findall(REGEX_MD_IMAGE, md)

        if len(images) == 0:
            return md

        RESOURCES_OUTPUT_DIR = OUTPUT_MD + self.id() + RESOURCES_DIR + '/'

        if not os.path.exists(RESOURCES_OUTPUT_DIR):
            os.makedirs(RESOURCES_OUTPUT_DIR)

        for image in images:

            image_filename = image.split('/')[-1]

            print('Processing image: ' + image_filename)

            # Replace leading slash with relative path
            md = re.sub(image, './' + image_filename, md)

            # Download image file to expected path
            image_file = open(RESOURCES_OUTPUT_DIR + image_filename, 'wb')
            res = requests.get(self.base_url() + '/images/' + image_filename)
            image_file.write(res.content)
            image_file.close()

        return md

    def item(self, item: TocItem):

        print(item)

        # Make HTTP request to get the HTML content
        html = self.request(item)

        # Let the plugin pre-process HTML
        html = self._plugin.html(html)

        # Convert HTML to Markdown
        md = markdownify.markdownify(html, heading_style=markdownify.ATX)

        # Let the plugin post-process markdown
        md = self._plugin.markdown(md, PluginData(self.base_url()))

        for item in item.children:
            md += self.item(item)

        return md

    def request(self, item: TocItem):

        if self._content is not None:
            return self._content

        res = requests.get(self.base_url() + item.uri)

        html = res.content.decode('utf-8')

        soup = bs4.BeautifulSoup(html, 'lxml')

        self._content = soup.select_one(self._plugin.mapping('content'))

        for REMOVE_TAG in REMOVE_HTML_TAGS:
            for tag in self._content.find_all(REMOVE_TAG):
                tag.decompose()

        return self._content

    def validate(self) -> bool:

        match = re.compile(REGEX_DOC_URL).match(self._url)

        if match is None:
            raise ValueError(ENTER_DOC_URL)

        return True

    def __str__(self) -> str:
        return f'<Docs id={self.id()}>'


def init(args) -> Docs:

    if len(args) > 0:
        url = args[0]
    else:
        url = input(ENTER_DOC_URL)

    # @todo select plugin from regex matcher
    plugin = ADAPTERS[0]

    return Docs(url, plugin)
