import numpy as np
from PIL import Image, ImageEnhance

from util.basic_transformations import BasicTransformations
from util.image_display_helper import ImageDisplayHelper
from util.input_output import *

display = ImageDisplayHelper(False, 2, 5)
bt = BasicTransformations(display)


def process(image_path):
    display = ImageDisplayHelper(False, 2, 5)
    bt = BasicTransformations(display)

    image = Image.open(image_path)
    contrast_bumped_image = np.asarray(ImageEnhance.Contrast(image).enhance(5))
    image = np.asarray(image)

    gray_image = bt.gray_scale(contrast_bumped_image)
    binarized_image = bt.otsu_threshold(gray_image)
    eroded_image = bt.erosion(binarized_image)
    closed_image = bt.morphological_closing(binarized_image, iterations=5)
    eroded_closed_image = bt.morphological_closing(eroded_image, iterations=5)

    _, result_polygon = _find_plate_contour(eroded_closed_image, image)
    polygon_flat_list = [item for sublist in result_polygon for item in sublist]
    plate_corners_list = [(arr[0], arr[1]) for arr in polygon_flat_list]

    deskewed_image = four_point_transform(gray_image, np.array(plate_corners_list))
    _draw_plate_polygons(image, result_polygon)

    cv2.imshow("Original", image)
    cv2.imshow("Grayscale", gray_image)
    cv2.imshow("Contrast bumped", contrast_bumped_image)
    cv2.imshow("Bin", binarized_image)
    cv2.imshow("Bin -> Erosion", eroded_image)
    cv2.imshow("Bin -> Erosion -> Closing", eroded_closed_image)
    cv2.imshow("Bin -> Closing", closed_image)
    cv2.imshow("Result Polygon", image)
    cv2.imshow("Deskewed image", deskewed_image)
    cv2.imwrite("ocr-ready.jpg", deskewed_image)

    cv2.waitKey()


def deskew(image):
    gray_image = bt.gray_scale(image)
    contrast_bumped_image = bt.contrast_brightness(gray_image, alpha=2, beta=50)

    binarized_image = bt.otsu_threshold(gray_image)
    eroded_image = bt.erosion(binarized_image)
    closed_image = bt.morphological_closing(binarized_image, iterations=5)
    eroded_closed_image = bt.morphological_closing(eroded_image, iterations=5)
    # ut.show_one_image(eroded_closed_image)

    _, result_polygon = _find_plate_contour(eroded_closed_image, image)
    polygon_flat_list = [item for sublist in result_polygon for item in sublist]
    plate_corners_list = [(arr[0], arr[1]) for arr in polygon_flat_list]

    deskewed_image = four_point_transform(gray_image, np.array(plate_corners_list))
    _draw_plate_polygons(image, result_polygon)
    return deskewed_image


def _order_corner_points(points):
    # initialize a list of coordinates that will be ordered top-left, top-right, bottom-right, bottom-left
    rect = np.zeros((4, 2), dtype="float32")
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    ooints_sum = points.sum(axis=1)
    rect[0] = points[np.argmin(ooints_sum)]
    rect[2] = points[np.argmax(ooints_sum)]
    # top-right point will have the smallest difference, bottom-left will have the largest difference
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]

    return rect


def four_point_transform(image, points):
    rect = _order_corner_points(points)
    (top_left, top_right, bottom_right, bottom_left) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    width_a = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) + ((bottom_right[1] - bottom_left[1]) ** 2))
    width_b = np.sqrt(((top_right[0] - top_left[0]) ** 2) + ((top_right[1] - top_left[1]) ** 2))
    max_width = max(int(width_a), int(width_b))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    height_a = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
    height_b = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))
    max_height = max(int(height_a), int(height_b))

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")

    warp_matrix = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, warp_matrix, (max_width, max_height))

    return warped


if __name__ == '__main__':
    process("dataset/skewed_trimmed_samples/skewed_009.jpg")
