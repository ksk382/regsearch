# -*- coding: utf-8 -*-
import random
from bs4 import BeautifulSoup
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import io


def pdfparser(filename):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Process each page contained in the document.
    fp = open(filename, 'rb')
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    fp.close()
    device.close()
    text = retstr.getvalue()
    return text


def convert_to_txt(doc_dir, out_dir):
    files = os.listdir(doc_dir)
    # files = random.sample(files, 25)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    count = 0
    error_list = []
    for i in files:
        count += 1
        fname = doc_dir + i

        if i.endswith('.html'):
            try:

                txt_name = i.replace('.html', '.txt')
                txt_name = txt_name.replace('_clean', '')
                out_txt = out_dir + txt_name
                if os.path.exists(out_txt):
                    print (f'Done already {count} out of {len(files)} -- {txt_name}')
                    continue
                else:
                    # read the htm file
                    with open(fname, 'rb') as f:
                        page = f.read()
                    # parse the htm file
                    soup = BeautifulSoup(page, 'html.parser')
                    text = soup.text
                    # write the txt file
                    text_file = open(out_txt, 'w')
                    text_file.write(text)
                    text_file.close()
            except Exception as e:
                err_msg = f'{fname} -- {str(e)})'
                print (err_msg)
                error_list.append([fname, str(e)])

        if i.endswith('.pdf'):
            txt_name = i.replace('.pdf', '.txt')
            txt_name = txt_name.replace('_clean', '')
            out_txt = out_dir + txt_name
            if os.path.exists(out_txt):
                print (f'Done already {count} out of {len(files)} -- {txt_name}')
                continue
            else:
                # parse the pdf file
                try:
                    text = pdfparser(fname)
                    # write the txt file
                    text_file = open(out_txt, 'w')
                    text_file.write(text)
                    text_file.close()
                except Exception as e:
                    err_msg = f'{fname} -- {str(e)})'
                    print (err_msg)
                    error_list.append([fname, str(e)])


        print (f'completed {count} out of {len(files)} -- {txt_name}')
    return error_list

def remove_weirdos(doc_dir):
    files = os.listdir(doc_dir)
    a = []
    for i in files:
        if i.endswith('txt') and (i.endswith('.txt') == False):
            fname = doc_dir + '/' + i
            print (i)
            os.remove(fname)
    return


def run_text_conversion():
    cwd = os.getcwd()
    doc_dirs = ['frb_letters/', 'fdic_letters/','occ_letters/']
    doc_dirs = ['occ_letters/']
    total_error_list = []
    for dir in doc_dirs:
        out_dir = cwd + '/' + dir + 'text/'
        doc_dir = cwd + '/' + dir + 'clean/'
        print (doc_dir)
        error_list = convert_to_txt(doc_dir, out_dir)
        total_error_list = total_error_list + error_list
        #remove_weirdos(doc_dir)

    return total_error_list


if __name__ == '__main__':
    run_text_conversion()
