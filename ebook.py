import requests
import bs4
import sys
import re
import json
import markdownify

remove_tags = [
    'awsdocs-page-header',
    'awsdocs-copyright',
    'awsdocs-thumb-feedback',
    'awsdocs-language-banner',
    'awsdocs-filter-selector',
]

page_still_valid = True
authors = set()
page = 1

# get html with request
# get menu items
# get body

def main():
    url = sys.argv[1]

    base_url = re.sub("/[\w+\-\_]*.html", "/", url)
    
    print(base_url)
    
    toc_response = requests.get(base_url + 'toc-contents.json')
    
    toc = json.loads(toc_response.text)
    
    print(toc['contents'])

    for link in toc['contents']:
        
        link_response = requests.get(base_url + link['href'])
        
        soup = bs4.BeautifulSoup(link_response.text,'lxml', from_encoding='utf-8')

        body = soup.select_one('#main-col-body')
        
        for remove_tag in remove_tags:
            for tag in body.find_all(remove_tag):
                tag.decompose()
        
        html = re.sub(r'[\ \n]{2,}', ' ', str(body))
        html = re.sub(r'<p>[\ \n]{1,}', '<p>', html)
        html = re.sub(r'[\ \n]{1,}</p>', '</p>', html)
        
        md = markdownify.markdownify(
            html, 
            heading_style=markdownify.ATX
        )
  
        html_file = open('.output/' + link['href'],'w+')
        html_file.write(html)
        html_file.close()
        
        md_file = open('.output/' + link['href'].replace('.html','.md'),'w+')
        md_file.write(md)
        md_file.close()
        
    return True

if __name__ == "__main__":
    main()
