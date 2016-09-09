import numpy as np
from scipy.spatial import ConvexHull
import cv2
import sys
import os
import multiprocessing
from matplotlib import pyplot as plt

from face_detector import create_detector, detect_face

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        img_list = [line for line in f.read().split('\n') if line]

    detector = create_detector()

    def create_mask(imgfile):
        gray = cv2.imread(imgfile, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        faces = detect_face(gray, detector)

        if faces is not None and faces:
            img = cv2.imread(imgfile)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            mask = np.zeros(img.shape[:2], np.uint8)
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)

            min_pt = np.array([faces[0][0], faces[0][1]])
            max_pt = min_pt+np.array([faces[0][2], faces[0][3]])
            center_pt = np.floor(0.5 * (min_pt + max_pt)).astype('int32')
            scale = 1.5
            face_region_size = np.floor((max_pt - min_pt) * 0.5 * scale).astype('int32')
            rect = (center_pt[0] - face_region_size[0],
                    center_pt[1] - face_region_size[1],
                    center_pt[0] + face_region_size[0],
                    center_pt[1] + face_region_size[1])

            #print rect
            cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
            mask2 = np.where((mask==2) | (mask==0), 0, 255).astype('uint8')

            #masked_img = img*mask2[:,:,np.newaxis]
            #plt.imshow(masked_img),plt.title('Using face detector'),plt.show()
            #plt.imshow(mask2), plt.show()
            basename, ext = os.path.splitext(imgfile)

            cv2.imwrite(basename + '_mask0' + ext, mask2)

            return True
        else:
            return False

    pool = multiprocessing.Pool(16)
    pool.map(create_mask, img_list)
