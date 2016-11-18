for f in `ls $1`; do
	echo $f
	python visualize_points.py $1/$f/crop/settings.txt
done
