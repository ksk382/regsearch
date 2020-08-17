from frb_letters import run_frb
from fdic_letters import run_fdic
from occ_letters import run_occ
from convert_to_text import run_text_conversion
from distutils.dir_util import copy_tree
import os

# test comment

def move_clean_files():
    cwd = os.getcwd()
    agencies = ['frb', 'fdic']
    for i in agencies:
        src_folder = cwd + f'/{i}_letters/clean/'
        dst_folder = cwd + f'/../reglist/templates/{i}_letters'
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)
        copy_tree(src_folder, dst_folder)

    src_folder = cwd + '/occ_letters/clean/'
    dst_folder = cwd + '/../reglist/static/'
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    copy_tree(src_folder, dst_folder)

    return

if __name__ == '__main__':

    # each function grabs the source documents
    #run_occ()
    #run_frb()
    #run_fdic()

    # convert all clean docs to text files
    #error_list = run_text_conversion()

    # put the clean files into the Django templates folder
    move_clean_files()
    print ('Main Scrape Complete')