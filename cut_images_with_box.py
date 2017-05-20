import cv2
import sys
import os
import multiprocessing
import shutil
import threading
import math

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

        try:
            print 'reading', imgfile
            img = cv2.imread(imgfile)
            print 'done'

            with open(imgfile + '.bbox', 'r') as f:
                faces = [parse_line(line) for line in f.read().split('\n') if line]
            print faces
        except:
            return True

        #pts_file = dummy + '.pts'
        #if not os.path.exists(pts_file):
        #    return None
        #pts = read_points(pts_file)

        for i in range(len(faces)):
            # take only the first face
            x, y, w, h = faces[i]
            print x, y, w, h

            #if not is_good_box(faces[i], pts):
            #    continue

            scale_factor = 2.0

            x0 = x + 0.5 * w
            y0 = y + 0.5 * h
            print x0, y0

            half_w = scale_factor * 0.5 * w
            half_h = scale_factor * 0.5 * h

            # face region corners
            left = int(x0 - half_w)
            right = int(x0 + half_w)
            top = int(y0 - half_h)
            bottom = int(y0 + half_h)

            print left, right, top, bottom

            new_box = [left, top, right-left, bottom - top]

            # image size
            height, width = img.shape[:2]
            print width, height

            # fix the corners and pad the image
            if left < 0:
                left_pad = -left
                left_shift = left
            else:
                left_pad = 0
                left_shift = 0

            if right >= width:
                right_pad = right - width + 1
            else:
                right_pad = 0

            if top < 0:
                top_pad = -top
                top_shift = top
            else:
                top_pad = 0
                top_shift = 0

            if bottom >= height:
                bottom_pad = bottom - height + 1
            else:
                bottom_pad = 0

            print left_pad, right_pad, top_pad, bottom_pad

            # pad the image
            padded_img = cv2.copyMakeBorder(img, top_pad, bottom_pad, left_pad, right_pad, cv2.BORDER_CONSTANT, value=[255, 255, 255])

            # crop the image
            face_region = padded_img[top-top_shift:bottom-top_shift, left-left_shift:right-left_shift]

            # scale the cropped image
            wsize = 250
            res = cv2.resize(face_region, (wsize, wsize), interpolation = cv2.INTER_CUBIC)

            cv2.imwrite(os.path.join(crop_images_dir, basename), res)

            #transformed_pts = transform_points(new_box, pts, wsize)
            #image_file_name, ext = os.path.splitext(basename)
            #transformed_pts_file = os.path.join(crop_images_dir, image_file_name+'.pts')
            #with open(transformed_pts_file, 'w') as f:
            #    f.write(str(len(transformed_pts) / 2) + '\n')
            #    f.write(' '.join(map(str, transformed_pts)) + '\n')
        return True

    def run_with_limited_time(func, args, kwargs, time):
        """Runs a function with time limit

        :param func: The function to run
        :param args: The functions args, given as tuple
        :param kwargs: The functions keywords, given as dict
        :param time: The time limit in seconds
        :return: True if the function ended successfully. False if it was terminated.
        """
        p = threading.Thread(target=func, args=args, kwargs=kwargs)
        p.start()
        p.join(time)
        if p.is_alive():
            p.terminate()
            return False

        return True

    def batch_worker(imgfiles):
        for imgfile in imgfiles:
            crop_image(imgfile)

    N = len(img_list)
    num_workers = 16
    batch_size = math.ceil(N / float(num_workers))

    threads = []
    for i in range(num_workers):
        i0 = int(i * batch_size)
        i1 = int(min((i+1) * batch_size, N))
        t = threading.Thread(target=batch_worker, args=(img_list[i0:i1], ))
        t.daemon = True
        threads.append(t)
        t.start()

    for t in threads:
        t.join(30)
