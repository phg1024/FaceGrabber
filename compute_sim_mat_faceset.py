import sys
import os
from os import listdir
from os.path import isfile, join
import json
from subprocess import call

import urllib2
import urllib
import time

from facepp.facepp_api.facepp import API

imgpath = sys.argv[1]
jsons = [f for f in listdir(imgpath) if isfile(join(imgpath, f)) and f.endswith('.json')]
#print jsons

all_tokens = []
for json_i in jsons:
    #print json_i
    with open(join(imgpath, json_i)) as file_i:
        data_i = json.load(file_i)
        #print data_i
        if data_i['faces']:
            all_tokens.append(data_i['faces'][0]['face_token'])
        else:
            all_tokens.append(None)

print all_tokens

if True:
    key = "oyBJwdTTxOqRNFWDMLFenLNz3jtSrA60"
    secret = "8HefWg9VUexp6xaccA8AdlQGJ9eimZlD"

    api = API(key, secret)

    import numpy as np
    N = len(all_tokens)
    print N
    sim_mat = np.zeros((N, N))
    for i, token_i in enumerate(all_tokens):
        sim_mat[i][i] = 1
        for j in range(i+1,N):
            token_j = all_tokens[j]
            if token_i and token_j:
                res_ij = api.compare(face_token1=token_i, face_token2=token_j)
                print res_ij['confidence']
                sim_mat[i][j] = res_ij['confidence']
                sim_mat[j][i] = res_ij['confidence']
            else:
                sim_mat[i][j] = -1
                sim_mat[j][i] = -1

    np.save('simmat.mat', sim_mat)
else:
    pass

import matplotlib.pyplot as plt
plt.imshow(sim_mat)
plt.colorbar()
plt.show()
