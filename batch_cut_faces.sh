persons=`ls $1`

for p in $persons; do
  ./cut_faces.sh $1 $p
done
