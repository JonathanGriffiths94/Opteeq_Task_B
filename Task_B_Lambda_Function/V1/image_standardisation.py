import cv2
import numpy as np


def standardise_image(img: 'numpy.ndarray') -> 'numpy.ndarray':
    """
    :param img:
    :return: standardised image
    """
    # Function call to check text orientation and rotate image
    # rotated_img = rotate_image(img)
    rotated_img = img
    # Function call to check image size and resize image
    resized_img = resize_and_pad(rotated_img)

    return resized_img


def resize_and_pad(img: np.ndarray, desired_size: int = 2000) -> np.ndarray:
    old_size = img.shape[:2]  # old_size is in (height, width) format

    ratio = float(desired_size) / max(old_size)
    new_size = tuple([int(x * ratio) for x in old_size])

    # new_size should be in (width, height) format
    img = cv2.resize(img, (new_size[1], new_size[0]))

    delta_w = desired_size - new_size[1]
    delta_h = desired_size - new_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [0, 0, 0]
    new_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                 value=color)
    return new_img


def detect_angle(img: 'numpy.ndarray') -> int:
    """
    Text orientation detection.
    :param img: Image array
    :return: angle corresponding to orientation, 90=desired orientation
    """

    # TO DO: Add image crop to only select the area of the actual receipt

    # Convert image to grayscale and perform a gaussian blur
    # Then use adaptive threshold to obtain a binary image
    mask = np.zeros(img.shape, dtype=np.uint8)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    adaptive = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 4)

    # Find contours
    cnts = cv2.findContours(adaptive, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # Filter using contour area to remove noise particles and large borders
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 45000 and area > 20:
            cv2.drawContours(mask, [c], -1, (255, 255, 255), -1)

    # Pass contours that pass the filter onto a mask
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    h, w = mask.shape

    # To determine the angle we split the image in half based the dimensions
    # If width > height then it must be a horizontal image so we split in half vertically
    # If height > width then it must be a vertical image so we split in half horizontally

    # Horizontal
    if w > h:
        left = mask[0:h, 0:0 + w // 2]
        right = mask[0:h, w // 2:]
        left_pixels = cv2.countNonZero(left)
        right_pixels = cv2.countNonZero(right)
        return 0 if left_pixels >= right_pixels else 270

        # Vertical
    else:
        top = mask[0:h // 2, 0:w]
        bottom = mask[h // 2:, 0:w]
        top_pixels = cv2.countNonZero(top)
        bottom_pixels = cv2.countNonZero(bottom)
        return 90 if bottom_pixels >= top_pixels else 180


def rotate_image(img, center=None, scale=1.0):
    angle = detect_angle(img)

    (h, w) = img.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Rotate image to 90 degrees (Portrait)
    if angle == 90:
        # Return the image
        return img
    elif angle == 0:
        # Perform the rotation
        M = cv2.getRotationMatrix2D(center, 90, scale)
        rotated = cv2.warpAffine(img, M, (w, h))
        return rotated
    elif angle == 270:
        # Perform the rotation
        M = cv2.getRotationMatrix2D(center, -90, scale)
        rotated = cv2.warpAffine(img, M, (w, h))
        return rotated
    elif angle == 180:
        # Perform the rotation
        M = cv2.getRotationMatrix2D(center, 180, scale)
        rotated = cv2.warpAffine(img, M, (w, h))
        return rotated