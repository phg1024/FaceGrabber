import argparse
import sys
import os
import shutil
import math

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str)
parser.add_argument('size', type=int)
parser.add_argument('dest', type=str)

args = parser.parse_args()

with open(args.input_file, 'r') as f:
    lines = f.read().splitlines()

# create destination folder
if os.path.exists(args.dest):
    shutil.rmtree(args.dest)
os.mkdir(args.dest)

num_splits = int(math.ceil(len(lines) / float(args.size)))

for i in range(num_splits):
    print 'processing split %d/%d' % (i, num_splits)
    lines_i = lines[i*args.size:(i+1)*args.size]

    split_dir = os.path.join(args.dest, 'split_%04d' % i)
    if os.path.exists(split_dir):
        shutil.rmtree(split_dir)
    os.mkdir(split_dir)
    for line in lines_i:
        shutil.copy(line, split_dir)
