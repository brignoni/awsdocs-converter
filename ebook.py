import bs4
import glob
import json
import markdownify
import os
import re
import requests

remove_tags = [
    'awsdocs-page-header',
    'awsdocs-copyright',
    'awsdocs-thumb-feedback',
    'awsdocs-language-banner',
    'awsdocs-filter-selector',
]

OUTPUT_HTML = '.output_html/'
OUTPUT_MD = '.output_md/'


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

    filename = state['id'] + '/' + str(state['count']).zfill(2) + '-' + link['href']

    html_file = open(OUTPUT_HTML + filename, 'w+')
    html_file.write(html)
    html_file.close()

    md_file = open(OUTPUT_MD + filename.replace('.html', '.md'), 'w+')
    md_file.write(md)
    md_file.close()

    state['count'] += 1

    if 'contents' in link:
        for sub_link in link['contents']:
            get_link_content(sub_link, state)

    return True


def main():
    
    url = input('Enter AWS Whitepaper URL: ')
    
    base_url = re.sub("/[\w+\-\_]*.html", "/", url.split('?')[0])
    
    id = base_url.split('/')[len(base_url.split('/'))-2]
    
    if not os.path.exists(OUTPUT_MD + id):
        os.makedirs(OUTPUT_MD + id)

    if not os.path.exists(OUTPUT_HTML + id):
        os.makedirs(OUTPUT_HTML + id)
    
    state = {'count': 0, 'base_url': base_url, 'id': id}

    print(state)

    toc_response = requests.get(state['base_url'] + 'toc-contents.json')
    
    home_response = requests.get(url)

    soup = bs4.BeautifulSoup(home_response.content.decode('utf-8'), 'lxml')

    home_body = soup.select_one('#main-col-body')

    title = home_body.h1.text

    toc = json.loads(toc_response.text)

    for link in toc['contents']:
        get_link_content(link, state)

    html_file = open(OUTPUT_MD + state['id'] + '/title.txt', 'w+')
    html_file.write(f'---\ntitle: {title}\nauthor: AWS\nlanguage: en-US')
    html_file.close()

    filenames = glob.glob(OUTPUT_MD + state['id'] + '/*.md')

    filenames.sort()
    
    filenames_str = ' '.join(map(str,filenames))

    os.system(f'pandoc -o .output_ebook/{id}.epub {OUTPUT_MD}{id}/title.txt {filenames_str}')
    os.system(f'/Applications/calibre.app/Contents/MacOS/ebook-convert .output_ebook/{id}.epub .output_ebook/{id}.mobi')

    return True


if __name__ == "__main__":
    main()
