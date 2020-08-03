import os


cwd = os.getcwd()
agency = 'occ'
txtdir = cwd + f'/../scraping/{agency}_letters/text/'
clean_dir = cwd + f'/../scraping/{agency}_letters/clean/'
print (txtdir)
files = os.listdir(txtdir)
clean_files = os.listdir(clean_dir)
doc_contents = []
txt_names = []
doc_names = []
filenames = []
print (clean_files)
for i in files:
    fname = txtdir + i
    j = i.replace('.txt','')
    doc_name = next((s for s in clean_files if j in s), None)

