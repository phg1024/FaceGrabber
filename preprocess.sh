image_directory=$1
person_name=$2

### Creating image list
python create_image_list.py $image_directory $person_name.txt

### Detect faces in images
python face_detector.py $person_name.txt

### Crop face images
python crop_images.py $person_name.txt

### Create image list for cropped images
python create_image_list.py $1crop "$person_name"_crop.txt

### Generate face embedding
python gen_rep.py `cat "$person_name"_crop.txt` --output_file "$person_name"_reps.txt

### Classify faces
python classify_faces.py "$person_name"_reps.txt --method greedy --threshold 0.9
