import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument('output_file', type=str)
parser.add_argument('--recursive', action='store_true')

args = parser.parse_args()

root_dir = args.directory

img_exts = ['.jpg', '.png']
img_paths = []

if args.recursive:
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            basename, ext = os.path.splitext(file)
            img_path = os.path.join(subdir, file)
            print img_path, ext
            if ext in img_exts:
                img_paths.append(img_path)
else:
    for item in os.listdir(root_dir):
        if os.path.isfile(os.path.join(root_dir, item)):
            basename, ext = os.path.splitext(item)
            img_path = os.path.join(root_dir, item)
            print img_path, ext
            if ext in img_exts:
                img_paths.append(img_path)

print img_paths
with open(args.output_file, 'w') as f:
    [f.write(p + '\n') for p in img_paths]
