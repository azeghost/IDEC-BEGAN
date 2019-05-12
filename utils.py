"""
Most codes from https://github.com/carpedm20/DCGAN-tensorflow
"""
from __future__ import division
import scipy.misc
import matplotlib.pyplot as plt
import os

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
from keras.datasets import mnist
from keras.datasets import fashion_mnist
from smallNorbDataset import SmallNORBDataset
import urllib.request
import gzip
from skimage.transform import resize

def load_mnist():
    (X, y), (X_test, y_test) = mnist.load_data()
    X = np.concatenate((X, X_test))
    y = np.concatenate((y, y_test))
    del X_test
    del y_test

    X = X.astype(np.float32) / 255.0

    print('Dataset size {}'.format(X.shape))

    y_vec = np.zeros((len(y), 10), dtype=np.float)
    for i, label in enumerate(y):
        y_vec[i, y[i]] = 1.0
    X = X.reshape((X.shape[0], X.shape[1], X.shape[2], 1))
    print(X.shape)
    return X, y_vec


def load_fashion_mnist():
    (X, y), (X_test, y_test) = fashion_mnist.load_data()
    X = np.concatenate((X, X_test))
    y = np.concatenate((y, y_test))
    del X_test
    del y_test

    X = X.astype(np.float32) / 255.0

    print('Dataset size {}'.format(X.shape))

    y_vec = np.zeros((len(y), 10), dtype=np.float)
    for i, label in enumerate(y):
        y_vec[i, y[i]] = 1.0
    print(X.shape)
    X = X.reshape((X.shape[0], X.shape[1], X.shape[2], 1))
    print(X.shape)
    return X, y_vec


def download_small_norb():
    """Loads the SmallNORB dataset.

    # Returns
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`.
    """
    dirname = os.path.join('datasets', 'small-norb')
    base = 'https://cs.nyu.edu/~ylclab/data/norb-v1.0-small/'
    files = ['smallnorb-5x46789x9x18x6x2x96x96-training-cat.mat.gz',
             'smallnorb-5x46789x9x18x6x2x96x96-training-dat.mat.gz',
             'smallnorb-5x46789x9x18x6x2x96x96-training-info.mat.gz',
             'smallnorb-5x01235x9x18x6x2x96x96-testing-cat.mat.gz',
             'smallnorb-5x01235x9x18x6x2x96x96-testing-dat.mat.gz',
             'smallnorb-5x01235x9x18x6x2x96x96-testing-info.mat.gz']

    print('Dataset initialization...')

    if not os.path.exists(dirname):
        if not os.path.exists('datasets'):
            os.mkdir('datasets')
        os.mkdir(dirname)

    for fname in files:
        exists = os.path.isfile(dirname + '/' + fname[:-3])

        if not exists:
            print('Downloading dataset remotely...')

            url = base + fname
            response = urllib.request.urlopen(url)
            with open(dirname + '/' + fname[:-3], 'wb') as outfile:
                outfile.write(gzip.decompress(response.read()))

            print('Download completed!')
        else:
            print('Used dataset from local!')

    dataset = SmallNORBDataset(dataset_root=dirname)

    print('Enumeration of dataset started...')

    x_train = np.zeros((dataset.n_examples * 2, 32, 32))
    y_train = np.zeros(dataset.n_examples * 2)

    for i, data in enumerate(dataset.data['train']):
        x_train[2 * i] = resize(data.image_lt, (32, 32), anti_aliasing=True)
        x_train[2 * i + 1] = resize(data.image_rt, (32, 32), anti_aliasing=True)
        y_train[2 * i] = data.category
        y_train[2 * i + 1] = data.category

    x_test = np.zeros((dataset.n_examples * 2, 32, 32))
    y_test = np.zeros(dataset.n_examples * 2)

    for i, data in enumerate(dataset.data['test']):
        x_train[2 * i] = resize(data.image_lt, (32, 32), anti_aliasing=True)
        x_train[2 * i + 1] = resize(data.image_rt, (32, 32), anti_aliasing=True)
        y_test[2 * i] = data.category
        y_test[2 * i + 1] = data.category

    print('Completed enumeration of dataset!')

    return (x_train, y_train), (x_test, y_test)


def load_small_norb():
    (X, y), (X_test, y_test) = download_small_norb()
    X = np.concatenate((X, X_test))
    y = np.concatenate((y, y_test))
    del X_test
    del y_test

    print('Dataset size {}'.format(X.shape))

    y_vec = np.zeros((len(y), 5), dtype=np.float)
    #for i, label in enumerate(y):
    #   y_vec[i, y[i]] = 1.0
    X = X.reshape((X.shape[0], X.shape[1], X.shape[2], 1))
    print('Shape of x ' , X.shape)
    print('Shape of y ' , y_vec.shape)
    return X, y_vec


def check_folder(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir


def show_all_variables():
    model_vars = tf.trainable_variables()
    slim.model_analyzer.analyze_vars(model_vars, print_info=True)


def get_image(image_path, input_height, input_width, resize_height=64, resize_width=64, crop=True, grayscale=False):
    image = imread(image_path, grayscale)
    return transform(image, input_height, input_width, resize_height, resize_width, crop)


def save_images(images, size, image_path):
    return imsave(inverse_transform(images), size, image_path)


def imread(path, grayscale=False):
    if (grayscale):
        return scipy.misc.imread(path, flatten=True).astype(np.float)
    else:
        return scipy.misc.imread(path).astype(np.float)


def merge_images(images, size):
    return inverse_transform(images)


def merge(images, size):
    h, w = images.shape[1], images.shape[2]
    if (images.shape[3] in (3, 4)):
        c = images.shape[3]
        img = np.zeros((h * size[0], w * size[1], c))
        for idx, image in enumerate(images):
            i = idx % size[1]
            j = idx // size[1]
            img[j * h:j * h + h, i * w:i * w + w, :] = image
        return img
    elif images.shape[3] == 1:
        img = np.zeros((h * size[0], w * size[1]))
        for idx, image in enumerate(images):
            i = idx % size[1]
            j = idx // size[1]
            img[j * h:j * h + h, i * w:i * w + w] = image[:, :, 0]
        return img
    else:
        raise ValueError('in merge(images,size) images parameter ''must have dimensions: HxW or HxWx3 or HxWx4')


def imsave(images, size, path):
    image = np.squeeze(merge(images, size))
    return scipy.misc.imsave(path, image)


def center_crop(x, crop_h, crop_w, resize_h=64, resize_w=64):
    if crop_w is None:
        crop_w = crop_h
    h, w = x.shape[:2]
    j = int(round((h - crop_h) / 2.))
    i = int(round((w - crop_w) / 2.))
    return scipy.misc.imresize(x[j:j + crop_h, i:i + crop_w], [resize_h, resize_w])


def transform(image, input_height, input_width, resize_height=64, resize_width=64, crop=True):
    if crop:
        cropped_image = center_crop(image, input_height, input_width, resize_height, resize_width)
    else:
        cropped_image = scipy.misc.imresize(image, [resize_height, resize_width])
    return np.array(cropped_image) / 127.5 - 1.


def inverse_transform(images):
    return (images + 1.) / 2.


""" Drawing Tools """


# borrowed from https://github.com/ykwon0407/variational_autoencoder/blob/master/variational_bayes.ipynb
def save_scattered_image(z, id, z_range_x, z_range_y, name='scattered_image.jpg'):
    N = 10
    plt.figure(figsize=(8, 6))
    plt.scatter(z[:, 0], z[:, 1], c=np.argmax(id, 1), marker='o', edgecolor='none', cmap=discrete_cmap(N, 'jet'))
    plt.colorbar(ticks=range(N))
    axes = plt.gca()
    axes.set_xlim([-z_range_x, z_range_x])
    axes.set_ylim([-z_range_y, z_range_y])
    plt.grid(True)
    plt.savefig(name)


# borrowed from https://gist.github.com/jakevdp/91077b0cae40f8f8244a
def discrete_cmap(N, base_cmap=None):
    """Create an N-bin discrete colormap from the specified input map"""

    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:

    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, N))
    cmap_name = base.name + str(N)
    return base.from_list(cmap_name, color_list, N)
