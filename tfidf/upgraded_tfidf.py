import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from html import unescape
import random
import re
import time


def flatten(agency):

    print ('flatten function...')

    cwd = os.getcwd()
    txtdir = cwd + f'/../scraping/{agency}_letters/text/'
    clean_dir = cwd + f'/../scraping/{agency}_letters/clean/'
    template_location = '../../../files/'

    files = os.listdir(txtdir)
    clean_files = os.listdir(clean_dir)
    doc_contents = []
    txt_names = []
    doc_names = []
    filenames = []
    for i in files:
        if not i.endswith('.txt'):
            continue
        fname = txtdir + i
        j = i.replace('.txt','')
        doc_name = next((s for s in clean_files if j in s), None)
        filepath = template_location + doc_name

        with open(fname, 'rb') as f:
            contents = f.read()
        try:
            txt_names.append(i)
            contents = contents.decode('utf-8')
            doc_names.append(doc_name)
            filenames.append(filepath)
            doc_contents.append(contents)
            f.close()
        except:
            print ('Didnt work: {0}'.format(i))
    print ('flatten function complete.')
    return doc_contents, txt_names, doc_names, filenames

def parent_parens(i):
    cites = []
    k = i
    for j in re.findall('\(', i):
        y = k.rfind('(')
        k = i[:y]
        cites.append(k)
    return cites

def get_cfr_numbers(text):

    cites = []
    x = re.findall('[0-9]+\.[0-9]+\S+', text)
    for i in x:
        while not (i[-1].isalnum() or i[-1] == ')'):
            i = i[:-1]
        cites.append(i.lower())
        # if it includes 9.18(b)(4)(iii)(B), also include 9.18, 9.18(b), 9.18(b)(4)...
        cites = cites + parent_parens(i)

    return cites

def get_usc_numbers(text):

    text = text.lower()

    cites = []

    # find U.S.C. with symbol sign
    x = re.findall('\d+ u\.s\.c\. \W \d+\(\S+', text)
    for i in x:
        i = i.replace('.', '')
        i = i.replace('§', '')
        i = i.replace('  ', ' ')
        c = [i] + parent_parens(i)
        cites = cites + c

    # find U.S.C. without symbol sign
    x = re.findall('\d+ u\.s\.c\. \d+\(\S+', text)
    for i in x:
        i = i.replace('.', '')
        i = i.replace('§', '')
        i = i.replace('  ', ' ')
        c = [i] + parent_parens(i)
        cites = cites + c

    # find USC with symbol sign
    x = re.findall('\d+ usc \W \d+\(\S+', text)
    for i in x:
        i = i.replace('.', '')
        i = i.replace('§', '')
        i = i.replace('  ', ' ')
        c = [i] + parent_parens(i)
        cites = cites + c

    # find USC without symbol sign
    x = re.findall('\d+ usc \d+\(\S+', text)
    for i in x:
        i = i.replace('.', '')
        i = i.replace('§', '')
        i = i.replace('  ', ' ')
        c = [i] + parent_parens(i)
        cites = cites + c

    components = []
    for i in cites:
        x = re.findall('\S+', i)
        for j in x:
            components.append(j)

    cites = cites + components

    x = re.findall('section \d+', text)
    for i in x:
        cites.append(i)

    return cites


def get_bespoke(text):
    cites = get_cfr_numbers(text)
    cites = cites + get_usc_numbers(text)
    return cites

# tokenize the doc and lemmatize its tokens
def my_tokenizer(text):
    tokens = nlp(text)
    clean_list = []
    for t in tokens:
        if keep_token(t):
            clean_list.append(t.lemma_)

    cites = get_bespoke(text)
    clean_list = clean_list + cites
    return clean_list

def keep_token(t):
    return ((t.is_alpha) and
            not (len(t.text) == 1 or t.is_space or t.is_punct or
                 t.is_stop or t.like_num))


# create a dataframe from a word matrix
def wm2df(wm, feat_names):
    # create an index for each row
    idx_names = ['doc{:d}'.format(idx) for idx, _ in enumerate(wm)]
    cols = feat_names
    df = pd.DataFrame(data=wm.toarray(), index=idx_names,
                      columns=cols)
    return (df)


def make_tokens(doc, nlp):
    doc_clean = doc.lower()
    tokens = nlp(doc_clean)
    clean_list = []
    for t in tokens:
        if keep_token(t):
            clean_list.append(t.lemma_)
    cites = get_bespoke(doc)
    clean_list = clean_list + cites

    return clean_list

def identity_tokenizer(text):
    return text

def run_tfidf(agency):

    print ('documents loading...')
    doc_contents, txt_names, doc_names, filenames = flatten(agency)

    print ('spacy loading...')
    spacy.load('en')
    nlp = spacy.lang.en.English()

    print ('tokenizing...')
    tokenized_corpus = []
    error_list = []
    count = 0
    for i in doc_contents:
        count +=1
        try:
            x = make_tokens(i, nlp)
        except Exception as e:
            print (f'failed to make tokens for {doc_contents.index(i)}')
            error_list.append([doc_contents.index(i), str(e)])
            x = []
        tokenized_corpus.append(x)
        if count % 100 == 0:
            print (f'{count} -- out of {len(doc_contents)}')

    print ('starting TF-IDF analysis...')

    start_time = time.time()
    tfidf = TfidfVectorizer(tokenizer=identity_tokenizer,
                            stop_words='english',
                            lowercase=False,
                            ngram_range=(1,3))

    tfidf_matrix = tfidf.fit_transform(tokenized_corpus)
    feature_names = tfidf.get_feature_names()

    print("--- %s seconds ---" % (time.time() - start_time))



    # so far, the data frame is too big to store
    #df = wm2df(tfidf_matrix, feature_names)

    #df['txt_name'] = txt_names
    #df['doc_name'] = doc_names
    #df['filename'] = filenames

    #print (df[['txt_name', 'doc_name', 'filename']])


    print ('pickling...\n\n')

    out_p = f'../reglist/pickle/{agency}_feature_names.pickle'
    with open(out_p, 'wb') as handle:
        pickle.dump(feature_names, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print (f'{out_p} done')

    out_p = f'../reglist/pickle/{agency}_tfidf_matrix.pickle'
    with open(out_p, 'wb') as handle:
        pickle.dump(tfidf_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print (f'{out_p} done')

    out_p = f'../reglist/pickle/{agency}_doc_contents.pickle'
    with open(out_p, 'wb') as handle:
        pickle.dump(doc_contents, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print (f'{out_p} done')

    out_p = f'../reglist/pickle/{agency}_txt_names.pickle'
    with open(out_p, 'wb') as handle:
        pickle.dump(txt_names, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print (f'{out_p} done')

    out_p = f'../reglist/pickle/{agency}_filenames.pickle'
    with open(out_p, 'wb') as handle:
        pickle.dump(filenames, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print (f'{out_p} done')

    out_p = f'../reglist/pickle/{agency}_doc_names.pickle'
    with open(out_p, 'wb') as handle:
        pickle.dump(doc_names, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print (f'{out_p} done')

    #print ('writing df to csv...')
    #df.to_csv(f'../reglist/pickle/{agency}_df.csv', sep='\t')

    print (f'done with {agency}')

    return

if __name__ == '__main__':

    agencies = ['occ', 'frb', 'fdic']
    for agency in agencies:
        run_tfidf(agency)