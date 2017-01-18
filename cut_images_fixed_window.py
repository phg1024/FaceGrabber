import cv2
import sys
import os
import multiprocessing
import shutil

def parse_line(line):
    return [int(x) for x in line.split(',') if x]

def read_points(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    num_points_tag = lines[0]
    points_str = ' '.join(lines[1:])
    points = map(lambda x: float(x), points_str.split())
    return points

def is_good_box(box, points):
    def is_inside(box, point):
        x, y, w, h = box
        px, py = point
        return True if px >= x and px < x + w and py >= y and py < y + h else False

    x = [points[i*2] for i in range(len(points)/2)]
    y = [points[i*2+1] for i in range(len(points)/2)]
    good_cnt = 0
    for xi, yi in zip(x, y):
        if is_inside(box, (xi, yi)):
            good_cnt += 1
    return good_cnt > 0.75 * len(x)

def transform_points(box, pts, size):
    x, y, w, h = box
    px = [pts[i*2] for i in range(len(pts)/2)]
    py = [pts[i*2+1] for i in range(len(pts)/2)]

    points = []
    for i in range(len(px)):
        xi = (px[i] - x) / float(w) * size
        yi = (py[i] - y) / float(h) * size
        points.append(xi)
        points.append(yi)

    return points

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        img_list = [line for line in f.read().split('\n') if line]

    images_dir = os.path.dirname(os.path.realpath(img_list[0]))
    crop_images_dir = os.path.join(images_dir, 'crop')

    try:
        if os.path.exists(crop_images_dir):
            shutil.rmtree(crop_images_dir)
        os.mkdir(crop_images_dir)
    except:
        print 'Failed to delete target directory ...'

    def crop_image(imgfile):
        dummy, ext = os.path.splitext(imgfile)
        basename = os.path.basename(imgfile)
        print 'processing', imgfile
        print basename, ext

        img = cv2.imread(imgfile)

        pts_file = dummy + '.pts'
        if not os.path.exists(pts_file):
            return None
        pts = read_points(pts_file)

        x = 475
        y = 4
        w = 512
        h = 512

        # crop the image
        face_region = img[y:y+h, x:x+w]

        cv2.imwrite(os.path.join(crop_images_dir, basename), face_region)

        transformed_pts = transform_points((x, y, w, h), pts, 512)
        image_file_name, ext = os.path.splitext(basename)
        transformed_pts_file = os.path.join(crop_images_dir, image_file_name+'.pts')
        with open(transformed_pts_file, 'w') as f:
            f.write(str(len(transformed_pts) / 2) + '\n')
            f.write(' '.join(map(str, transformed_pts)) + '\n')

    pool = multiprocessing.Pool(16)
    pool.map(crop_image, img_list)
