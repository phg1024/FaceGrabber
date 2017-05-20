#!/bin/bash
directory=$1

for f in `ls $directory`; do
  echo $f;
  ./create_face_token.sh $directory/$f > $directory/$f.json
done
