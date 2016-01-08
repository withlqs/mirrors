#!/usr/bin/python
from string import rfind
from time import mktime, strptime
from os import makedirs, path, stat, utime
from urllib import urlretrieve, urlopen
from xml.etree import ElementTree
import os

base_url = 'https://dl.google.com/android/repository/'
base_url2 = 'https://dl-ssl.google.com/android/repository/'
out_dir = '/data/mirrors/android/repository'

download_url = ''

def download(filename, last_modified):
   file = out_dir + filename
   print 'Downloading ' + filename
   #urlretrieve(base_url + filename, file)
   os.system('wget -c -t 0 -O '+file+' '+download_url+filename)
   utime(file, (last_modified, last_modified))

   process(filename)

def process(filename, size=-1):
   file = out_dir + filename
   if path.isfile(file) and stat(file).st_size == size:
      print 'Skipping: ' + filename
      return

   print 'Processing: ' + filename
   handle = urlopen(download_url + filename)
   headers = handle.info()
   content_length = int(headers.getheader('Content-Length'))
   last_modified = mktime(strptime(headers.getheader('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z'))

   if rfind(filename, '/') > 0:
      dir = out_dir + filename[:rfind(filename, '/')]
   else:
      dir = out_dir

   if not path.isdir(dir):
      print 'Creating ' + dir
      makedirs(dir)

   if not path.isfile(file):
      download(filename, last_modified)
   else:
      file_stat = stat(file)
      if file_stat.st_mtime != last_modified or file_stat.st_size != content_length:
         download(filename, last_modified)
      else:
         print 'Skipping: ' + filename

def fetch(file):
   global download_url
   print 'file: '+file

   if base_url in file:
      dir = file[len(base_url) - 1:rfind(file, '/') + 1]
      file = file[rfind(file, '/') + 1:]
      download_url = base_url
   elif 'http' in file:
      dir = file[len(base_url2) - 1:rfind(file, '/') + 1]
      file = file[rfind(file, '/') + 1:]
      download_url = base_url2
   else:
      dir = '/'
      download_url = base_url

   print 'dir: '+dir
   print 'file: '+file
   print 'download_url: '+download_url

   process(dir + file)
   base_dir = path.dirname(dir + file)
   if base_dir != '/':
      base_dir += '/'
   tree = ElementTree.parse(out_dir + dir + file)
   for element in tree.getiterator():
      if element.tag.split('}')[1] == 'url':
         if element.text[-4:] != '.xml':
            if not 'http' in element.text:
               process(base_dir + element.text)
         else:
            fetch(element.text)
for file in ['repository-10.xml', 'addons_list-2.xml']:
   fetch(file)
