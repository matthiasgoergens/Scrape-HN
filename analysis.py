#!/usr/bin/python
from math import *
import pickle

results = 'res.working'
data = 'lengthscore.data'

(store, next, inter_timeout) = pickle.load (file(results,'r'))

lengths = {}
scores = {}


d = file(data, 'w')
d.write('#length\tscore')
for (length, score) in store.values():
    d.write(str(length)+'\t'+str(score)+'\n')
    try:
        if length is not None:
            lengths[length] += 1
    except KeyError:
        lengths[length] = 1
    try:
        if score is not None:
            scores[score] += 1
    except:
        scores[score] = 1
d.close()

def stat(werte):
    print werte.keys()
    maxWert = max(werte.keys())
    minWert = min(werte.keys())
    for wert in range(minWert,maxWert+1):
        if wert == 0:
            print '<',
        print werte.get(wert, 0),
#        print str(wert)+': '+str( werte.get(wert, 0))+'\t',
        if wert == 0:
            print '>',
    print
    
#print lengths

#stat(scores)

#print
#stat(lengths)




