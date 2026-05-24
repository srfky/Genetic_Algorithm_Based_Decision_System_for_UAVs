#4 images merge

import cv2
import numpy as np

images = [cv2.imread(f'Autonomous task codes\imagesphotograph-{i}.jpg') for i in range(1, 5)]

grays = [cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) for img in images]

orb = cv2.ORB_create()

homographies = []

base_img = images[0]

for i in range(1, 4):
    # Identify features and calculate descriptors
    keypoints_base, descriptors_base = orb.detectAndCompute(grays[i-1], None)
    keypoints_next, descriptors_next = orb.detectAndCompute(grays[i], None)

    # Match using BFMatcher
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(descriptors_base, descriptors_next)

    # Choose good matches
    good_matches = [m for m in matches if m.distance < 0.7 * max(len(matches), 1)]

    # Get the corresponding points
    src_pts = np.float32([keypoints_base[m.queryIdx].pt for m in good_matches])
    dst_pts = np.float32([keypoints_next[m.trainIdx].pt for m in good_matches])

    # Calculate the homography matrix.
    H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC)
    homographies.append(H)

    # Update the merged image.
    base_img = cv2.warpPerspective(base_img, H, (base_img.shape[1] + images[i].shape[1], base_img.shape[0]))
    base_img[0:images[i].shape[0], 0:images[i].shape[1]] = images[i]

# Show the combined panorama.
cv2.imshow('Panorama', base_img)
cv2.waitKey(0)
cv2.destroyAllWindows()