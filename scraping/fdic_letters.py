# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib.request
import pickle
import os.path
import os


def fdic_letter_links():

    category_links = get_tier1_links()

    letter_links = []
    for i in category_links:
        url = i
        print (url)
        hdr = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"}
        req = urllib.request.Request(url, headers=hdr)
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        for link in soup.findAll('a'):
            try:
                j = link.get('href').lower()
                if j.count('-') >= 2 and j.startswith('4000'):
                    m = 'https://www.fdic.gov/regulations/laws/rules/' + j
                    letter_links.append(m)
            except:
                pass

        print (f'length of letter_links: {len(letter_links)}')

    print ('pickling...')
    with open('fdic_letters/fdic_doc_links.pickle', 'wb') as handle:
        pickle.dump(letter_links, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return letter_links


def get_tier1_links():

    url = 'https://www.fdic.gov/regulations/laws/rules/4000-50.html'
    category_links = []
    print (url)
    hdr = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"}
    req = urllib.request.Request(url, headers=hdr)
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    for link in soup.findAll('a'):
        try:
            j = link.get('href').lower()
            if j.startswith('4000-'):
                print (j)
                m = 'https://www.fdic.gov/regulations/laws/rules/' + j
                category_links.append(m)
        except:
            pass

    return category_links


def download_letters():

    with open('fdic_letters/fdic_doc_links.pickle', 'rb') as handle:
        doc_links = pickle.load(handle)

    raw_source_dir_name = 'fdic_letters/'

    count = 0
    for i in doc_links:
        url = i

        letter_name = 'FDIC-' + i.split('.html#fdic4000')[1]
        filename = raw_source_dir_name + letter_name + '.html'

        if os.path.isfile(filename):
            print (f'already have filename: {filename}')
            count += 1
            print (f'completed {count} out of {len(doc_links)}')
            continue
        else:

            print (filename, url)

            hdr = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"}
            req = urllib.request.Request(url, headers=hdr)
            page = urllib.request.urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')

            with open(filename, "w") as file:
                file.write(str(soup))
            #input('enter')
            count += 1
            print (f'FDIC gathering: completed {count} out of {len(doc_links)}')


def clean_up_txt():
    clean_source_dir_name = 'fdic_letters/clean/'
    if not os.path.exists(clean_source_dir_name):
        os.makedirs(clean_source_dir_name)
    txtdir = 'fdic_letters/text/'
    if not os.path.exists(txtdir):
        os.makedirs(txtdir)

    source_dir = 'fdic_letters/'
    x = os.listdir(source_dir)
    count = 0
    for i in x:
        if i.endswith('.html') and (i.endswith('_clean.html') == False):
            fname = source_dir + i
            with open(fname, 'rb') as f:
                contents = f.read()
            soup = BeautifulSoup(contents, 'html.parser')
            c = soup.find('div', {'id': 'content'})
            d = soup.find_all('h2') + soup.find_all('h1') + soup.find_all('img')
            for j in d:
                j.decompose()

            e = soup.find_all('a')
            for k in e:
                stop_list = ['[Table of Contents]', '[Previous Page]', '[Next Page]', '[Search]']
                for word in stop_list:
                    if word in k.text:
                        k.decompose()

            try:
                letter_name = i.replace('.html', '')
                out_name = clean_source_dir_name + letter_name + '_clean.html'
                with open(out_name, "w") as file:
                    file.write(str(c))
                txt_name = txtdir + letter_name + '.txt'
                with open(txt_name, "w") as file:
                    file.write(c.text)
            except Exception as e:
                print (c)
                print (str(e))
                print (i)
                input('enter')

        print (f'FDIC clean up text: {count} out of {len(x)} -- {i}')
        count +=1

def run_fdic():
    if not os.path.exists('fdic_letters/'):
        os.makedirs('fdic_letters/')
    fdic_letter_links()
    download_letters()
    clean_up_txt()

if __name__ == "__main__":

    run_fdic()





