import bs4
import glob
import json
import markdownify
import os
import re
import requests

CALIBRE_EBOOK_PATH = '/Applications/calibre.app/Contents/MacOS/ebook-convert'
OUTPUT_EBOOK = '.output_ebook/'
OUTPUT_MD = '.output_markdown/'
URL_REGEX = r'^https://docs.aws.amazon.com/.*'
ENTER_DOC_URL = 'Enter AWS Documentation URL: '

REMOVE_HTML_TAGS = [
    'awsdocs-page-header',
    'awsdocs-copyright',
    'awsdocs-thumb-feedback',
    'awsdocs-language-banner',
    'awsdocs-filter-selector',
]


class AWSDocsPage:

    def __init__(self, url, toc={'root': True}) -> None:
        self._url = url
        self._toc = toc
        pass

    def base_url(self) -> str:
        return re.sub("/[\w+\-\_]*.html", "/", self._url.split('?')[0])

    def url(self):
        if 'href' not in self._toc:
            return self._url
        return self.base_url() + '/' + self._toc['href']

    def id(self) -> str:
        if 'href' in self._toc:
            return re.sub('.html', '', self._toc['href'])

        return self.base_url().split('/')[len(self.base_url().split('/'))-2]

    def content(self):
        if hasattr(self, '_content'):
            return self._content
        res = requests.get(self.url())
        html = res.content.decode('utf-8')
        soup = bs4.BeautifulSoup(html, 'lxml')
        self._content = soup.select_one('#main-col-body')

        for REMOVE_TAG in REMOVE_HTML_TAGS:
            for tag in self._content.find_all(REMOVE_TAG):
                tag.decompose()

        return self._content

    def title(self):
        if 'title' not in self._toc:
            return self.content().h1.text.strip()

        return self._toc['title']

    def children(self) -> list:
        if 'contents' in self._toc:
            return list(map(lambda page_toc: AWSDocsPage(self._url, page_toc), self._toc['contents']))
        else:
            return []

    def has_children(self):
        return len(self.children()) > 0

    def markdown(self):
        html = re.sub(r'[\ \n]{2,}', ' ', str(self.content()))
        html = re.sub(r'<p>[\ \n]{1,}', '<p>', html)
        html = re.sub(r'[\ \n]{1,}</p>', '</p>', html)
        html = re.sub(r'</ul>', '</ul>\n\n', html)

        md = markdownify.markdownify(html, heading_style=markdownify.ATX)

        md = re.sub(r'[\n]{4,}\t\+', '\n\t+', md)

        if self.has_children():
            for page in self.children():
                print(page)
                md += page.markdown() + "\n\n---\n\n"

        return md

    def validate(self) -> bool:
        match = re.compile(URL_REGEX).match(self._url)
        if match is None:
            raise ValueError(ENTER_DOC_URL)
        return self

    def __str__(self) -> str:
        return f'<AWSDocsPage id={self.id()}>'


class AWSDocs(AWSDocsPage):

    def toc(self):
        if 'contents' in self._toc:
            return self._toc['contents']
        res = requests.get(self.base_url() + 'toc-contents.json')
        self._toc = json.loads(res.text)
        return self._toc['contents']

    def to_markdown(self):
        if not os.path.exists(OUTPUT_MD + self.id()):
            os.makedirs(OUTPUT_MD + self.id())

        self.toc()

        print(self)

        for idx, page in enumerate(self.children()):
            filename = self.id() + '/' + str(idx).zfill(2) + '-' + page.id()
            file = open(OUTPUT_MD + filename + '.md', 'w+')
            file.write(page.markdown())
            file.close()

    def to_ebook(self):

        self.to_markdown()

        filenames = glob.glob(OUTPUT_MD + self.id() + '/*.md')

        filenames.sort()

        filenames_args = ' '.join(map(str, filenames))

        metadata_path = OUTPUT_MD + self.id() + '/metadata.yaml'

        metadata = open(metadata_path, 'w+')
        metadata.write(f'---\ntitle: {self.title()}\nauthor: AWS\nlanguage: en-US\n---')
        metadata.close()

        epub_command = f'pandoc -o {OUTPUT_EBOOK}{self.id()}.epub {metadata_path} {filenames_args}'

        os.system(epub_command)

        return self

    def to_mobi(self):
        self.to_ebook()
        id = self.id()
        mobi_command = f'{CALIBRE_EBOOK_PATH} {OUTPUT_EBOOK}{self.id()}.epub {OUTPUT_EBOOK}{self.id()}.mobi'
        os.system(mobi_command)

    def __str__(self) -> str:
        return f'<AWSDoc id={self.id()}>'


def main():

    url = input(ENTER_DOC_URL)

    doc = AWSDocs(url)

    doc.validate()

    doc.to_mobi()

    return True


if __name__ == "__main__":
    main()
