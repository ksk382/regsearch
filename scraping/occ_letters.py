from bs4 import BeautifulSoup
import urllib.request, json, getopt
from pathlib import Path
import requests
import os
import pickle
from selenium import webdriver

def get_month_links():

    # https://occ.gov/topics/charters-and-licensing/interpretations-and-actions/1996/index-interpretations-and-actions-1996.html
    base_site = 'https://occ.gov/topics/charters-and-licensing/interpretations-and-actions/'
    month_links = []
    chromeOptions = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images': 2}
    chromeOptions.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chromeOptions)

    for i in range (1996, 2021):
        year = str(i)
        year_site = base_site + year + '/index-interpretations-and-actions-' + year + '.html'
        print (year_site)

        # get all the month links
        # For OCC, normal urllib request times out w/ SSL exchange. Use Selenium
        #hdr = {'User-Agent': 'Mozilla/5.0'}
        #req = urllib.request.Request(year_site, headers=hdr)
        #page = urllib.request.urlopen(req)

        driver.get(year_site)
        page = driver.execute_script("return document.body.innerHTML")

        print ('page got')
        soup = BeautifulSoup(page, 'html.parser')
        print ('page parsed')

        for link in soup.findAll('a'):
            j = link.get('href')
            # https://occ.gov/topics/charters-and-licensing/interpretations-and-actions/1996/interpretations-and-actions-dec-1996.html
            if ('/topics/charters-and-licensing/interpretations-and-actions/' + year + '/interpretations') in str(j):
                complete_link = 'https://www.occ.treas.gov' + j
                month_links.append(complete_link)
                print (complete_link)

    driver.quit()

    print (month_links)
    return month_links


def get_pdf_links(month_links):

    pdf_link_set = []
    for x in month_links:

        hdr = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"}
        req = urllib.request.Request(x, headers=hdr)
        page = urllib.request.urlopen(req)
        #driver.get(year_site)
        #page = driver.execute_script("return document.body.innerHTML")

        soup = BeautifulSoup(page, 'html.parser')
        for link in soup.findAll('a'):
            j = link.get('href')
            if str(j).endswith('.pdf'):
                pdf_link = 'https://www.occ.treas.gov' + j
                if 'https://www.occ.treas.gov/topics/charters-and-licensing/interpretations-and-actions/' in pdf_link:
                    if pdf_link not in pdf_link_set:
                        print (pdf_link)
                        pdf_link_set.append(pdf_link)
    print ('pickling...')
    with open('occ_letters/occ_links.pickle', 'wb') as handle:
        pickle.dump(pdf_link_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return pdf_link_set

def download_pdfs():

    clean_dir = 'occ_letters/clean/'
    if not os.path.exists(clean_dir):
        os.makedirs(clean_dir)

    with open('occ_letters/occ_links.pickle', 'rb') as handle:
        pdf_link_set = pickle.load(handle)

    print (pdf_link_set)

    count = 0
    for x in pdf_link_set:
        count += 1
        url = x
        y = 'https://www.occ.treas.gov/topics/charters-and-licensing/interpretations-and-actions/'
        year = x.replace(y, '')[0:4]
        docname = x.replace((y + year + '/'), '')
        pname = clean_dir + docname
        filename = Path(pname)

        if os.path.isfile(filename):
            print (f'Aready had {docname}')
        else:
            try:
                response = requests.get(url)
                filename.write_bytes(response.content)
                print (pname)
            except Exception as e:
                print(e)
        print (f'{count} out of {len(pdf_link_set)} completed -- {x}')



def run_occ():
    if not os.path.exists('occ_letters/'):
        os.makedirs('occ_letters/')
        # find all links
    month_links = get_month_links()
    pdf_link_set = get_pdf_links(month_links)

    # download files for all links
    download_pdfs()

if __name__ == "__main__":

    run_occ_letters()


