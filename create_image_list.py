import os
import sys

rootdir = sys.argv[1]

img_exts = ['.jpg', '.png']
img_paths = []
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        basename, ext = os.path.splitext(file)
        img_path = os.path.join(subdir, file)
        print img_path, ext
        if ext in img_exts:
            img_paths.append(img_path)

print img_paths
with open(sys.argv[2], 'w') as f:
    [f.write(p + '\n') for p in img_paths]
