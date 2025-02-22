import cv2
import numpy as np
import  os

def read_circles_and_image_size(filename):
    circles = []
    with open(filename, 'r') as file:
        for line in file:
            x, y, r, img_w, img_h = map(float, line.strip().split(','))
            circles.append((x, y, r, img_w, img_h))
    return circles


def circle_to_points(x, y, r, num_points=20):
    theta = np.linspace(0, 2 * np.pi, num_points)
    x_circle = x + r * np.cos(theta)
    y_circle = y + r * np.sin(theta)
    return np.vstack((x_circle, y_circle)).astype(np.int32).T


def closest_point_index(points, target):
    distances = np.linalg.norm(points - target, axis=1)
    return np.argmin(distances)


def compute_polygon(c1, c2, num_points=20):
    x1, y1, r1, _, _ = c1
    x2, y2, r2, _, _ = c2

    # Compute points on each circle
    points1 = circle_to_points(x1, y1, r1, num_points)
    points2 = circle_to_points(x2, y2, r2, num_points)

    # Select a start point from the first circle
    start_point = points1[0]

    # Sort the points of the first circle in a clockwise order
    angles1 = np.arctan2(points1[:, 1] - y1, points1[:, 0] - x1)
    sorted_indices1 = np.argsort(angles1)
    sorted_points1 = points1[sorted_indices1]

    # Find the closest point in the second circle
    closest_index = closest_point_index(points2, start_point)

    # Sort the points of the second circle in a counter-clockwise order from the closest point
    angles2 = np.arctan2(points2[:, 1] - y2, points2[:, 0] - x2)
    sorted_indices2 = np.argsort(-angles2)  # Reverse order for counter-clockwise
    sorted_points2 = points2[sorted_indices2]

    # Rotate sorted_points2 to start from the closest point
    sorted_points2 = np.roll(sorted_points2, -closest_index, axis=0)

    # Combine the points to form the polygon
    polygon = np.vstack((sorted_points1, sorted_points2))

    return polygon


def normalize_points(points, img_w, img_h):
    # Normalize points to be in the range [0, 1] relative to image width and height
    return points / np.array([img_w, img_h])


def plot_polygons(circles, polygons, image_size=(600, 600)):
    image = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)

    for x, y, r, _, _ in circles:
        center = (int(x), int(y))
        radius = int(r)
        cv2.circle(image, center, radius, (255, 0, 0), 1)  # Draw circle in red

    for poly in polygons:
        poly = np.int32(poly)
        cv2.polylines(image, [poly], isClosed=True, color=(0, 255, 0), thickness=1)  # Draw polygon in green

    image_show=cv2.resize(image,(1024,1024))
    cv2.imshow('Circles and Polygons', image_show)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def write_polygons_to_file(polygons, filename, img_w, img_h):
    with open(filename, 'w') as file:
        for poly in polygons:
            normalized_poly = normalize_points(poly, img_w, img_h)
            # Create a string with '0' followed by space-separated coordinates
            line = '0 ' + ' '.join(f"{x:.6f} {y:.6f}" for x, y in normalized_poly)
            file.write(line + '\n')


def process_file():
    filename = '../demo/HS_image/105.txt'
    output_filename = '../demo/HS_image/labels/105.txt'

    circles = read_circles_and_image_size(filename)
    polygons = []

    for i in range(0, len(circles), 2):
        c1 = circles[i]
        c2 = circles[i + 1]
        polygon = compute_polygon(c1, c2)
        polygons.append(polygon)

    # Get image dimensions from the first circle entry
    img_w, img_h = circles[0][3], circles[0][4]

    plot_polygons(circles, polygons, image_size=(int(img_w), int(img_h)))
    write_polygons_to_file(polygons, output_filename, img_w, img_h)


def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)

            circles = read_circles_and_image_size(input_file)
            polygons = []

            for i in range(0, len(circles), 2):
                c1 = circles[i]
                c2 = circles[i + 1]
                polygon = compute_polygon(c1, c2)
                polygons.append(polygon)

            # Get image dimensions from the first circle entry
            img_w, img_h = circles[0][3], circles[0][4]

            # Plot polygons (optional)
            plot_polygons(circles, polygons, image_size=(int(img_w), int(img_h)))

            # Write polygons to the output file
            write_polygons_to_file(polygons, output_file, img_w, img_h)


if __name__ == '__main__':
    input_folder = './projects/ZZL_seg/datasets/images/labels_circle'
    output_folder = './projects/ZZL_seg/datasets/labels'
    process_folder(input_folder, output_folder)
#