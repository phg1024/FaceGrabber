import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy.spatial.distance as dist

from sklearn.cluster import MeanShift, estimate_bandwidth, AgglomerativeClustering
from sklearn.mixture import GMM, VBGMM
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn import linear_model

import argparse
import sys
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str)
parser.add_argument('--method', type=str, default='scikit')
parser.add_argument('--threshold', type=float, default=0.75)

args = parser.parse_args()

# read the input file
all_reps = {}
with open(args.input_file, 'r') as f:
    lines = [line for line in f.read().split('\n') if line]
    for line in lines:
        filename, rep_str = line.split(':')
        all_reps[filename] = [float(x) for x in rep_str.split()]

print all_reps

def greedy_removal(reps_in, threshold=0.9):
    reps = reps_in.copy()

    THRES = threshold
    max_dist = 10.0

    outliers = []

    while max_dist > THRES:
        X = np.array(reps.values())
        D = dist.squareform(dist.pdist(X, 'euclidean'))
        sums = D.sum(axis=0)
        idx = np.argmax(sums)
        max_dist = D.sum(axis=0)[idx] / len(reps.values())

        print D.sum(axis=0)[idx], D.sum(), D.sum(axis=0)[idx] / len(reps.values())

        if max_dist < THRES:
            break
        else:
            key = reps.keys()[idx]
            #print idx, key
            outliers.append(key)
            reps.pop(key)

    inliers = reps.keys()
    print 'outliers', outliers
    print 'inliers', inliers
    return (inliers, outliers)

if args.method == 'scikit':
    X = np.array(all_reps.values())

    if True:
        D = dist.squareform(dist.pdist(X, 'euclidean'))
        plt.imshow(D)
        plt.show()

    ms = MeanShift(bandwidth=0.9)
    ms.fit(X)

    labels_ms = ms.labels_
    cluster_centers = ms.cluster_centers_

    # AgglomerativeClustering
    clustering = AgglomerativeClustering(linkage='ward')
    clustering.fit(X)

    labels = clustering.labels_

    labels_unique = np.unique(labels)
    n_clusters = len(labels_unique)

    print n_clusters
    print labels

    all_mean = X.mean(axis=0)
    main_mean = X[labels==0].mean(axis=0)
    others_mean = X[labels!=0].mean(axis=0)

    d1 = np.linalg.norm(all_mean-main_mean)
    d2 = np.linalg.norm(all_mean-others_mean)

    if d1 < d2:
        main_person = labels == 0
        other_persons = main_person != 1
    else:
        main_person = labels != 0
        other_persons = main_person != 1

    images_dir = os.path.dirname(os.path.realpath(all_reps.keys()[0]))
    main_person_dir = os.path.join(images_dir, 'main_person')
    other_persons_dir = os.path.join(images_dir, 'other_persons')

    if os.path.exists(main_person_dir):
        shutil.rmtree(main_person_dir)
    os.mkdir(main_person_dir)

    with open(images_dir + '/main_person.txt', 'w') as f:
        for i in range(len(labels)):
            if main_person[i]:
                f.write(all_reps.keys()[i] + '\n')
                shutil.copy(all_reps.keys()[i], main_person_dir)

    if os.path.exists(other_persons_dir):
        shutil.rmtree(other_persons_dir)
    os.mkdir(other_persons_dir)
    with open(images_dir + '/other_persons.txt', 'w') as f:
        for i in range(len(labels)):
            if other_persons[i]:
                f.write(all_reps.keys()[i] + '\n')
                shutil.copy(all_reps.keys()[i], other_persons_dir)


    # plot the embeddings
    plt.plot(X.transpose(), '-b', alpha=0.25)
    plt.plot(X[labels==0].transpose(), '-r', alpha=0.5)
    plt.show()
elif args.method == 'greedy':
    print 'Greedy removal'

    inliers, outliers = greedy_removal(all_reps, args.threshold)

    print len(inliers), len(outliers)

    images_dir = os.path.dirname(os.path.realpath(all_reps.keys()[0]))
    main_person_dir = os.path.join(images_dir, 'main_person')
    other_persons_dir = os.path.join(images_dir, 'other_persons')

    if os.path.exists(main_person_dir):
        shutil.rmtree(main_person_dir)
    os.mkdir(main_person_dir)

    with open(images_dir + '/main_person.txt', 'w') as f:
        for k in inliers:
            f.write(k + '\n')
            shutil.copy(k, main_person_dir)

    if os.path.exists(other_persons_dir):
        shutil.rmtree(other_persons_dir)
    os.mkdir(other_persons_dir)
    with open(images_dir + '/other_persons.txt', 'w') as f:
        for k in outliers:
            f.write(k + '\n')
            shutil.copy(k, other_persons_dir)

elif args.method == 'svm':
    # use greedy method to find two subsets: true inliners and true outliers
    inliers, dummy = greedy_removal(all_reps, 0.5)
    dummy, outliers = greedy_removal(all_reps, 1.0)

    print len(inliers), len(outliers), len(all_reps)

    if True:
        # train a SVM classifier with true inliners and true outliers
        X_inliers = [all_reps[key] for key in inliers]
        X_outliers = [all_reps[key] for key in outliers]
        X = np.vstack((X_inliers, X_outliers))
        y = np.hstack(([0 for key in inliers], [1 for key in outliers]))
        #clf = svm.SVC()
        #clf = RandomForestClassifier(n_estimators=128)
        clf = GradientBoostingClassifier(n_estimators=128, learning_rate=1.0)
        clf = clf.fit(X, y)
        print X, y
        clf.fit(X, y)

        # perform classification using the SVM
        print clf.predict(all_reps.values())
        results = clf.predict(all_reps.values())

        inliers = [all_reps.keys()[i] for i in range(len(results)) if results[i] == 0]
        outliers = [all_reps.keys()[i] for i in range(len(results)) if results[i] == 1]

        print len(inliers), len(outliers)

    images_dir = os.path.dirname(os.path.realpath(all_reps.keys()[0]))
    main_person_dir = os.path.join(images_dir, 'main_person')
    other_persons_dir = os.path.join(images_dir, 'other_persons')

    if os.path.exists(main_person_dir):
        shutil.rmtree(main_person_dir)
    os.mkdir(main_person_dir)

    with open(images_dir + '/main_person.txt', 'w') as f:
        for k in inliers:
            f.write(k + '\n')
            shutil.copy(k, main_person_dir)

    if os.path.exists(other_persons_dir):
        shutil.rmtree(other_persons_dir)
    os.mkdir(other_persons_dir)
    with open(images_dir + '/other_persons.txt', 'w') as f:
        for k in outliers:
            f.write(k + '\n')
            shutil.copy(k, other_persons_dir)

elif args.method == 'total_variance':
    # use greedy method to find two subsets: true inliners and true outliers
    inliers, dummy = greedy_removal(all_reps, 0.5)
    dummy, outliers = greedy_removal(all_reps, 1.0)

    X_inliers = [all_reps[key] for key in inliers]
    X_outliers = [all_reps[key] for key in outliers]
    X = np.vstack((X_inliers, X_outliers))
    y = np.hstack(([0 for key in inliers], [1 for key in outliers]))

    # fit a GMM classifier
    clf = GMM(n_components=1)
    print clf.fit(X_inliers)

    # slowly grow the set of inliers based on total variance increase
    all_scores = clf.score(all_reps.values())
    idx_scores = [(i, all_scores[i]) for i in range(len(all_scores))]
    sorted_scores = sorted(idx_scores, key=lambda x: x[1])
    print sorted_scores
    print 'median', sorted_scores[int(len(sorted_scores)/2)]

    # fit a line to the sorted scores
    N_line = len(sorted_scores)
    #print N_line
    y_line = np.array([y for x, y in sorted_scores]).reshape((-1, 1))
    x_line = np.array(range(len(y_line))).reshape((-1, 1))
    #print x_line[int(N_line/2):], y_line[int(N_line/2):]

    regr = linear_model.LinearRegression()
    regr.fit(x_line[int(N_line/2):], y_line[int(N_line/2):])
    print 'coeff', regr.coef_

    error_line = y_line - regr.predict(x_line)
    print error_line.reshape((1, -1))
    good = np.abs(error_line) < args.threshold

    print [sorted_scores[i][0] for i in range(len(good)) if good[i]]
    print [sorted_scores[i][0] for i in range(len(good)) if not good[i]]
    inliers = [all_reps.keys()[sorted_scores[i][0]] for i in range(len(good)) if good[i]]
    outliers = [all_reps.keys()[sorted_scores[i][0]] for i in range(len(good)) if not good[i]]

    print len(inliers), len(outliers)

    if False:
        # take the highest half
        high_scores = sorted_scores[int(len(sorted_scores)/2):]

        # compute mean and variance
        mean_high_score = np.array([y for x,y in high_scores]).mean()
        var_high_score = np.std(np.array([y for x, y in high_scores]))
        print 'mean', mean_high_score, 'std', var_high_score
        print 'threshold', mean_high_score - 5.0 * var_high_score
        good = clf.score(all_reps.values()) > mean_high_score - 5.0 * var_high_score
        print good

        inliers = [all_reps.keys()[i] for i in range(len(good)) if good[i]]
        outliers = [all_reps.keys()[i] for i in range(len(good)) if not good[i]]

    images_dir = os.path.dirname(os.path.realpath(all_reps.keys()[0]))
    main_person_dir = os.path.join(images_dir, 'main_person')
    other_persons_dir = os.path.join(images_dir, 'other_persons')

    if os.path.exists(main_person_dir):
        shutil.rmtree(main_person_dir)
    os.mkdir(main_person_dir)

    with open(images_dir + '/main_person.txt', 'w') as f:
        for k in inliers:
            f.write(k + '\n')
            shutil.copy(k, main_person_dir)

    if os.path.exists(other_persons_dir):
        shutil.rmtree(other_persons_dir)
    os.mkdir(other_persons_dir)
    with open(images_dir + '/other_persons.txt', 'w') as f:
        for k in outliers:
            f.write(k + '\n')
            shutil.copy(k, other_persons_dir)
