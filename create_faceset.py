import sys
import os
from os import listdir
from os.path import isfile, join
import json
from subprocess import call

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

print all_tokens

print ' '.join(['curl', '-X', 'POST', '"https://api-us.faceplusplus.com/facepp/v3/faceset/create"',
'-F', '"api_key=oyBJwdTTxOqRNFWDMLFenLNz3jtSrA60"',
'-F', '"api_secret=8HefWg9VUexp6xaccA8AdlQGJ9eimZlD"',
'-F', '"outer_id=obamafamily"',
'-F', '"tag=person,male"',
'-F', '"face_tokens=%s"' % all_tokens[0]])

for token_i in all_tokens[1:]:
    print ' '.join(['curl', '-X', 'POST', '"https://api-us.faceplusplus.com/facepp/v3/faceset/addface"',
    '-F', '"api_key=oyBJwdTTxOqRNFWDMLFenLNz3jtSrA60"',
    '-F', '"api_secret=8HefWg9VUexp6xaccA8AdlQGJ9eimZlD"',
    '-F', '"outer_id=obamafamily"',
    '-F', '"face_tokens=%s"' % token_i])
