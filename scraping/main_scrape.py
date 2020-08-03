from frb_letters import run_frb
from fdic_letters import run_fdic
from occ_letters import run_occ
from convert_to_text import run_text_conversion
from distutils.dir_util import copy_tree

def move_clean_files():
    cwd = os.getcwd()
    agencies = ['occ', 'frb', 'fdic']
    for i in agencies:
        src_folder = cwd + f'{i}_letters/clean/'
        dst_folder =

    return

if __name__ == '__main__':

    # each function grabs the source documents
    run_occ()
    run_frb()
    run_fdic()

    # convert all clean docs to text files
    error_list = run_text_conversion()

    # put the clean files into the Django templates folder
    move_clean_files()