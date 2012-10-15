#!/usr/bin/python
import os
import itertools
from os.path import exists
import os.path
import pickle
import re
import sys
import urllib
import time
from random import randrange

# The script will request Hacker News items.  Starting randomly,it
# will request item after item in order of their index.  After
# reaching max_item, the script will loop back to item 1.
# Every item will be requested at most once.
max_item = 500000
start_item = randrange(1, max_item)

# Directory, where the requested pages are stored.
cache_dir = 'pages'

res = "res.working"

# My proxy at work blocks too many requests to the same site in short
# time.  (Or is it Hacker News that's blocking spidering directly and
# the proxy only relays the block?)
#
# Anyway, after the first unsuccessful download, we'll wait for
# (init_timeout) seconds before trying again.  Each subsequent failure
# will wait exponentially longer (increase_factor).
init_timeout = 5
increase_factor = 2

# As a special safeguard, we even wait between successful downloads.
# The inter_timeout_increase will be added after each failure.
inter_timeout = 0.3
inter_timeout_increase = 0.05

id_chunk = re.compile(r'<a href="item\?id=[0-9]+">link</a>')
number = re.compile(r'[0-9]+')

comment = re.compile(r'<span class="comment">.*?</span>')

score = re.compile('<span id=score_[0-9]+>[0-9]+ points?</span>')

proxyBlock = re.compile("(konnte nicht geholt werden)|(Es konnte keine Verbindung zum Host hergestellt werden)")

def markDown (s):
    """Removes HTML-Tags from its argument."""
    return re.sub('<.*?>','', s)

def get_id (item):
    # ToDo: Why two = ?
    idSs = idS = id_chunk.findall(item)
    if len(idSs):
        idS = idSs[0]
        id = number.findall(idS)[0]
        return int(id)
    else:
        return None
    
def get_score (item):
    ss = score.findall(item)
    if len(ss):
        return int(number.findall(markDown(ss[0]))[0])

def get_length(item):
    cs = comment.findall(item)
    if len(cs):
        c = cs[0]
        #strip tags
        nc = re.sub('<.*?>','', c)
#        print "nc:", nc
        return len(nc)
    else:
#        print "Did not find length."
#        print item
#        sys.exit(1)
        return None

from exceptions import *

class ProxyError (Exception):
    def __init__(self, url, chunk):
        self.url = url
        self.chunk = chunk
    def __repr__(self):
        return "ProxyError - "+ str(url) + ":\n" + str(chunk) + "\n"

def extract(s):
    """Returns all comments as {id: (length, score)}"""
    items = s.split('<span class="comhead">')[1:]
    d = {}
    for item in items:
        try:
            l = get_length(item)
            id = get_id(item)
            s = get_score(item)
            if id is not None and l is not None and s is not None:
                d[id] = (l,s)
        except KeyboardInterrupt:
            raise
        except:
            raise
    return d

last = None

def tryRemove(fName):
    """Tries to remove a file, but fails silently."""
    try:
        os.remove(fName)
    except OSError, e:
        print e

def get(id):
    global last, inter_timeout
    fName = "pages/item?id="+str(id)
    url = "http://news.ycombinator.com/item?id=" + str(id)
    if not exists(fName):
        print "downloading", url
        gotten = False
        timeout = init_timeout
        while not gotten:
            f = urllib.urlopen(url)
            s = f.read()
            f.close()
            time.sleep(inter_timeout)
            
            if len(proxyBlock.findall(s)) > 0:
                print "Proxy blocked:"
                print s
                print "Timeout:", timeout
                inter_timeout += inter_timeout_increase
                print "inter_timeout increased to", inter_timeout
                time.sleep(timeout)
                # exponential increase in timeout
                timeout = timeout * increase_factor
            else:
                try:
                    file(fName, 'w').write(s)
                except:
                    # Does Python write files atomically?  I do not
                    # know, so we delete the possible half-written
                    # file in case of an expection.
                    tryRemove(fName)     
                    raise
                gotten = True
    else:
        s = file(fName, 'r').read()
    return s



def getCached (cache_dir):
    """Reads in previously downloaded pages, from the cache directory."""
    store = {}
    print "Starting to read in previously downloaded pages: "
    for f in os.listdir(cache_dir):
        sys.stdout.write('.')
        store.update(extract (file(os.path.join(cache_dir,f), 'r').read()))
    print "Finished reading in previously downloaded pages."
    return store
        

def init ():
    return (getCached(cache_dir), start_item)

def main():
    """Read in cached pages; get new pages until user aboards with
    Ctrl-C, then write out the results"""
    store, next = init()

    try:
        for j in itertools.count(next):
            i = ((j-1) % max_item) + 1
            print "working on item:", i
            if i % 10 == 0:
                print
            if i in store:
                pass
#                print "in store"
            else:
                n = extract(get(i))
#                print "new:", n
                store.update(n)
                next = i
    except KeyboardInterrupt:
        pass
    except ProxyError:
        pass

    pickle.dump((store, next, inter_timeout), file(res, 'w'))
#    print next
#    print "store:", store
    print "inter_timeout:", inter_timeout



if __name__ == "__main__":
    main ()
