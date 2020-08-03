# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import random
import numpy as np
import os
import time
import sys

def flatten():
    cwd = os.getcwd()
    txtdir = cwd + '/fdic_letters'
    print (txtdir)
    files = os.listdir(txtdir)
    doc_contents = []
    txt_names = []
    doc_names = []
    filenames = []
    for i in files:
        if i.endswith('.txt'):
            fname = txtdir + '/' + i
            with open(fname, 'rb') as f:
                contents = f.read()
            try:
                contents = contents.decode('utf-8')
                txt_names.append(i)
                doc_names.append(i.replace('.txt', ''))
                html_path_name = '../../../files/' + i.replace('.txt', '_clean.html')
                filenames.append(html_path_name)
                doc_contents.append(contents)
                f.close()
            except Exception as e:
                print (f'Didnt work: {i} {str(e)}')
    return doc_contents, txt_names, doc_names, filenames


start_time = time.time()
print (start_time)
doc_contents, txt_names, doc_names, filenames = flatten()



print ('length of contents: ', len(doc_contents))
print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()

with open('../reglist/pickle/txt_names_fdic.pickle', 'wb') as handle:
    pickle.dump(txt_names, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../reglist/pickle/filenames_fdic.pickle', 'wb') as handle:
    pickle.dump(filenames, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../reglist/pickle/doc_names_fdic.pickle', 'wb') as handle:
    pickle.dump(doc_names, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../reglist/pickle/doc_contents_fdic.pickle', 'wb') as handle:
    pickle.dump(doc_contents, handle, protocol=pickle.HIGHEST_PROTOCOL)

#sys.exit()
input('enter')

tf = TfidfVectorizer(analyzer='word',
                     ngram_range=(1,3),
                     min_df = 0,
                     stop_words = 'english',
                     token_pattern=r'\S+',
                     lowercase = True)
print ('Vectorizer complete')
print("--- %s seconds ---" % (time.time() - start_time))

tfidf_matrix =  tf.fit_transform(doc_contents)
print ('Fit_transform complete')
print("--- %s seconds ---" % (time.time() - start_time))

feature_names = tf.get_feature_names()
print ('Length of feature names: ', len(feature_names))

print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
#--- 26.7841911316 seconds ---



print ('pickling...\n\n')

with open('../reglist/pickle/feature_names_fdic.pickle', 'wb') as handle:
    pickle.dump(feature_names, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../reglist/pickle/tfidf_matrix_fdic.pickle', 'wb') as handle:
    pickle.dump(tfidf_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()

while True:
    s = random.sample(feature_names, 10)
    print (s)
    input('enter')