import bs4
import markdownify
import sys
import os
import re
import requests
import PluginImporter
from Plugin import TocItem

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
OUTPUT = '.output/'
ENTER_DOC_URL = 'Enter URL: '
RESOURCES_DIR = '/resources'


class PyWebDoc2Ebook:

    _content = dict()
    _toc = None

    def __init__(self, url, plugin) -> None:
        self._url = url
        self._plugin = plugin

    def epub(self):

        if not self.markdown():
            print('Epub processing aborted.')
            return False

        metadata = [
            f'title="{self.title()}"',
            f'author="{self._plugin.domain}"',
            f'language="{self._plugin.language}"',
        ]

        metadata_args = ' --metadata '.join(map(str, metadata))

        epub_command = f'pandoc --resource-path {self.path()}{RESOURCES_DIR} --metadata {metadata_args} -o {self.pathname()}.epub {self.pathname()}.md'

        print(epub_command)

        os.system(epub_command)

        return True

    def mobi(self):

        if not self.epub():
            print('Mobi processing aborted.')
            return False

        mobi_args = [
            '--mobi-file-type new',
            '--personal-doc',
            '--prefer-author-sort',
        ]

        mobi_args_str = ' '.join(map(str, mobi_args))

        mobi_command = f'{CALIBRE_CLI_PATH} {self.pathname()}.epub {self.pathname()}.mobi {mobi_args_str}'

        print(mobi_command)

        os.system(mobi_command)

        return True

    def base(self) -> str:
        return '/'.join(self._url.split('/')[:-1])

    def prefix(self):
        return re.sub(r'[\.]+', '-', self._plugin.domain)

    def suffix(self):
        segments = self._url.split('/')
        return segments.pop()

    def id(self) -> str:
        id = list(filter(lambda s: s, self._url.split('/'))).pop()
        id = re.sub(r'(\.html)', '', id)
        return f'{self.prefix()}-{id}'

    def path(self) -> str:
        return f'{OUTPUT}{self.id()}'

    def pathname(self):
        return f'{OUTPUT}{self.id()}/{self.id()}'

    def title(self):
        return self._toc.title

    def items(self):

        if self._toc is not None:
            return self._toc.items

        url = self._url

        plugin_toc_url = self._plugin.toc_url(self._url)


        if type(plugin_toc_url) == str:
            url = plugin_toc_url
        elif len(self._plugin.toc_filename) > 0:
            url = f'{self.base()}/{self._plugin.toc_filename}'

        res = requests.get(url)

        if self._plugin.toc_format == 'json':
            res = res.json()
        else:
            html = res.content.decode('utf-8')
            res = bs4.BeautifulSoup(html, 'lxml')

        self._toc = self._plugin.toc(res)

        return self._toc.items

    def markdown(self):

        if not self.found():
            print('No items found in TOC.')
            return False

        if not os.path.exists(self.path()):
            os.makedirs(self.path())

        # Flatten all items to a single markdown string.
        md = '\n'.join(list(map(self.item, self.items())))

        # Replace relative ./ paths with absolute URLs.
        md = re.sub(r'\.\/', self.base(), md)

        # Process markdown images.
        md = self.images(md)

        # Write file to output folder.
        file = open(self.pathname() + '.md', 'w+')
        file.write(md)
        file.close()

        return True

    def images(self, md: str) -> str:

        # Find all images and remove duplicates.
        images = list(set(re.findall(self._plugin.image_regex, md)))

        if len(images) == 0:
            return md

        RESOURCES_OUTPUT_DIR = self.path() + RESOURCES_DIR + '/'

        if not os.path.exists(RESOURCES_OUTPUT_DIR):
            os.makedirs(RESOURCES_OUTPUT_DIR)

        for image in images:

            image_filename = image.split('/')[-1]

            print('Processing image: ' + image_filename)

            # Replace leading slash with relative path.
            md = re.sub(image, './' + image_filename, md)

            # Download image file to expected path.
            image_file = open(RESOURCES_OUTPUT_DIR + image_filename, 'wb')
            res = requests.get(self.base() + '/images/' + image_filename)
            image_file.write(res.content)
            image_file.close()

        return md

    def found(self):
        return len(self.items()) > 0

    def item(self, item: TocItem):
        print(item)

        # Make HTTP request to get the HTML content.
        html = self.request(item)

        # Let the plugin pre-process HTML.
        html = self._plugin.html(str(html))

        # Convert HTML to Markdown.
        md = markdownify.markdownify(html, heading_style=markdownify.ATX)

        # Let the plugin post-process markdown
        md = self._plugin.markdown(md)

        return md

    def request(self, item: TocItem) -> str:

        if self._content.get(item.uri) is not None:
            return self._content.get(item.uri)

        url = self._plugin.url(item, self.base())

        res = requests.get(url)

        html = res.content.decode('utf-8')

        soup = bs4.BeautifulSoup(html, 'lxml')

        content = soup.select_one(self._plugin.html_content_selector)

        for REMOVE_TAG in self._plugin.html_remove():
            for tag in content.find_all(REMOVE_TAG):
                tag.decompose()

        self._content.update({item.uri: str(content)})

        return str(content)

    def __str__(self) -> str:
        return f'<PyWebDoc2Ebook id="{self.id()}"/>'


def init(url):

    plugin = PluginImporter.get_plugin_by_url(url)

    return PyWebDoc2Ebook(url, plugin)


def input(args) -> PyWebDoc2Ebook:

    if len(args) > 0:
        url = args[0]
    else:
        url = input(ENTER_DOC_URL)

    return init(url)
