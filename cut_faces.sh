MY_PATH="`dirname $0`"
MY_PATH="`(cd \"$MY_PATH\" && pwd)`"

image_directory=$1
person_name=$2
strict_mode=$3

### Creating image list
python $MY_PATH/create_image_list.py $image_directory/$person_name $image_directory/$person_name/image_list.txt

### Detect faces in images
python $MY_PATH/face_detector.py $image_directory/$person_name/image_list.txt

### Crop face images
python $MY_PATH/cut_images.py $image_directory/$person_name/image_list.txt
