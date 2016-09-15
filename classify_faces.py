import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

from sklearn.cluster import MeanShift, estimate_bandwidth

import sys
import os
import shutil

# read the input file
reps = {}
with open(sys.argv[1], 'r') as f:
    lines = [line for line in f.read().split('\n') if line]
    for line in lines:
        filename, rep_str = line.split(':')
        reps[filename] = [float(x) for x in rep_str.split()]

print reps

X = np.array(reps.values())

ms = MeanShift()
ms.fit(X)
labels = ms.labels_
cluster_centers = ms.cluster_centers_

labels_unique = np.unique(labels)
n_clusters = len(labels_unique)

print n_clusters

main_person = labels == 0
other_persons = labels != 0

images_dir = os.path.dirname(os.path.realpath(reps.keys()[0]))
main_person_dir = os.path.join(images_dir, 'main_person')
other_persons_dir = os.path.join(images_dir, 'other_persons')

if not os.path.exists(main_person_dir):
    os.mkdir(main_person_dir)

with open(images_dir + '/main_person.txt', 'w') as f:
    for i in range(len(labels)):
        if main_person[i]:
            f.write(reps.keys()[i] + '\n')
            shutil.copy(reps.keys()[i], main_person_dir)

if not os.path.exists(other_persons_dir):
    os.mkdir(other_persons_dir)
with open(images_dir + '/other_persons.txt', 'w') as f:
    for i in range(len(labels)):
        if other_persons[i]:
            f.write(reps.keys()[i] + '\n')
            shutil.copy(reps.keys()[i], other_persons_dir)
