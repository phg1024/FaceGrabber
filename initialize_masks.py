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
import multiprocessing
import skimage.io
import dlib
from matplotlib import pyplot as plt

from face_detector import create_detector, detect_face

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str)

args = parser.parse_args()

def safe_create(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)

if __name__ == '__main__':
    with open(args.input_file, 'r') as f:
        img_list = [line for line in f.read().split('\n') if line]

    img_dir = os.path.dirname(args.input_file)
    #safe_create(os.path.join(img_dir, 'masks'))
    #safe_create(os.path.join(img_dir, 'masked'))

    detector = create_detector()
    predictor = dlib.shape_predictor('./shape_predictor_68_face_landmarks.dat')

    def create_mask(imgfile):
        print 'processing', imgfile
        gray = cv2.imread(imgfile, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        faces, dets = detect_face(gray, detector)

        if faces is not None and faces:
            img = cv2.imread(imgfile)
            #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            shape = predictor(skimage.io.imread(imgfile), dets[0])
            parts = [shape.part(i) for i in range(shape.num_parts)]
            #print dir(shape), parts

            pts = np.array([[p.x, p.y] for p in parts])
            contour_pts = pts[0:17]

            # flip contour points vertically w.r.t line y = 0.5 * (pts[0].y, pts[16].y)
            flip_line_y = 0.5 * (pts[0][1] + pts[16][1])
            flipped_contour_pts = np.array([[p[0], p[1] - 2 * (p[1] - flip_line_y)] for p in contour_pts])

            #print pts
            #print pts, flipped_contour_pts
            #all_pts = np.vstack((pts, flipped_contour_pts))
            #all_pts = pts
            #print all_pts

            showHull = False
            if showHull:
                masked_img = img.copy()
                for p in pts:
                    cv2.circle(masked_img, tuple(np.round(p-1.0).astype('int32')), 2, (0,255,0))
                plt.imshow(masked_img)
                #for simplex in hull.simplices:
                #    plt.plot(pts[simplex, 0], pts[simplex, 1], 'b-')
                plt.show()
            outputPoints = False
            if outputPoints:
                with open('%s.pts' % imgfile, 'w') as f:
                    for p in pts:
                        print p
                        f.write('%d %d\n' % (p[0], p[1]))
                    return True

            mask = np.zeros(img.shape[:2], np.uint8)
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)

            if False:
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
            else:
                # fill a rough face region
                hull = ConvexHull(pts)
                hull_pts = np.array([[pts[v, 0], pts[v, 1]] for v in hull.vertices]).astype('int32')
                cv2.fillConvexPoly(mask, hull_pts, 1)

                hull = ConvexHull(flipped_contour_pts)
                hull_pts = np.array([[flipped_contour_pts[v, 0], flipped_contour_pts[v, 1]] for v in hull.vertices]).astype('int32')
                cv2.fillConvexPoly(mask, hull_pts, 3)

                # cut out eyes and mouth
                left_eye = range(36, 42)
                right_eye = range(42, 48)
                mouth = range(60, 68)

                left_eye_pts = np.array([pts[v] for v in left_eye]).astype('int32')
                right_eye_pts = np.array([pts[v] for v in right_eye]).astype('int32')
                mouth_pts = np.array([pts[v] for v in mouth]).astype('int32')

                #print left_eye_pts, right_eye_pts, mouth_pts
                cv2.fillPoly(mask, [left_eye_pts, right_eye_pts, mouth_pts], 0)

                cv2.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)

            mask_out = np.where((mask==2) | (mask==0), 0, 255).astype('uint8')
            mask2 = np.where((mask==2) | (mask==0), 0, 1).astype('uint8')

            if False:
                # now use mask2 to perform classification with SVM
                # assemble data using all pixels in img
                pos_pixels = []
                neg_pixels = []
                width, height, depth = img.shape
                print width, height, depth

                #print mask2
                #print img

                wsize = 4
                for h in range(wsize, height-wsize):
                    for w in range(wsize, width-wsize):
                        feat_vec = []
                        for y in range(-wsize, wsize+1):
                            for x in range(-wsize, wsize+1):
                                feat_vec.append(img[h][w])
                        feat_vec = np.array(feat_vec)
                        if mask2[h][w]:
                            pos_pixels.append(feat_vec.flatten())
                        else:
                            neg_pixels.append(feat_vec.flatten())
                pos_pixels = np.array(pos_pixels)
                neg_pixels = np.array(neg_pixels)
                print pos_pixels.shape, neg_pixels.shape

                # train SVM
                X = np.vstack((pos_pixels, neg_pixels))
                y = np.hstack(([1 for x in range(len(pos_pixels))],
                               [0 for x in range(len(neg_pixels))]))
                print 'data prepared'
                print 'training Classifier ...'
                #clf = svm.SVC()
                #clf = GMM(n_components=5)
                #clf = SGDClassifier(loss="hinge", penalty="l2")
                #clf = RandomForestClassifier(n_estimators=128)
                clf = GradientBoostingClassifier(n_estimators=32, learning_rate=1.0)
                clf.fit(X, y)
                print 'done'

                mask3 = np.zeros(img.shape[:2], np.uint8)
                for h in range(wsize, height-wsize):
                    for w in range(wsize, width-wsize):
                        feat_vec = []
                        for y in range(-wsize, wsize+1):
                            for x in range(-wsize, wsize+1):
                                feat_vec.append(img[h][w])

                        feat_vec = np.array(feat_vec)
                        good = clf.predict(feat_vec.flatten())
                        if good:
                            mask3[h][w] = 255
                        else:
                            mask3[h][w] = 0

            showSegmentation = False
            if showSegmentation:
                masked_img = img*mask2[:,:,np.newaxis]
                plt.imshow(masked_img),plt.title('Using face detector'),plt.show()

            basename, ext = os.path.splitext(imgfile)
            img_filename = os.path.basename(imgfile)
            img_dir = os.path.dirname(imgfile)

            masked_idx = (mask_out==0)
            masked_out = img
            masked_out[masked_idx] = 0

            print '%s/masks/%s' % (img_dir, img_filename)
            print '%s/masked/%s' % (img_dir, img_filename)

            safe_create(os.path.join(img_dir, 'masks'))
            safe_create(os.path.join(img_dir, 'masked'))

            cv2.imwrite('%s/masks/%s' % (img_dir, img_filename), mask_out)
            cv2.imwrite('%s/masked/%s' % (img_dir, img_filename), masked_out)

            #cv2.imwrite(basename + '_mask3' + ext, mask3)
            #cv2.imwrite('mask.png', mask_out)

            return True
        else:
            return False

    pool = multiprocessing.Pool(16)
    pool.map(create_mask, img_list)
    #pool.map(create_mask, [img_list[0]])
