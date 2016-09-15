import numpy as np
from scipy.spatial import ConvexHull
import cv2
import sys
import os
import multiprocessing
import skimage.io
import dlib
from matplotlib import pyplot as plt

from face_detector import create_detector, detect_face

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        img_list = [line for line in f.read().split('\n') if line]

    detector = create_detector()
    predictor = dlib.shape_predictor('./shape_predictor_68_face_landmarks.dat')

    def create_mask(imgfile):
        gray = cv2.imread(imgfile, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        faces, dets = detect_face(gray, detector)

        if faces is not None and faces:
            img = cv2.imread(imgfile)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

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
            all_pts = np.vstack((pts, flipped_contour_pts))
            print all_pts

            hull = ConvexHull(all_pts)

            showHull = False
            if showHull:
                masked_img = img.copy()
                for p in pts:
                    cv2.circle(masked_img, tuple(np.round(p-1.0).astype('int32')), 2, (0,255,0))
                plt.imshow(masked_img)
                for simplex in hull.simplices:
                    plt.plot(all_pts[simplex, 0], all_pts[simplex, 1], 'b-')
                plt.show()

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
                hull_pts = np.array([[all_pts[v, 0], all_pts[v, 1]] for v in hull.vertices]).astype('int32')
                cv2.fillConvexPoly(mask, hull_pts, 1)
                cv2.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)

            mask_out = np.where((mask==2) | (mask==0), 0, 255).astype('uint8')
            mask2 = np.where((mask==2) | (mask==0), 0, 1).astype('uint8')

            # TODO exclude eyebrow region, eye region and inner-mouth region

            showSegmentation = False
            if showSegmentation:
                masked_img = img*mask2[:,:,np.newaxis]
                plt.imshow(masked_img),plt.title('Using face detector'),plt.show()

            basename, ext = os.path.splitext(imgfile)

            cv2.imwrite(basename + '_mask0' + ext, mask_out)
            #cv2.imwrite('mask.png', mask_out)

            return True
        else:
            return False

    pool = multiprocessing.Pool(16)
    pool.map(create_mask, img_list)
    #pool.map(create_mask, [img_list[0]])
