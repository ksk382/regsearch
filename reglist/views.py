# -*- coding: utf-8 -*-
from django.shortcuts import render
import pickle
from django.http import FileResponse, Http404
import os.path
from django.shortcuts import redirect
import urllib


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

# Create your views here.
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
        form = request.GET
        print ('didnt post')

    context = {'form': form}
    context.update(csrf(request))

    return render(request, 'reglist/index.html', context)

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


    search_terms = search_terms.lower()

    results_list = []
    if 'occ' in sources:
        results_list = results_list + get_results('occ', search_terms)
    if 'fdic' in sources:
        results_list = results_list + get_results('fdic', search_terms)
    if 'frb' in sources:
        results_list = results_list + get_results('frb', search_terms)


    r = sorted(results_list, key=lambda t: t[0] * -1)
    #print (r)
    r = r[:25]
    full_r = []
    for i in r:
        print (i)
        a = doc_contents[i[4]][i[1]]
        x = a.find(search_terms)
        d = a[max(0, (x - 100)): (x + len(search_terms) + 50)]
        excerpt = d[d.find(' '):d.rfind(' ')]
        print (excerpt)
        j = i + [excerpt]
        j[4] = i[4].upper()
        full_r.append(j)

    context = {'search_terms': search_terms,
                'results': full_r,
                'sources': sources}
    response = render(request, 'reglist/results.html', context)
    print (f'returning response {sources}')

    return response


def get_results(agency, search_terms):
    print (agency)
    try:
        i = feature_names[agency].index(search_terms)
    except:
        return []
    x = tfidf_matrix[agency].getcol(i)
    x = x.todense().tolist()
    # [score / item number / docname / filename / agency]
    l = [[round(pair[1][0], 2), pair[0], doc_names[agency][pair[0]], filenames[agency][pair[0]], agency] for pair in zip(range(0, len(x)), x) if pair[1][0] > 0]
    # sort by score
    r = sorted(l, key=lambda t: t[0] * -1)
    return r


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

