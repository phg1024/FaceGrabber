MY_PATH="`dirname $0`"
MY_PATH="`(cd \"$MY_PATH\" && pwd)`"

image_directory=$1
person_name=$2
strict_mode=$3

### Creating image list
python $MY_PATH/create_image_list.py $image_directory/$person_name $image_directory/$person_name/image_list.txt

### Copy the images to a renamed directory
rm -rf $image_directory/$person_name/renamed 
mkdir $image_directory/$person_name/renamed
python $MY_PATH/copy_index_images.py $image_directory/$person_name/image_list.txt $image_directory/$person_name/renamed
