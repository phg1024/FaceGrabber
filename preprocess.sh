image_directory=$1
person_name=$2
strict_mode=$3

### Creating image list
python create_image_list.py $image_directory $person_name.txt

### Detect faces in images
/usr/bin/python face_detector.py $person_name.txt

### Cut faces
./cut_faces.sh $image_directory

### Create image list for cropped images
python create_image_list.py $1/crop "$person_name"_crop.txt

exit 0

### Generate face embedding
python gen_rep.py `cat "$person_name"_crop.txt` --output_file "$person_name"_reps.txt

### Classify faces
if [ "$strict_mode" == "yes" ]; then
  python classify_faces.py "$person_name"_reps.txt --method total_variance --threshold 10
else
  python classify_faces.py "$person_name"_reps.txt --method total_variance --threshold 50
fi
