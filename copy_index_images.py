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
        offset = int(sys.argv[3])
    else:
        offset = 0

    for i in range(len(img_list)):
        src_filename = img_list[i]
        basename, ext = os.path.splitext(src_filename)
        filename_str = ('%05d' % (offset + i)) + ext
        dst_filename = os.path.join(dst, filename_str)
        shutil.copy(src_filename, dst_filename)
        if os.path.exists(basename + '.pts'):
            pts_filename_str = ('%05d' % (offset + i)) + '.pts'
            shutil.copy(basename + '.pts', os.path.join(dst, pts_filename_str))
