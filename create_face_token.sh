#!/bin/bash
curl -X POST "https://api-us.faceplusplus.com/facepp/v3/detect" \
-F "api_key=oyBJwdTTxOqRNFWDMLFenLNz3jtSrA60" \
-F "api_secret=8HefWg9VUexp6xaccA8AdlQGJ9eimZlD" \
-F "image_file=@$1"
