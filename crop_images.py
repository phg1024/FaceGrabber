import cv2
import sys
import os
import multiprocessing

def parse_line(line):
    return [int(x) for x in line.split(',') if x]

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        img_list = [line for line in f.read().split('\n') if line]

    images_dir = os.path.dirname(os.path.realpath(img_list[0]))
    crop_images_dir = os.path.join(images_dir, 'crop')

    def crop_image(imgfile):
        dummy, ext = os.path.splitext(imgfile)
        basename = os.path.basename(imgfile)
        print 'processing', imgfile
        print basename, ext
        img = cv2.imread(imgfile)

        with open(imgfile + '.bbox', 'r') as f:
            faces = [parse_line(line) for line in f.read().split('\n') if line]
        print faces
        for i in range(len(faces)):
            # take only the first face
            x, y, w, h = faces[i]
            print x, y, w, h

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

            # scale the crop to 256x256
            wsize = 256
            res = cv2.resize(face_region, (wsize, wsize), interpolation = cv2.INTER_CUBIC)

            cv2.imwrite(os.path.join(crop_images_dir, basename + ('_crop_%d' % i) + ext), res)

    pool = multiprocessing.Pool(16)
    pool.map(crop_image, img_list)
