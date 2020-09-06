# -*- coding: utf-8 -*-
from django.shortcuts import render
import pickle
from django.http import FileResponse, Http404
import os.path
from django.shortcuts import redirect
import urllib
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from collections import defaultdict

feature_names = {}
tfidf_matrix = {}
doc_names = {}
filenames = {}
doc_contents = {}

for source in ['occ', 'fdic', 'frb']:

    p_file = f'reglist/pickle/{source}_feature_names.pickle'
    with open(p_file, 'rb') as handle:
        feature_names[source] = pickle.load(handle)

    p_file = f'reglist/pickle/{source}_tfidf_matrix.pickle'
    with open(p_file, 'rb') as handle:
        tfidf_matrix[source] = pickle.load(handle)

    p_file = f'reglist/pickle/{source}_doc_names.pickle'
    with open(p_file, 'rb') as handle:
        doc_names[source] = pickle.load(handle)

    p_file = f'reglist/pickle/{source}_filenames.pickle'
    with open(p_file, 'rb') as handle:
        filenames[source] = pickle.load(handle)

    p_file = f'reglist/pickle/{source}_doc_contents.pickle'
    with open(p_file, 'rb') as handle:
        doc_contents[source] = pickle.load(handle)

def index(request):
    print ('Views: inside index')
    if request.method == 'POST':
        form = request.POST
        print (form)
        search_terms = form['search_terms_val']
        a = form.getlist('Agencies')
        sources = ''.join(a).lower()
        x = 'query/' + sources + '/' + urllib.parse.quote(search_terms)
        print (f'url: {x}')
        response = redirect(x)
        return response
    else:
        print ('didnt post')
    return render(request, 'reglist/index.html')

def results(request, sources, search_terms):

    print ('inside results function')
    print ('request.method: ', request.method)

    if request.method == 'POST':
        form = request.POST
        print (form)
        search_terms = form['search_terms_val']
        if search_terms == '':
            return redirect('index')
        print (f'posted: {search_terms}')
        a = form.getlist('Agencies')
        sources = ''.join(a).lower()
        if sources == '':
            sources = 'occfrbfdic'
        x = '../../' + sources + '/' + urllib.parse.quote(search_terms)
        print (f'url: {x}')
        print ('heres a post')
        return redirect(x)

    if 'occ' in sources:
        df1 = get_results('occ', search_terms)
    if 'fdic' in sources:
        df2 = get_results('fdic', search_terms)
    if 'frb' in sources:
        df3 = get_results('frb', search_terms)
    results_list = pd.concat([df1,df2,df3])
    r = results_list.sort_values(by='doc_score', ascending=False)

    page_num = 0
    r = r[(page_num * 25):((page_num + 1) * 25)]
    full_r = []
    for j, i in r.iterrows():
        # [search term score / doc number / docname / filename / agency / feature_found]
        agency = i['agency']
        doc_num = i['doc_num']
        doc_score = round(i['doc_score'],2)
        doc_name = i['doc_name']
        filename = i['filename']
        max_term = i['max_term']
        doc = doc_contents[agency][doc_num]
        x = doc.find(max_term)
        y = len(max_term)
        d = doc[max(0, (x - 100)): (x + y + 50)]
        excerpt = d[d.find(' '):d.rfind(' ')]
        excerpt = excerpt.replace('\n', ' ')
        k = [doc_score, doc_num, doc_name, filename, agency, max_term, excerpt]
        full_r.append(k)

    context = {'search_terms': search_terms,
                'results': full_r,
                'sources': sources}
    response = render(request, 'reglist/results.html', context)
    print (f'returning response {sources}')

    return response


def generate_ngrams(s, n):
    # Convert to lowercases
    s = s.lower()
    # Break sentence in the token, remove empty tokens
    tokens = [token for token in s.split(" ") if token != ""]
    # Use the zip function to generate n-grams
    # Concatenate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]



def get_results(agency, search_terms):
    print (agency)
    df = pd.DataFrame([])
    # need to include the following info:
    # [search score / item number / docname / filename / agency / feature_found]
    df['doc_num'] = range(0, len(doc_names[agency]))
    df['filename'] = filenames[agency]
    df['doc_name'] = doc_names[agency]
    df['agency'] = agency

    # adding 'AND' functionality
    bool_search = search_terms.split('AND')
    print (bool_search)
    term_cols = []
    b = [[] for i in bool_search]
    term_list = []
    bool_count = 0
    for q in bool_search:
        q = q.strip()
        try_features = generate_ngrams(q, 1)
        try_features = try_features + generate_ngrams(q, 2)
        try_features = try_features + generate_ngrams(q, 3)
        print (try_features)
        for try_feature in try_features:
            try:
                i = feature_names[agency].index(try_feature)
                x = tfidf_matrix[agency].getcol(i)
                x = x.toarray().flatten()
                df[try_feature] = x
                b[bool_count].append(try_feature)
                term_list.append(try_feature)
            except Exception as e:
                print (str(e))
        bool_count +=1

    # calculate doc_scores based on sum of boolean search sets
    # for example, 'cryptocurrency custody' should return a letter that has
    # both those terms, not just a letter that has a strong score for one
    bool_sums_cols = []
    for b_count in range(0, bool_count):
        n = 'sum_of_bool_count_' + str(b_count)
        df[n] = df[b[b_count]].sum(axis=1)
        bool_sums_cols.append(n)
    for b_col in bool_sums_cols:
        df = df[df[b_col] > 0]
    # take the naive sum between the booleans.
    df['doc_score'] = df[bool_sums_cols].sum(axis=1)
    df['max_term'] = df[term_list].idxmax(axis=1)
    print (df.sort_values(by='doc_score', ascending = False))

    return df


def show_file(request, filename):

    print (filename)

    if filename.endswith('.pdf'):
        try:
            fname = 'reglist/static/' + filename
            print (os.path.isfile(fname))
            return FileResponse(open(fname, 'rb'), content_type='application/pdf')

        except FileNotFoundError:
            print ('file not found')
            raise Http404()

    if filename.startswith('FDIC'):
        fname = 'fdic_letters/' + filename  # this also needs to include fdic/
        print (os.path.isfile(fname))
        return render(None, 'reglist/letter.html', {'template_name': fname})

    if filename.endswith('.html'):
        fname = 'frb_letters/' + filename  # this also needs to include fdic/
        print (os.path.isfile(fname))
        return render(None, 'reglist/letter.html', {'template_name': fname})



if __name__ == "__main__":
    print ('\n\n\n')
    print ('hello')
    search_terms = 'cryptocurrency custody'
    sources = 'occfrbfdic'

    if 'occ' in sources:
        df1 = get_results('occ', search_terms)
    if 'fdic' in sources:
        df2 = get_results('fdic', search_terms)
    if 'frb' in sources:
        df3 = get_results('frb', search_terms)
    results_list = pd.concat([df1,df2,df3])
    r = results_list.sort_values(by='doc_score', ascending=False)

    page_num = 0
    r = r[(page_num*25):((page_num+1) * 25)]
    full_r = []
    for j, i in r.iterrows():
        # [search term score / doc number / docname / filename / agency / feature_found]
        agency = i['agency']
        doc_num = i['doc_num']
        doc_score = i['doc_score']
        doc_name = i['doc_name']
        filename = i['filename']
        max_term = i['max_term']
        doc = doc_contents[agency][doc_num]
        x = doc.find(max_term)
        y = len(max_term)
        d = doc[max(0, (x - 100)): (x + y + 50)]
        excerpt = d[d.find(' '):d.rfind(' ')]
        excerpt = excerpt.replace('\n', ' ')
        k = [doc_score, doc_num, doc_name, filename, agency, max_term, excerpt]
        full_r.append(k)

    #print (full_r)
    '''
    context = {'search_terms': search_terms,
               'results': full_r,
               'sources': sources}
    response = render(request, 'reglist/results.html', context)
    print (f'returning response {sources}')'''