#!/bin/bash
curl -X POST "https://api-us.faceplusplus.com/facepp/v3/search" \
-F "api_key=oyBJwdTTxOqRNFWDMLFenLNz3jtSrA60" \
-F "api_secret=8HefWg9VUexp6xaccA8AdlQGJ9eimZlD" \
-F "face_token=$1" \
-F "outer_id=$2"
