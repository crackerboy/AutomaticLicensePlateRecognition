import logging


import cv2
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt

logger = logging.getLogger()
mpl.rcParams['figure.dpi'] = 150
subplot_width = 3
subplot_height = 5


def plot(figure, subplot, image, title):
    figure.subplot(subplot)

    figure.imshow(image)
    figure.xlabel(title)
    figure.xticks([])
    figure.yticks([])
    return True


def plot_(figure, subplot, image, title):
    figure.subplot(subplot)

    figure.plot(image)
    figure.xlabel(title)

    return True


def plot_image(img, subplot_index, title='', fix_colors=True):
    plt.subplot(subplot_height, subplot_width, subplot_index)

    if fix_colors:
        if len(img.shape) == 3 and img.shape[2] == 3:
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        else:
            plt.imshow(img, cmap='gray')
    else:
        plt.imshow(img)

    plt.title(title)
    plt.axis('off')


def morphological_closing(image, kernel_size=(3, 3), iterations=6):
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)


def erosion(image, kernel_size=(3, 3), iterations=1):
    kernel_size = np.ones(kernel_size, np.uint8)
    return cv2.erode(image, kernel_size, iterations=iterations)


def canny_edge_detection(image, low_thresh=170, high_thresh=200):
    return cv2.Canny(image, low_thresh, high_thresh)


def show_results(original_image, gray_image, canny_image, auto_canny_image):
    plt.figure("test", figsize=(30, 30))
    plot(plt, 321, original_image, "Original image")
    plot(plt, 322, gray_image, "Canny image")
    plot(plt, 323, canny_image, "Y bound")
    plot(plt, 324, auto_canny_image, "X bound")

    plt.tight_layout()
    plt.show()

    return True


def plot_histograms(hist_1, hist_2, title):
    plt.figure("Histograms", figsize=(10, 5))
    plot_(plt, 121, hist_1, "Before")
    plot_(plt, 122, hist_2, "After")

    plt.title(title)
    plt.show()
