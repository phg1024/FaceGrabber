### Creating image list
```
python create_image_list.py directory image_list_file
```

### Detect faces in images
```
python face_detector.py image_list_file
```

### Crop face images
```
python crop_images.py image_list_file
```

### Create image list for cropped images
```
python create_image_list.py new_directory crop_image_list_file
```

### Generate face embedding
```
python gen_rep.py `cat crop_image_list_file` --output_file reps_file
```

### Classify faces
```
python classify_faces.py reps_file
```
