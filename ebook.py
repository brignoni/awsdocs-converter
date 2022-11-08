import bs4
import glob
import json
import markdownify
import os
import re
import requests

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
            return self.content().h1.text.trim()

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

    def ebook(self):
        if not os.path.exists(OUTPUT_MD + self.id()):
            os.makedirs(OUTPUT_MD + self.id())

        self.toc()

        print(self)

        for idx, page in enumerate(self.children()):
            filename = self.id() + '/' + str(idx).zfill(2) + '-' + page.id()
            file = open(OUTPUT_MD + filename + '.md', 'w+')
            file.write(page.markdown())
            file.close()

        return self

    def __str__(self) -> str:
        return f'<AWSDoc id={self.id()}>'


def get_link_content(link, state):
    link_response = requests.get(state['base_url'] + link['href'])

    soup = bs4.BeautifulSoup(link_response.content.decode('utf-8'), 'lxml')

    body = soup.select_one('#main-col-body')

    for remove_tag in remove_tags:
        for tag in body.find_all(remove_tag):
            tag.decompose()

    html = re.sub(r'[\ \n]{2,}', ' ', str(body))
    html = re.sub(r'<p>[\ \n]{1,}', '<p>', html)
    html = re.sub(r'[\ \n]{1,}</p>', '</p>', html)
    html = re.sub(r'</ul>', '</ul>\n\n', html)

    md = markdownify.markdownify(
        html,
        heading_style=markdownify.ATX
    )

    md = re.sub(r'[\n]{4,}\t\+', '\n\t+', md)

    filename = state['id'] + '/' + \
        str(state['count']).zfill(2) + '-' + link['href']

    # html_file = open(OUTPUT_HTML + filename, 'w+')
    # html_file.write(html)
    # html_file.close()

    md_file = open(OUTPUT_MD + filename.replace('.html', '.md'), 'w+')
    md_file.write(md)
    md_file.close()

    state['count'] += 1

    if 'contents' in link:
        for sub_link in link['contents']:
            get_link_content(sub_link, state)

    return True


def main():

    url = input(ENTER_DOC_URL)

    root = AWSDocs(url)

    # Check this is a valid AWS Whitepaper URL.
    root.validate()

    # Download the HTML pages, convert to markdown and write to disk.
    root.ebook()

    # html_file = open(OUTPUT_MD + state['id'] + '/title.txt', 'w+')
    # html_file.write(f'---\ntitle: {title}\nauthor: AWS\nlanguage: en-US')
    # html_file.close()

    # filenames = glob.glob(OUTPUT_MD + state['id'] + '/*.md')

    # filenames.sort()

    # filenames_str = ' '.join(map(str, filenames))

    # os.system(
    #     f'pandoc -o .output_ebook/{id}.epub {OUTPUT_MD}{id}/title.txt {filenames_str}')
    # os.system(
    #     f'/Applications/calibre.app/Contents/MacOS/ebook-convert .output_ebook/{id}.epub .output_ebook/{id}.mobi')

    return True


if __name__ == "__main__":
    main()
