# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, NavigableString
import urllib.request
from pathlib import Path
import requests
import os
from shutil import copyfile


def make_year_urls(start_year, end_year):
    year_urls = []
    base = 'https://www.federalreserve.gov/supervisionreg/srletters/'
    for i in range(start_year, end_year):
        url = base + str(i) + '.htm'
        year_urls.append(url)
    return year_urls


def get_doc_links(year_url):
    doc_links = []
    url = year_url
    print (url)
    hdr = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"}
    req = urllib.request.Request(url, headers=hdr)
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    for link in soup.findAll('a'):
        j = link.get('href').lower()
        if '/srletters/' in j and j.endswith('.htm') and j[-8:-4].isdigit():
            doc_link = 'https://www.federalreserve.gov' + j
            doc_links.append(doc_link)

    return doc_links


def fed_letters():

    year_urls = make_year_urls(1990,2020)
    for year_url in year_urls:
        doc_links = get_doc_links(year_url)
        for i in doc_links:
            docname = i[-10:-4]
            pname = 'frb_letters/' + docname + '.pdf'
            filename = Path(pname)

            if os.path.exists(filename):
                print (f'Already have {filename}')
                continue
            else:

                # try pdf first
                url = i.replace('.htm', '') + '.pdf'
                hdr = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest"}
                try:
                    response = requests.get(url)
                    if response.status_code != 404:
                        filename.write_bytes(response.content)
                        print (url)
                    else:
                        pname = 'frb_letters/' + docname + '.htm'
                        filename = Path(pname)

                        hdr = {'User-Agent': 'Mozilla/5.0'}
                        req = urllib.request.Request(i, headers=hdr)
                        page = urllib.request.urlopen(req)
                        soup = BeautifulSoup(page, 'html.parser')
                        with open(filename, "w") as file:
                            file.write(str(soup))
                        print (i)
                except Exception as e:
                    print (str(e))


def strip_tags(soup, invalid_tags):

    for tag in soup.findAll(True):
        if tag.name in invalid_tags:
            s = ""
            for c in tag.contents:
                if not isinstance(c, NavigableString):
                    c = strip_tags(c, invalid_tags)
                s += str(c)
            tag.replaceWith(s)
    return soup


def munge_letters():

    # convert htms to cleaned up html (removing FRB footers etc.)
    # also copy pdfs over to clean folder as is

    base_dir = 'frb_letters/'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    clean_dir = 'frb_letters/clean/'
    if not os.path.exists(clean_dir):
        os.makedirs(clean_dir)

    x = os.listdir(base_dir)


    pdfs = []
    htms = []
    for i in x:
        if i.endswith('.htm'):
            htms.append(i)
        elif i.endswith('.pdf'):
            pdfs.append(i)


    for i in pdfs:
        a = base_dir + i
        b = clean_dir + i
        copyfile(a,b)

    count = 0

    for i in htms:

        print (f'{count} out of {len(htms)} -- {i}')
        fname = base_dir + i
        with open(fname, 'rb') as f:
            contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
        c = soup.find_all('div', {'class': 'footer'}) + soup.find_all('div', {'class': 'pubfooter'})

        for j in c:
            j.decompose()

        # need to work on deleting links
        soup = strip_tags(soup, 'a')

        try:
            letter_name = i.replace('.htm', '')
            out_name = clean_dir + letter_name + '_clean.html'
            with open(out_name, "w") as file:
                file.write(str(soup))
            print (out_name)

        except Exception as e:
            print (c)
            print (str(e))
            print (i)
            input('enter')

        count +=1

def run_frb():
    if not os.path.exists('frb_letters/'):
        os.makedirs('frb_letters/')
    fed_letters()
    munge_letters()

if __name__ == "__main__":

    run_frb()





