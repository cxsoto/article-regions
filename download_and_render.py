#!/usr/bin/env python
#
# This (Linux-specific) script downloads the PDF files for article IDs listed
# in pmc_ids.txt from PubMed Central servers in the US or in Europe. Then it
# renders those PDFs to sets of JPG images (one per page) using the
# ImageMagick package. Finally, the image files are renamed for consistency.
#
# Some checks are included for server acessibility, tool availability, and
# PDF-reading policy.
#
# Carlos X. Soto, csoto@bnl.gov


from __future__ import print_function

import os
import time
import requests

pdf_dir = 'pdfs'
img_dir = 'imgs'

pmcid_file = 'pmc_ids.txt'
pmcids = open(pmcid_file,'r').read().splitlines()
print('{} article IDs in {}'.format(len(pmcids), pmcid_file))

url_pref = 'https://www.ncbi.nlm.nih.gov/pmc/articles/'
url_post = '/pdf'

#### Switch to European servers are US servers are inaccessible
print('Checking PubMed Central servers...')
if requests.get(url_pref + pmcids[0]).status_code != 200:
    print('Failed to connect to US NIH servers. Trying European servers...')
    url_pref = 'https://europepmc.org/articles/'
    url_post = '?pdf=render'
    if requests.get(url_pref + pmcids[0]).status_code != 200:
        print('Failed again. Exiting...')
        exit(1)
    print('...using European server.')
else:
    print('...using US server.')
        
#### Check that required tools are installed
print('Checking installed tools...')
tools = ['curl', 'pdfinfo', 'convert']
pkgs = ['curl', 'poppler-utils', 'imagemagick']
missing = []
missing_pkgs = []
for i, t in enumerate(tools):
    if os.system('which {} &> /dev/null'.format(t)):
        missing.append(t)
        missing_pkgs.append(pkgs[i])
if missing:
    print('Cannot proceed, missing tools: ' + ', '.join(missing))
    print('To install, run: sudo apt install ' + ' '.join(missing_pkgs))
    exit(1)
print('...tools ok.')

#### Check PDF-read permissions for ImageMagick package
print('Checking PDF permissions for ImageMagick...')
if os.system('grep \'rights=".*read.*" pattern="PDF"\' /etc/ImageMagick-6/policy.xml &> /dev/null'.format(t)):
    print('Cannot proceed, ImageMagick policy does not allow reading PDF files...')
    print('To fix, open the file /etc/ImageMagick-6/policy.xml and replace the line')
    print('\t<policy domain="coder" rights="none" pattern="PDF" />\nwith')
    print('\t<policy domain="coder" rights="read|write" pattern="PDF" />')
    exit(1)
print('...permissions ok.')
    
#### Download article PDFs (from NIH or EuropePMC servers)
if not os.path.isdir(pdf_dir):
    os.mkdir(pdf_dir)

for id in pmcids:
    dest = '{}/{}.pdf'.format(pdf_dir, id)
    if not os.path.isfile(dest):
        source = url_pref + id + url_post
        print('Downloading {} ...'.format(source), end = ' ', flush = True)
        error = os.system('curl -o {} -L {} &> /dev/null'.format(dest, source))
        if error:
            print('FAILED')
        else:
            print('{}KB'.format(os.stat(dest).st_size // 1024))
        time.sleep(3)
    # check if PDF files are intact
    error = os.system('pdfinfo {} &> /dev/null'.format(dest))
    if error:
        print('ERROR: PDF file {} appears to be broken.'.format(dest))

#### Render PDFs to sets of 72dpi (ImageMagick default) JPEG images
if not os.path.isdir(img_dir):
    os.mkdir(img_dir)
    
pdf_files = [f for f in sorted(os.listdir(pdf_dir)) if f.endswith('.pdf')]

for p in pdf_files:
    print('Rendering {} ...'.format(p), end = ' ', flush = True)
    if os.path.isfile('{}/{}-0.jpg'.format(img_dir, p[:-4])):
        continue
    error = os.system('convert {}/{} -colorspace sRGB {}/{}jpg &> /dev/null'.format(pdf_dir, p, img_dir, p[:-3]))
    if error:
        print('FAILED')
    else:
        print('done')
        
#### Rename image files to include number of article pages
all_imgs = [f[:-4].split('-') for f in sorted(os.listdir(img_dir)) if f.endswith('.jpg')]
articles = sorted(list(set([i[0] for i in all_imgs])))

for a in articles:
    print('Renaming image files for {} ...'.format(a), end = ' ', flush = True)
    a_imgs = [i for i in all_imgs if i[0] == a]
    for i in a_imgs:
        if len(a_imgs) == 1:     # handle single-page articles
            os.rename('{}/{}.jpg'.format(img_dir, i[0]), '{}/{}-01-00.jpg'.format(img_dir, i[0]))
            continue
        orig_name = '{}-{}.jpg'.format(i[0], i[1])
        new_name = '{:s}-{:02d}-{:02d}.jpg'.format(i[0], len(a_imgs), int(i[1]))
        os.rename('{}/{}'.format(img_dir, orig_name), '{}/{}'.format(img_dir, new_name))
    print('({} pages)'.format(len(a_imgs)))

print('Done processing articles.')