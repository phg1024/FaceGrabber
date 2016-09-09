import numpy as np
from scipy.spatial import ConvexHull
import cv2
import dlib
import sys
import multiprocessing

use_dlib = True

haar_cascade_path = 'haarcascade_frontalface_default.xml'

def load_cascade(filepath=haar_cascade_path):
    return cv2.CascadeClassifier(filepath)

def create_detector():
    if use_dlib:
        return dlib.get_frontal_face_detector()
    else:
        return load_cascade()

def detect_face(img, detector=None):
    if not detector:
        detector = create_detector()
    if use_dlib:
        dets = detector(img)
        faces = []
        for i, d in enumerate(dets):
            faces.append([d.left(), d.top(), d.right()-d.left(), d.bottom()-d.top()])
        return faces
    else:
        return detector.detectMultiScale(img, 1.25, 5)

if __name__ == '__main__':
    face_detector = create_detector()

    with open(sys.argv[1], 'r') as f:
        img_list = [line for line in f.read().split('\n') if line]

    def proc_image(imgfile):
        print 'processing', imgfile
        img = cv2.imread(imgfile, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        faces = detect_face(img, face_detector)
        print faces
        if faces is not None:
            with open(imgfile+'.bbox', 'w') as f:
                for face in faces:
                    f.write(','.join([str(v) for v in face]) + '\n')
            return True
        else:
            print 'No face detected.'
            return False

    pool = multiprocessing.Pool(6)
    pool.map(proc_image, img_list)
    sys.exit(0)
