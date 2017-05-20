MY_PATH="`dirname $0`"
MY_PATH="`(cd \"$MY_PATH\" && pwd)`"

image_directory=$1
person_name=$2
need_crop=$3

if [ "$need_crop" -eq "1" ]; then
  ### Creating image list
  python $MY_PATH/create_image_list.py $image_directory/$person_name $image_directory/$person_name/image_list.txt

  ### Detect faces in images
  /usr/bin/python $MY_PATH/face_detector.py $image_directory/$person_name/image_list.txt

  ### Crop face images
  python $MY_PATH/cut_images_with_box.py $image_directory/$person_name/image_list.txt
fi

### Creating image list
python $MY_PATH/create_image_list.py $image_directory/$person_name/crop $image_directory/$person_name/crop/image_list.txt

### Mask faces in the cropped images
/usr/bin/python $MY_PATH/initialize_masks.py $image_directory/$person_name/crop/image_list.txt
