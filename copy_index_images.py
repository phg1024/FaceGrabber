import sys
import os
import shutil

def create_dir(dirname):
  try:
    os.stat(dirname)
  except:
    os.mkdir(dirname)

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        img_list = [line for line in f.read().split('\n') if line]

    dst = sys.argv[2]

    create_dir(sys.argv[2])

    if len(sys.argv) > 3:
        need_pts = sys.argv[3]
    else:
        need_pts = "y"

    if len(sys.argv) > 4:
        offset = int(sys.argv[4])
    else:
        offset = 0

    for i in range(len(img_list)):
        src_filename = img_list[i]
        print src_filename
        basename, ext = os.path.splitext(src_filename)
        filename_str = ('%d' % (offset + i)) + ext
        dst_filename = os.path.join(dst, filename_str)
        if os.path.exists(basename + '.pts') or need_pts == "n":
            shutil.copy(src_filename, dst_filename)
            if need_pts != "n":
                pts_filename_str = ('%d' % (offset + i)) + '.pts'
                shutil.copy(basename + '.pts', os.path.join(dst, pts_filename_str))
