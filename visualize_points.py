import numpy as np
from scipy.spatial import ConvexHull

from sklearn import svm
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.mixture import GMM, VBGMM
from sklearn.linear_model import SGDClassifier

import argparse
import cv2
import sys
import os
import shutil
import multiprocessing
import skimage.io
import dlib
from matplotlib import pyplot as plt

from face_detector import create_detector, detect_face

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str)

args = parser.parse_args()

def read_points(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    num_points_tag = lines[0]
    points_str = ' '.join(lines[1:])
    points = map(lambda x: float(x), points_str.split())
    return points

if __name__ == '__main__':
    with open(args.input_file, 'r') as f:
        img_list = [line.split() for line in f.read().split('\n') if line]

    images_dir = os.path.dirname(os.path.realpath(args.input_file))
    points_images_dir = os.path.join(images_dir, 'feature_points')
    print images_dir, points_images_dir

    if os.path.exists(points_images_dir):
        shutil.rmtree(points_images_dir)
    os.mkdir(points_images_dir)

    def visualize_points(filenames):
        imgfile, ptsfile = filenames
        dummy, ext = os.path.splitext(imgfile)
        basename = os.path.basename(imgfile)
        print 'processing', imgfile, ptsfile

        img = cv2.imread(os.path.join(images_dir, imgfile))
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if not os.path.exists(os.path.join(images_dir, ptsfile)):
            return None
        pts = read_points(os.path.join(images_dir, ptsfile))

        num_pts = len(pts) / 2
        for i in range(num_pts):
            xi = pts[i*2]
            yi = pts[i*2+1]
            cv2.circle(img, tuple(np.round([xi-1, yi-1]).astype('int32')), 2, (0,255,0), -1)

        cv2.imwrite(os.path.join(points_images_dir, imgfile), img)
        #print 'done.'

        return True

    pool = multiprocessing.Pool(16)
    pool.map(visualize_points, img_list)
