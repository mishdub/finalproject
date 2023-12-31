from Draw import Draw
import math
from shapely.geometry import Polygon, MultiPolygon, LineString, Point,MultiPoint,MultiLineString
from shapely.ops import unary_union
from shapely.ops import nearest_points
from scipy.spatial import ConvexHull
from math import cos, sin, radians
from alphashape import alphashape





import time
import warnings
import copy
import sympy as sp
import numpy as np

from decimal import Decimal, getcontext


class Algo17:

    def __init__(self, container_instance, item_instances):
        self.container_instance = container_instance
        self.item_instances = item_instances
        warnings.showwarning = self.warning_handler
        self.error_occurred = False  # Initialize error_occurred as False
        # Define a warning handler to print warnings

    def calculate_angle(self, point, centroid):
        return (math.atan2(point[1] - centroid[1], point[0] - centroid[0]) + 2 * math.pi) % (2 * math.pi)

    def is_counterclockwise(self, coordinates):
        # Calculate the centroid
        centroid_x = sum(x[0] for x in coordinates) / len(coordinates)
        centroid_y = sum(x[1] for x in coordinates) / len(coordinates)
        centroid = (centroid_x, centroid_y)

        # Sort the coordinates based on angles
        sorted_coordinates = sorted(coordinates, key=lambda point: self.calculate_angle(point, centroid))

        # Check if the sorted coordinates are in counterclockwise order
        for i in range(len(sorted_coordinates) - 1):
            x1, y1 = sorted_coordinates[i]
            x2, y2 = sorted_coordinates[i + 1]
            cross_product = (x2 - x1) * (y2 + y1)
            if cross_product <= 0:
                return False

        return True

    def order_coordinates_counterclockwise(self, coordinates):
        """
        if self.is_counterclockwise(coordinates):
            print("orderd")
            return coordinates
        """
        # Calculate the centroid
        centroid_x = sum(x[0] for x in coordinates) / len(coordinates)
        centroid_y = sum(x[1] for x in coordinates) / len(coordinates)
        centroid = (centroid_x, centroid_y)

        # Sort the coordinates based on angles
        sorted_coordinates = sorted(coordinates, key=lambda point: self.calculate_angle(point, centroid))

        return sorted_coordinates

    def move_poly(self, polygon, angle, convex_region):
        # go over the front points of the polygon and crete lines from them in the direction and
        # check for intresection point in the all convex region
        list_of_points = []
        dime = self.container_instance.calculate_total_dimensions()
        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        min_distance = float('inf')
        from_p = None
        to_p = None
        for point in polygon.coordinates:
            x, y = point
            x1, y1 = self.calculate_endpoint_from_direction(x, y, vx, vy, dime)
            line = LineString([(x, y), (x1, y1)])
            if not line.crosses(Polygon(polygon.coordinates)):
                list_of_points.append(point)
                inter_x, inter_y = self.find_intersection_point(convex_region, [(x, y), (x1, y1)], (x, y))
                p1 = Point(x, y)
                p2 = Point(inter_x, inter_y)
                distance = p1.distance(p2)
                if distance < min_distance:
                    min_distance = distance
                    from_p = point
                    to_p = (inter_x, inter_y)
        return from_p, to_p

    def move_poly_LineString(self, polygon, angle, line_st):
        # go over the front points of the polygon and crete lines from them in the direction and
        # check for intresection point in a specific region (line string)
        list_of_lines = []
        list_of_lines.append(line_st)
        line_st = LineString(line_st)
        dime = self.container_instance.calculate_total_dimensions()
        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        min_distance = float('inf')
        from_p = None
        to_p = None
        list_of_points = []
        for point in polygon.coordinates:
            x, y = point
            x1, y1 = self.calculate_endpoint_from_direction(x, y, vx, vy, dime)
            line = LineString([(x, y), (x1, y1)])
            if not line.crosses(Polygon(polygon.coordinates)):
                list_of_lines.append([(x, y), (x1, y1)])
                in_po = self.find_intersection_point_linestring(line_st, [(x, y), (x1, y1)], (x, y))
                if in_po is not None:
                    list_of_points.append(in_po)
                    inter_x, inter_y = in_po
                    p1 = Point(x, y)
                    p2 = Point(inter_x, inter_y)
                    distance = p1.distance(p2)
                    if distance == 0:
                        break
                    if distance < min_distance:
                        min_distance = distance
                        from_p = point
                        to_p = (inter_x, inter_y)
        return from_p, to_p, list_of_points, list_of_lines, min_distance

    def move_poly_LineString2(self, polygon, angle, line_st):
        # go over all the points of the line string and create lines from them and check intresections in the polygon
        list_of_lines = []
        angle = (angle + 180) % 360
        dime = self.container_instance.calculate_total_dimensions()
        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        min_distance = float('inf')
        from_p = None
        to_p = None
        list_of_points = []
        for point_line in line_st.coords:
            xl, yl = point_line
            x1, y1 = self.calculate_endpoint_from_direction(xl, yl, vx, vy, dime)
            p = self.find_intersection_point2(polygon.coordinates, [(xl, yl), (x1, y1)], (xl, yl))
            if p is not None:
                inx, iny = p
                p1 = Point(xl, yl)
                p2 = Point(inx, iny)
                list_of_points.append((xl, yl))
                list_of_points.append((inx, iny))
                distance = p1.distance(p2)
                if distance < min_distance:
                    min_distance = distance
                    from_p = (inx, iny)
                    to_p = (xl, yl)
        return from_p, to_p, list_of_points, list_of_lines, min_distance

    def move_poly_MultiLineString(self, polygon, angle, MultiLineString):
        list_of_lines = []
        dime = self.container_instance.calculate_total_dimensions()
        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        min_distance = float('inf')
        from_p = None
        to_p = None
        list_of_points = []
        for point in polygon.coordinates:
            x, y = point
            x1, y1 = self.calculate_endpoint_from_direction(x, y, vx, vy, dime)
            line = LineString([(x, y), (x1, y1)])
            if not line.crosses(Polygon(polygon.coordinates)):
                list_of_lines.append([(x, y), (x1, y1)])
                for line_st in MultiLineString:
                    in_po = self.find_intersection_point_linestring(line_st, [(x, y), (x1, y1)], (x, y))
                    if in_po is not None:
                        list_of_points.append(in_po)
                        inter_x, inter_y = in_po
                        p1 = Point(x, y)
                        p2 = Point(inter_x, inter_y)
                        distance = p1.distance(p2)
                        if distance == 0:
                            break
                        if distance < min_distance:
                            min_distance = distance
                            from_p = point
                            to_p = (inter_x, inter_y)

        return from_p, to_p, list_of_points, list_of_lines, min_distance

    def move_poly_MultiLineString2(self, polygon, angle, MultiLineString):
        list_of_lines = []
        angle = (angle + 180) % 360
        dime = self.container_instance.calculate_total_dimensions()
        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        min_distance = float('inf')
        from_p = None
        to_p = None
        list_of_points = []
        for line_st in MultiLineString:
            # list_of_lines.append(line_st.coords)
            for point_line in line_st.coords:
                xl, yl = point_line
                x1, y1 = self.calculate_endpoint_from_direction(xl, yl, vx, vy, dime)
                p = self.find_intersection_point2(polygon.coordinates, [(xl, yl), (x1, y1)], (xl, yl))
                if p is not None:
                    inx, iny = p
                    p1 = Point(xl, yl)
                    p2 = Point(inx, iny)
                    list_of_points.append((xl, yl))
                    # list_of_points.append((inx, iny))
                    distance = p1.distance(p2)
                    if distance < min_distance:
                        min_distance = distance
                        from_p = (inx, iny)
                        to_p = (xl, yl)

        return from_p, to_p, list_of_points, list_of_lines, min_distance

    def place_poly(self, original_polygon, extended_poly, convex_region, angle, right_line, left_line):
        convex_exterior = Polygon(convex_region)
        convex_exterior = convex_exterior.exterior

        f_p = None
        t_p = None
        dis1 = float('inf')
        dis2 = float('inf')
        dis3 = float('inf')
        dis4 = float('inf')
        dis5 = float('inf')
        dis6 = float('inf')
        min_dis_in_multi = float('inf')
        min_dis_in_line = float('inf')
        min_dis_in_multi_and_line = float('inf')

        list_of_lines = []
        list_of_points = []
        list_of_l = []
        if extended_poly.intersects(convex_exterior):
            intersection = extended_poly.intersection(convex_exterior)
            print(intersection.geom_type)

            if intersection.is_empty:
                print("Polygons overlap, but no intersection.")
            else:

                if intersection.geom_type == "LineString":

                    f_p1, t_p1, list_of_points1, list_of_l1, dis1 = self.move_poly_LineString(original_polygon,
                                                                                              angle,
                                                                                              list(intersection.coords))
                    f_p2, t_p2, list_of_points2, list_of_l2, dis2 = self.move_poly_LineString2(original_polygon,
                                                                                               angle,
                                                                                               intersection)
                    if dis1 < dis2:
                        f_p = f_p1
                        t_p = t_p1
                        list_of_l = list_of_l1
                        list_of_points = list_of_points1
                        min_dis_in_line = dis1

                    else:
                        f_p = f_p2
                        t_p = t_p2
                        list_of_l = list_of_l2
                        list_of_points = list_of_points2
                        min_dis_in_line = dis2




                elif intersection.geom_type == "MultiLineString":
                    for line in intersection.geoms:
                        list_of_lines.append(list(line.coords))

                    f_p1, t_p1, list_of_points1, list_of_l1, dis3 = self.move_poly_MultiLineString2(original_polygon,
                                                                                                    angle,
                                                                                                    intersection.geoms)

                    f_p2, t_p2, list_of_points2, list_of_l2, dis4 = self.move_poly_MultiLineString(original_polygon,
                                                                                                   angle,
                                                                                                   intersection.geoms)

                    if dis3 < dis4:
                        f_p = f_p1
                        t_p = t_p1
                        list_of_l = list_of_l1
                        list_of_points = list_of_points1
                        min_dis_in_multi = dis3

                    else:
                        f_p = f_p2
                        t_p = t_p2
                        list_of_l = list_of_l2
                        list_of_points = list_of_points2
                        min_dis_in_multi = dis4

        else:
            print("not intresectino?")

        if min_dis_in_multi < min_dis_in_line:
            min_dis_in_multi_and_line = min_dis_in_multi
        else:
            min_dis_in_multi_and_line = min_dis_in_line

        spoint1 = Point((list(right_line.coords))[0])
        spoint2 = Point((list(left_line.coords))[0])
        right_line = list(right_line.coords)
        pre_point1 = right_line[0]

        left_line = list(left_line.coords)
        pre_point2 = left_line[0]
        point1 = self.find_intersection_point(convex_exterior.coords, right_line, pre_point1)
        point2 = self.find_intersection_point(convex_exterior.coords, left_line, pre_point2)
        point1 = Point(point1)
        point2 = Point(point2)

        dis5 = spoint1.distance(point1)
        dis6 = spoint2.distance(point2)
        if dis5 < dis6:
            if dis5 < min_dis_in_multi_and_line:
                f_p = (spoint1.x, spoint1.y)
                t_p = (point1.x, point1.y)

        else:
            if dis6 < min_dis_in_multi_and_line:
                f_p = (spoint2.x, spoint2.y)
                t_p = (point2.x, point2.y)

        return f_p, t_p, list_of_lines + list_of_l, list_of_points

    def classify_points_left_right1(self, line_angle, line_start, points):
        left_side_points = []
        right_side_points = []

        for point in points:
            # Calculate the angle between the line and the vector from line_start to the point.
            angle_rad = math.atan2(point[1] - line_start[1], point[0] - line_start[0])
            angle_deg = math.degrees(angle_rad)

            # Determine if the point is on the left or right side.
            angle_difference = (angle_deg - line_angle + 360) % 360  # Ensure angle_difference is positive
            if angle_difference < 180:
                left_side_points.append(point)
            else:
                right_side_points.append(point)

        return left_side_points, right_side_points

    def classify_points_left_right2(self, line_angle, line_start, points):
        left_side_points = []
        right_side_points = []

        leftmost_point = None
        rightmost_point = None

        for point in points:
            # Calculate the angle between the line and the vector from line_start to the point.
            angle_rad = math.atan2(point[1] - line_start[1], point[0] - line_start[0])
            angle_deg = math.degrees(angle_rad)

            # Determine if the point is on the left or right side.
            angle_difference = (angle_deg - line_angle + 360) % 360  # Ensure angle_difference is positive
            if angle_difference < 180:
                left_side_points.append(point)
                # Update leftmost_point if the current point is more left.
                if leftmost_point is None or point[0] < leftmost_point[0]:
                    leftmost_point = point
            else:
                right_side_points.append(point)
                # Update rightmost_point if the current point is more right.
                if rightmost_point is None or point[0] > rightmost_point[0]:
                    rightmost_point = point

        return left_side_points, right_side_points, leftmost_point, rightmost_point

    def find_farthest_point_from_line(self, line_coords, points, polygon, vx, vy, dime):
        # Create a LineString object from the line coordinates.
        line = LineString(line_coords)

        max_distance = -1
        farthest_point = None

        pol = Polygon(polygon)

        i = 0
        for point_coords in points:
            # Create a Point object from the point coordinates.
            point = Point(point_coords)

            # Calculate the distance from the point to the line.
            distance = point.distance(line)
            x, y = point_coords
            x1, y1 = self.calculate_endpoint_from_direction(x, y, vx, vy, dime)
            line2 = LineString([(x, y), (x1, y1)])
            if distance > max_distance:
                if not line2.crosses(pol):
                    max_distance = distance
                    farthest_point = point_coords
        return farthest_point

    def find_farthest_point_from_line_temp(self, line_coords, points):
        # Create a LineString object from the line coordinates.
        line = LineString(line_coords)

        max_distance = -1
        farthest_point = None
        for point_coords in points:
            # Create a Point object from the point coordinates.
            point = Point(point_coords)
            # Calculate the distance from the point to the line.
            distance = point.distance(line)
            if distance > max_distance:
                max_distance = distance
                farthest_point = point_coords

        return farthest_point

    def find_farthest_point_from_line_special(self, line_coords, points, polygon, vx, vy, dime, center):
        # Create a LineString object from the line coordinates.
        line = LineString(line_coords)

        max_distance = -1
        farthest_point = None

        pol = Polygon(polygon)
        c_point = Point(center)

        i = 0
        for point_coords in points:
            # Create a Point object from the point coordinates.
            point = Point(point_coords)

            # Calculate the distance from the point to the line.
            distance = point.distance(line)
            x, y = point_coords
            x1, y1 = self.calculate_endpoint_from_direction(x, y, vx, vy, dime)
            line2 = LineString([(x, y), (x1, y1)])
            if distance > max_distance:
                if not line2.crosses(pol):
                    max_distance = distance
                    farthest_point = point_coords

        return farthest_point

    def find_farthest_point_from_line_special2(self, line_coords, points, polygon, vx, vy, dime, center):
        # Create a LineString object from the line coordinates.
        line = LineString(line_coords)

        max_distance = -1
        min_dis = float('inf')
        farthest_point = None
        sec_farthest_point = None

        pol = Polygon(polygon)
        c_point = Point(center)

        i = 0
        for point_coords in points:
            # Create a Point object from the point coordinates.
            point = Point(point_coords)

            # Calculate the distance from the point to the line.
            distance = point.distance(line)
            x, y = point_coords
            x1, y1 = self.calculate_endpoint_from_direction(x, y, vx, vy, dime)
            line2 = LineString([(x, y), (x1, y1)])
            dis = point.distance(c_point)
            if distance > max_distance and dis < min_dis:
                if not line2.crosses(pol):
                    max_distance = distance
                    min_dis = dis
                    farthest_point = point_coords
        return farthest_point

    def calculate_line_angle(self, line):
        # Extract the coordinates of the start and end points of the line
        start_x, start_y = line.coords[0]
        end_x, end_y = line.coords[-1]

        # Calculate the angle in radians
        angle_radians = math.atan2(end_y - start_y, end_x - start_x)

        # Convert the angle from radians to degrees
        angle_degrees = math.degrees(angle_radians)

        return angle_degrees

    def placement(self, angle, middle_polygon, convex_polygon):
        dime = self.container_instance.calculate_total_dimensions()
        center = self.calculate_centroid(middle_polygon)
        cx, cy = center

        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        left, right = self.classify_points_left_right1(angle, center, middle_polygon)

        x1, y1 = self.calculate_endpoint_from_direction(cx, cy, vx, vy, dime)

        line1 = [(cx, cy), (x1, y1)]

        px1, py1 = self.find_farthest_point_from_line(line1, right, middle_polygon, vx, vy, dime)
        px2, py2 = self.find_farthest_point_from_line(line1, left, middle_polygon, vx, vy, dime)

        p1 = self.calculate_endpoint_from_direction(px1, py1, vx, vy, dime)
        p2 = self.calculate_endpoint_from_direction(px2, py2, vx, vy, dime)

        right_line = LineString([(px1, py1), p1])
        left_line = LineString([(px2, py2), p2])

        filled_polygon = Polygon(list(left_line.coords) + list(right_line.coords)[::-1])

        flag = False
        pol = Polygon(convex_polygon.coordinates)
        pol = pol.buffer(0.1)

        if not (filled_polygon.intersects(pol)):
            flag = True
        return flag, (px1, py1), p1, (px2, py2), p2, (cx, cy), (x1, y1), filled_polygon, right_line, left_line

    def placement2(self, angle, middle_polygon, convex_polygon):
        middle_polygon = (Polygon(middle_polygon)).buffer(0.1)
        middle_polygon = middle_polygon.exterior.coords
        dime = self.container_instance.calculate_total_dimensions()
        center = self.calculate_centroid(middle_polygon)
        cx, cy = center
        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        left, right = self.classify_points_left_right1(angle, center, middle_polygon)

        x1, y1 = self.calculate_endpoint_from_direction(cx, cy, vx, vy, dime)

        line1 = [(cx, cy), (x1, y1)]

        px1, py1 = self.find_farthest_point_from_line(line1, right, middle_polygon, vx, vy, dime)
        px2, py2 = self.find_farthest_point_from_line(line1, left, middle_polygon, vx, vy, dime)

        p1 = self.calculate_endpoint_from_direction(px1, py1, vx, vy, dime)
        p2 = self.calculate_endpoint_from_direction(px2, py2, vx, vy, dime)

        right_line = LineString([(px1, py1), p1])
        left_line = LineString([(px2, py2), p2])

        filled_polygon = Polygon(list(left_line.coords) + list(right_line.coords)[::-1])

        flag = False
        pol = Polygon(convex_polygon.coordinates)
        pol = pol.buffer(0.1)

        if not (filled_polygon.intersects(pol)):
            flag = True
        return flag, (px1, py1), p1, (px2, py2), p2, (cx, cy), (x1, y1), filled_polygon, right_line, left_line

    def placement3(self, angle, middle_polygon, convex_region, dist, the_dist):
        center = self.calculate_centroid(middle_polygon)
        cx, cy = center

        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        left, right = self.classify_points_left_right1(angle, center, middle_polygon)

        x1, y1 = self.calculate_endpoint_from_direction(cx, cy, vx, vy, dist)

        line1 = [(cx, cy), (x1, y1)]

        px1, py1 = self.find_farthest_point_from_line(line1, right, middle_polygon, vx, vy, the_dist)
        px2, py2 = self.find_farthest_point_from_line(line1, left, middle_polygon, vx, vy, the_dist)

        p1 = self.calculate_endpoint_from_direction(px1, py1, vx, vy, dist)
        p2 = self.calculate_endpoint_from_direction(px2, py2, vx, vy, dist)

        right_line = LineString([(px1, py1), p1])
        left_line = LineString([(px2, py2), p2])

        filled_polygon = Polygon(list(left_line.coords) + list(right_line.coords)[::-1])

        flag = False
        pol = Polygon(convex_region).exterior

        if not (filled_polygon.intersects(pol)):
            flag = True
        return flag, (px1, py1), p1, (px2, py2), p2, (cx, cy), (x1, y1), filled_polygon, right_line, left_line

    def extend_pol(self, angle, convex_region, polygon):
        dime = self.container_instance.calculate_total_dimensions()
        center = self.calculate_centroid(polygon.coordinates)
        cx, cy = center

        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        left, right = self.classify_points_left_right1(angle, center, polygon.coordinates)

        x1, y1 = self.calculate_endpoint_from_direction(cx, cy, vx, vy, dime)
        line1 = [(cx, cy), (x1, y1)]

        px1, py1 = self.find_farthest_point_from_line(line1, right, polygon.coordinates, vx, vy, dime)
        px2, py2 = self.find_farthest_point_from_line(line1, left, polygon.coordinates, vx, vy, dime)


        p1 = self.calculate_endpoint_from_direction(px1, py1, vx, vy, dime)
        p2 = self.calculate_endpoint_from_direction(px2, py2, vx, vy, dime)

        int_point1 = self.find_intersection_point(convex_region, [(px1, py1), p1],(px1, py1))

        if int_point1 is None:
            int_point1 = px1, py1
            px, py = int_point1
        else:
            px, py = int_point1

        int_point2 = self.find_intersection_point(convex_region, [(px2, py2), p2],
                                                  (px2, py2))

        if int_point2 is None:
            int_point2 = px2, py2
            qx, qy = int_point2
        else:
            qx, qy = int_point2

        pol_coord = [(px1, py1), (px, py), (qx, qy), (px2, py2)]
        order_coordinates = self.order_coordinates_counterclockwise(pol_coord)
        pol = Polygon(order_coordinates)
        origin_pol = Polygon(polygon.coordinates)
        mergedPolys = unary_union([origin_pol, pol])
        exterior_coords_list = []
        if isinstance(mergedPolys, MultiPolygon):
            # Iterate through the constituent polygons
            for polygon in mergedPolys.geoms:
                # Get the coordinates of the exterior boundary of each polygon
                exterior_coords = list(polygon.exterior.coords)
                # Append them to the exterior_coords_list
                exterior_coords_list.extend(exterior_coords)
        else:
            # If it's a single Polygon, get its exterior coordinates directly
            exterior_coords_list = list(mergedPolys.exterior.coords)

        return exterior_coords_list

    def check_ep(self, angle, p, convex_center):
        new_pol = Polygon(p.coordinates)
        new_pol = new_pol.buffer(0.1)
        copied = copy.deepcopy(p)
        list_of = list(new_pol.exterior.coords)
        copied.set_coordinates(list_of)
        dime = self.container_instance.calculate_total_dimensions()
        center = self.calculate_centroid(copied.coordinates)
        cx, cy = center

        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        left, right = self.classify_points_left_right1(angle, center, copied.coordinates)

        ops_angle = (angle + 180) % 360

        vx2, vy2 = (
            math.cos(math.radians(ops_angle)), math.sin(math.radians(ops_angle)))

        x4, y4 = self.calculate_endpoint_from_direction(cx, cy, vx2, vy2, dime)

        x1, y1 = self.calculate_endpoint_from_direction(cx, cy, vx, vy, dime)
        line1 = [(cx, cy), (x4, y4)]
        po1 = self.find_farthest_point_from_line_special(line1, right, copied.coordinates, vx2, vy2, dime,
                                                         convex_center)
        qo1 = self.find_farthest_point_from_line_special2(line1, right, copied.coordinates, vx2, vy2, dime,
                                                          convex_center)

        po2 = self.find_farthest_point_from_line_special(line1, left, copied.coordinates, vx2, vy2, dime, convex_center)
        qo2 = self.find_farthest_point_from_line_special2(line1, left, copied.coordinates, vx2, vy2, dime,
                                                          convex_center)

        (px1, py1) = po1
        (qx1, qy1) = qo1
        (px2, py2) = po2
        (qx2, qy2) = qo2
        p1 = self.calculate_endpoint_from_direction(px1, py1, vx, vy, dime)
        p2 = self.calculate_endpoint_from_direction(px2, py2, vx, vy, dime)

        the_point = None
        right_angle = self.calculate_angle_in_degrees((px1, py1), p1)
        left_angle = self.calculate_angle_in_degrees((px2, py2), p2)
        right_angle = (right_angle % 360)
        left_angle = (left_angle % 360)

        if right_angle > left_angle:
            the_point = (px1, py1)
        else:
            the_point = (px2, py2)

        return (px2, py2), (qx2, qy2), left

    def check_ep2(self, angle, middle_polygon, center, polygon):
        dime = self.container_instance.calculate_total_dimensions()
        vx, vy = (
            math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        left, right = self.classify_points_left_right1(angle, center, middle_polygon)
        center = self.calculate_centroid(polygon.coordinates)
        cx, cy = center

        x1, y1 = self.calculate_endpoint_from_direction(cx, cy, vx, vy, dime)
        line1 = [(cx, cy), (x1, y1)]
        po1 = self.find_farthest_point_from_line(line1, right, polygon, vx, vy, dime)

        return po1

    def extend_pol_for_first_time(self, angle, polygon, center):
        dime = self.container_instance.calculate_total_dimensions()
        cx, cy = center

        vx, vy = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        left, right = self.classify_points_left_right1(angle, center, polygon.coordinates)

        x1, y1 = self.calculate_endpoint_from_direction(cx, cy, vx, vy, dime)
        line1 = [(cx, cy), (x1, y1)]

        px1, py1 = self.find_farthest_point_from_line(line1, right, polygon.coordinates, vx, vy, dime)
        px2, py2 = self.find_farthest_point_from_line(line1, left, polygon.coordinates, vx, vy, dime)

        p1 = self.calculate_endpoint_from_direction(px1, py1, vx, vy, dime)
        p2 = self.calculate_endpoint_from_direction(px2, py2, vx, vy, dime)

        right_line = LineString([(px1, py1), p1])
        left_line = LineString([(px2, py2), p2])

        filled_polygon = Polygon(list(left_line.coords) + list(right_line.coords)[::-1])

        return filled_polygon, right_line, left_line


    def extend_pol_for_first_time2(self, angle, polygon, center):
        polygon = (Polygon(polygon.coordinates)).buffer(0.1)
        polygon = polygon.exterior.coords
        dime = self.container_instance.calculate_total_dimensions()
        cx, cy = center

        vx, vy = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
        left, right = self.classify_points_left_right1(angle, center, polygon)

        x1, y1 = self.calculate_endpoint_from_direction(cx, cy, vx, vy, dime)
        line1 = [(cx, cy), (x1, y1)]

        px1, py1 = self.find_farthest_point_from_line(line1, right, polygon, vx, vy, dime)
        px2, py2 = self.find_farthest_point_from_line(line1, left, polygon, vx, vy, dime)

        p1 = self.calculate_endpoint_from_direction(px1, py1, vx, vy, dime)
        p2 = self.calculate_endpoint_from_direction(px2, py2, vx, vy, dime)

        right_line = LineString([(px1, py1), p1])
        left_line = LineString([(px2, py2), p2])

        filled_polygon = Polygon(list(left_line.coords) + list(right_line.coords)[::-1])

        return filled_polygon, right_line, left_line

    def find_intersection_point(self, polygon_coordinates, line_coords, po):
        # Create a polygon from the given coordinates

        polygon = Polygon(polygon_coordinates)

        exterior_ring = polygon.exterior

        # Create a LineString from the given line coordinates
        line = LineString(line_coords)

        # Find the intersection between the line and the polygon
        intersection = line.intersection(exterior_ring)

        # Check the type of the result to handle different cases
        if intersection.is_empty:
            print("beacuse empty")
            return None  # No intersection
        elif intersection.geom_type == 'Point':
            # Only one intersection point
            return (intersection.x, intersection.y)
        elif intersection.geom_type == 'MultiPoint':
            # Multiple intersection points
            closest_point = None
            min_distance = float('inf')
            given_point = Point(po)
            for point in intersection.geoms:
                distance = given_point.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = point

            # Find the closest point
            return closest_point.x, closest_point.y
        else:
            # Other types of intersections (e.g., LineString, MultiLineString)
            return None  # Handle as needed

    def find_intersection_point2(self, polygon_coordinates, line_coords, po):
        # Create a polygon from the given coordinates

        polygon = Polygon(polygon_coordinates)

        exterior_ring = polygon.exterior

        # Create a LineString from the given line coordinates
        line = LineString(line_coords)

        # Find the intersection between the line and the polygon
        intersection = line.intersection(exterior_ring)

        # Check the type of the result to handle different cases

        if intersection.is_empty:
            return None  # No intersection
        elif intersection.geom_type == 'Point':
            # Only one intersection point
            return (intersection.x, intersection.y)
        elif intersection.geom_type == 'MultiPoint':
            # Multiple intersection points
            closest_point = None
            min_distance = float('inf')
            given_point = Point(po)
            for point in intersection.geoms:
                distance = given_point.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = point
                    # Find the closest point
            return closest_point.x, closest_point.y
        elif intersection.geom_type == 'LineString':
            # Multiple intersection points
            closest_point = None
            min_distance = float('inf')
            given_point = Point(po)
            for point in list(intersection.coords):
                point = Point(point)
                distance = given_point.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = point
                    # Find the closest point
            return closest_point.x, closest_point.y

        else:
            print(intersection.geom_type)

            # Other types of intersections (e.g., LineString, MultiLineString)
            return None  # Handle as needed

    def find_intersection_point_special(self, polygon_coordinates, line_coords, po):
        # Create a polygon from the given coordinates

        polygon = Polygon(polygon_coordinates)
        polygon = polygon.buffer(0.1)

        exterior_ring = polygon.exterior

        # Create a LineString from the given line coordinates
        line = LineString(line_coords)

        # Find the intersection between the line and the polygon
        intersection = line.intersection(exterior_ring)

        # Check the type of the result to handle different cases
        if intersection.is_empty:
            print("beacuse empty")
            return None  # No intersection
        elif intersection.geom_type == 'Point':
            # Only one intersection point
            return (intersection.x, intersection.y)
        elif intersection.geom_type == 'MultiPoint':
            # Multiple intersection points
            closest_point = None
            min_distance = float('inf')
            given_point = Point(po)
            for point in intersection.geoms:
                distance = given_point.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = point

            # Find the closest point
            return closest_point.x, closest_point.y
        else:
            # Other types of intersections (e.g., LineString, MultiLineString)
            return None  # Handle as needed

    def find_intersection_point_linestring(self, line_string, line_coords, po):
        # Create a polygon from the given coordinates

        # Create a LineString from the given line coordinates
        line = LineString(line_coords)

        # Find the intersection between the line and the polygon
        intersection = line.intersection(line_string)

        # Check the type of the result to handle different cases

        if intersection.is_empty:
            return None  # No intersection
        elif intersection.geom_type == 'Point':
            # Only one intersection point
            return (intersection.x, intersection.y)
        elif intersection.geom_type == 'MultiPoint':
            # Multiple intersection points
            closest_point = None
            min_distance = float('inf')
            given_point = Point(po)
            for point in intersection.geoms:
                distance = given_point.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = point
                    # Find the closest point
            return closest_point.x, closest_point.y
        elif intersection.geom_type == 'LineString':
            # Multiple intersection points
            closest_point = None
            min_distance = float('inf')
            given_point = Point(po)
            for point in list(intersection.coords):
                point = Point(point)
                distance = given_point.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = point
                    # Find the closest point
            return closest_point.x, closest_point.y

        else:
            print(intersection.geom_type)

            # Other types of intersections (e.g., LineString, MultiLineString)
            return None  # Handle as needed


    def calculate_endpoint_from_direction(self, x1, y1, dx, dy, length):
        # Calculate the end point
        x2 = x1 + length * dx
        y2 = y1 + length * dy

        return x2, y2

    def calculate_endpoint_from_rounded_angle(self, x1, y1, desired_angle, length, precision=6):
        # Calculate the end point
        angle = math.atan2(y1, x1)
        current_angle = math.degrees(angle)  # Convert to degrees

        # Find the difference between the desired angle and the current angle
        angle_difference = desired_angle - current_angle

        # Round the angle difference to the specified precision
        rounded_angle_difference = round(angle_difference, precision)

        # Calculate the adjusted endpoint using the rounded angle difference
        adjusted_angle = math.radians(current_angle + rounded_angle_difference)
        dx = math.cos(adjusted_angle)
        dy = math.sin(adjusted_angle)

        x2 = x1 + length * dx
        y2 = y1 + length * dy

        return x2, y2

    def calculate_width_and_height(self, coordinates):
        if len(coordinates) < 2:
            raise ValueError("A polygon must have at least 2 vertices to calculate width and height.")

        # Initialize with the coordinates of the first vertex.
        min_x, max_x = coordinates[0][0], coordinates[0][0]
        min_y, max_y = coordinates[0][1], coordinates[0][1]

        # Iterate through the remaining vertices to find the bounding box.
        for x, y in coordinates:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        width = max_x - min_x
        height = max_y - min_y

        return min(width, height)

    def find_closest_point_to_point(self, polygon, target_point):
        # Initialize variables to keep track of the closest point and its distance
        closest_point = polygon.coordinates[0]
        closest_distance = math.dist(polygon.coordinates[0], target_point)  # Using the 'math.dist' function

        # Find the point in the polygon closest to the target point
        j = 0
        index = 0
        for polygon_point in polygon.coordinates:
            distance_to_target = math.dist(polygon_point, target_point)
            if distance_to_target < closest_distance:
                closest_distance = distance_to_target
                closest_point = polygon_point
                index = j
            j = j + 1

        return index, closest_point

    def for_edges_that_intersect(self, pol1, pol2):
        buffered_result = pol2.buffer(0.1)

        mergedPolys = pol1.difference(buffered_result)
        # print("before",mergedPolys)

        exterior_coords_list = []
        if isinstance(mergedPolys, MultiPolygon):
            largest_polygon = None
            largest_area = 0
            # Iterate through the constituent polygons
            for polygon in mergedPolys.geoms:
                # Get the coordinates of the exterior boundary of each polygon
                if isinstance(polygon, Polygon):
                    # Calculate the area of the polygon
                    area = polygon.area
                    if area > largest_area:
                        largest_area = area
                        largest_polygon = polygon
            return list(largest_polygon.exterior.coords)

        else:
            # If it's a single Polygon, get its exterior coordinates directly
            return list(mergedPolys.exterior.coords)

    def calculate_next_angle(self, current_angle, inc):
        threshold = self.container_instance.calculate_distance_threshold()
        dx, dy = (
            math.cos(math.radians(current_angle)), math.sin(math.radians(current_angle)))

        # pol_area = current_polygon.calculate_total_dimensions()
        # next_pol_area = next_polygon.calculate_total_dimensions()
        convex_area = self.container_instance.calculate_total_dimensions()
        # Calculate the distance adjustment based on both width and height
        distance = inc

        radius = math.sqrt(dx ** 2 + dy ** 2)
        new_angle = current_angle + math.atan2(dy, dx) + (distance / radius)

        # Ensure the angle is within [0, 360] degrees
        return new_angle

    def warning_handler(self, message, category, filename, lineno, file=None, line=None):
        self.error_occurred = True
        print(f"Warning: {category.__name__}: {message}")

    def calculate_angle_in_degrees(self, point, centroid):
        angle_radians = math.atan2(centroid[1] - point[1], centroid[0] - point[0])
        angle_degrees = math.degrees(angle_radians)
        return angle_degrees

    def check_if_line_cross(self, convex_polygon, polygon):
        new_list = []
        pol = Polygon(polygon.coordinates)
        center_con = self.calculate_centroid(convex_polygon.coordinates)

        for point in polygon.coordinates:
            line = LineString([center_con, point])
            if not line.crosses(pol):
                if point not in new_list:
                    new_list.append(point)
        return new_list

    def calculate_centroid(self, coords):
        # Create a convex polygon from the given coordinates
        convex_polygon = Polygon(coords)

        # Calculate the centroid of the convex polygon
        centroid = convex_polygon.centroid

        return centroid.x, centroid.y

    def create_lines(self, vertices):
        # Find the center of the convex region
        center_x, center_y = self.calculate_centroid(vertices)

        # Find the minimum and maximum coordinates
        min_x, min_y = min(x for x, y in vertices), min(y for x, y in vertices)
        max_x, max_y = max(x for x, y in vertices), max(y for x, y in vertices)



        # Create LineString objects for the vertical and horizontal lines
        vertical_line = LineString([(center_x, min_y), (center_x, max_y)])
        horizontal_line = LineString([(min_x, center_y), (max_x, center_y)])

        return [(center_x, min_y), (center_x, max_y)], [(min_x, center_y), (max_x, center_y)]

    def create_lines2(self, vertices):
        # Find the center of the convex region
        center_x, center_y = self.calculate_centroid(vertices)

        # Find the minimum and maximum coordinates
        min_x, min_y = min(x for x, y in vertices), min(y for x, y in vertices)
        max_x, max_y = max(x for x, y in vertices), max(y for x, y in vertices)

        # Calculate midpoints
        vertical_midpoint = (center_x, (min_y + max_y) / 2)
        horizontal_midpoint = ((min_x + max_x) / 2, center_y)

        # Calculate half the length
        half_length_x = (max_x - min_x) / 3  # Dividing by 4 to get half of the original length
        half_length_y = (max_y - min_y) / 3

        # Create LineString objects for the lines with half the length
        vertical_line = LineString([(center_x, center_y - half_length_y), (center_x, center_y + half_length_y)])
        horizontal_line = LineString([(center_x - half_length_x, center_y), (center_x + half_length_x, center_y)])

        return list(vertical_line.coords), list(horizontal_line.coords)

    def find_points_that_intersect(self, left_line, right_line,convex_region):
        pol = convex_region
        left = list(left_line.coords)
        right = list(right_line.coords)
        l_p = self.find_intersection_point(pol, left, left[0])
        r_p = self.find_intersection_point(pol, right, right[0])
        return l_p, r_p

    def point_line_projection_shapely(self, point, line):
        # Create Shapely Point and LineString objects
        shapely_point = Point(point)
        shapely_line = LineString(line)

        # Project the point onto the line
        nearest_point = shapely_line.interpolate(shapely_line.project(shapely_point))

        return nearest_point.x, nearest_point.y


    def point_polygon_projection_shapely(self, point, polygon):
        # Create Shapely Point and Polygon objects
        shapely_point = Point(point)
        shapely_polygon = Polygon(polygon.coordinates)

        # Project the point onto the polygon
        nearest_point = shapely_polygon.exterior.interpolate(shapely_polygon.exterior.project(shapely_point))

        return nearest_point.x, nearest_point.y

    def find_perpendicular_point_on_convex_region(self,A, convex_region):
        # A is a tuple of the form (x, y)
        # convex_region is a list of tuples representing the convex region vertices

        # Find the closest vertex to point A in the convex region
        closest_vertex = min(convex_region, key=lambda vertex: np.linalg.norm(np.array(vertex) - np.array(A)))

        # Calculate the slope of AB
        slope_AB = (closest_vertex[1] - A[1]) / (closest_vertex[0] - A[0])

        # Calculate the perpendicular slope
        slope_perpendicular = -1 / slope_AB

        # Calculate the coordinates of point C
        xC = A[0] + 1  # You can choose any arbitrary x-coordinate for C
        yC = slope_perpendicular * (xC - A[0]) + A[1]

        # Return the coordinates of point C
        return xC, yC

    def find_perpendicular_point_on_convex_region2(self, A, convex_region):
        # A is a tuple of the form (x, y)
        # convex_region is a list of tuples representing the convex region vertices

        # Find the convex hull of the convex region
        convex_hull = Polygon(convex_region).convex_hull

        # Find the closest vertex to point A in the convex region
        closest_vertex = min(convex_region, key=lambda vertex: np.linalg.norm(np.array(vertex) - np.array(A)))

        # Calculate the slope of AB
        slope_AB = (closest_vertex[1] - A[1]) / (closest_vertex[0] - A[0])

        # Create a LineString object representing the line passing through A and the closest vertex
        line_AB = LineString([A, closest_vertex])

        # Find the intersection point of the line AC with the convex hull
        intersection_point = line_AB.intersection(convex_hull)

        # Check if there is an intersection point
        if intersection_point.is_empty or not isinstance(intersection_point, Point):
            # Return the original point A if there is no intersection or if the intersection is not a point
            return A

        # Find the tangent vector to the convex hull at the point of intersection
        tangent_vector = np.array([1, slope_AB])
        tangent_vector /= np.linalg.norm(tangent_vector)

        # Adjust point C along the tangent vector to ensure perpendicularity
        adjusted_intersection = Point(np.array(intersection_point.xy) + 2 * tangent_vector)

        # Return the coordinates of the adjusted intersection point
        return adjusted_intersection.xy[0][0], adjusted_intersection.xy[1][0]

    def find_perpendicular_point_on_convex_region4(self, A, convex_region):
        # A is a tuple of the form (x, y)
        # convex_region is a list of tuples representing the convex region vertices

        # Find the closest vertex to point A in the convex region
        closest_vertex = min(convex_region, key=lambda vertex: np.linalg.norm(np.array(vertex) - np.array(A)))

        # Calculate the slope of AB
        slope_AB = (closest_vertex[1] - A[1]) / (closest_vertex[0] - A[0])

        # Handle the case of an infinite slope
        if np.isinf(slope_AB):
            # If the slope is infinite, xC is the same as A[0]
            xC = A[0]
            # Choose any arbitrary y-coordinate for C
            yC = A[1] + 1
        else:
            # Calculate the perpendicular slope
            slope_perpendicular = -1 / slope_AB
            # Calculate the coordinates of point C
            xC = A[0] + 1  # You can choose any arbitrary x-coordinate for C
            yC = slope_perpendicular * (xC - A[0]) + A[1]

        # Return the coordinates of point C
        return xC, yC

    def find_point_C(self,point_A, convex_region_coordinates):
        # Find the convex hull of the region
        hull = ConvexHull(convex_region_coordinates)

        # Find the centroid of the convex region
        centroid = np.mean(convex_region_coordinates, axis=0)

        # Choose a point C on the line passing through the centroid and point A
        vector_AC = np.array(point_A) - centroid
        point_C_candidate = np.array(point_A) + vector_AC

        # Check if the line AC intersects the convex hull at a 90-degree angle
        for simplex in hull.simplices:
            p1, p2 = convex_region_coordinates[simplex]
            if np.dot(point_C_candidate - p1, p2 - p1) == 0:
                # Intersection found
                return tuple(point_C_candidate)

        # If no intersection is found, return None or handle accordingly
        return None

    def intersection_of_lines(self,vertical_line, horizontal_line, prev_point_of_pol,convex_region):
        dime = self.container_instance.calculate_total_dimensions()
        p4 = self.find_perpendicular_point_on_convex_region2(prev_point_of_pol, convex_region)
        print(prev_point_of_pol,convex_region)
        print(p4)
        angle_ch = self.calculate_angle_in_degrees(prev_point_of_pol, p4)
        angle_ch1 = (angle_ch + 180) % 360
        angle_ch2 = angle_ch % 360
        vx, vy = (
            math.cos(math.radians(angle_ch1)), math.sin(math.radians(angle_ch1)))
        vx2, vy2 = (
            math.cos(math.radians(angle_ch2)), math.sin(math.radians(angle_ch2)))
        g1, g2 = prev_point_of_pol
        point1 = self.calculate_endpoint_from_direction(g1, g2, vx, vy, dime)
        point2 = self.calculate_endpoint_from_direction(g1, g2, vx2, vy2, dime)

        # Define the coordinates of the endpoints of the two lines
        vertical_line = LineString(vertical_line)
        horizontal_line = LineString(horizontal_line)
        main_line1 = LineString([(g1, g2), point1])
        main_line2 = LineString([(g1, g2), point2])

        # Find the intersection point
        intersection1 = vertical_line.intersection(main_line1)
        intersection2 = horizontal_line.intersection(main_line1)
        intersection3 = vertical_line.intersection(main_line2)
        intersection4 = horizontal_line.intersection(main_line2)
        pol = Polygon(convex_region)
        if main_line1.crosses(pol) or main_line1.within(pol):
            print("check1")
            if not intersection1.is_empty and not intersection2.is_empty:
                p1 = Point((g1, g2))
                p2 = Point((intersection1.x, intersection1.y))
                p3 = Point((intersection2.x, intersection2.y))
                dis1 = p1.distance(p2)
                dis2 = p1.distance(p3)
                if dis1 < dis2:
                    return intersection1.x, intersection1.y
                else:
                    return intersection2.x, intersection2.y
            elif not intersection1.is_empty:
                return intersection1.x, intersection1.y
            elif not intersection2.is_empty:
                return intersection2.x, intersection2.y
            else:
                return (g1, g2), point2
        elif main_line2.crosses(pol) or main_line2.within(pol):
            print("check2")
            if not intersection3.is_empty and not intersection4.is_empty:
                p1 = Point((g1, g2))
                p2 = Point((intersection3.x, intersection3.y))
                p3 = Point((intersection4.x, intersection4.y))
                dis1 = p1.distance(p2)
                dis2 = p1.distance(p3)
                if dis1 < dis2:
                    return intersection3.x, intersection3.y
                else:
                    return intersection4.x, intersection4.y
            elif not intersection3.is_empty:
                return intersection3.x, intersection3.y
            elif not intersection4.is_empty:
                return intersection4.x, intersection4.y
            else:
                return (g1,g2), point2
        else:
            return (g1, g2), point1

    def intersection_of_lines2(self,vertical_line, horizontal_line, prev_point_of_pol,convex_region):
        dime = self.container_instance.calculate_total_dimensions()
        p4 = self.find_perpendicular_point_on_convex_region(prev_point_of_pol, convex_region)
        angle_ch = self.calculate_angle_in_degrees(prev_point_of_pol, p4)
        angle_ch1 = (angle_ch + 180) % 360
        angle_ch2 = angle_ch % 360
        vx, vy = (
            math.cos(math.radians(angle_ch1)), math.sin(math.radians(angle_ch1)))
        vx2, vy2 = (
            math.cos(math.radians(angle_ch2)), math.sin(math.radians(angle_ch2)))
        g1, g2 = prev_point_of_pol
        point1 = self.calculate_endpoint_from_direction(g1, g2, vx, vy, dime)
        point2 = self.calculate_endpoint_from_direction(g1, g2, vx2, vy2, dime)

        # Define the coordinates of the endpoints of the two lines
        hor = horizontal_line
        vert = vertical_line
        vertical_line = LineString(vertical_line)
        horizontal_line = LineString(horizontal_line)
        main_line1 = LineString([(g1, g2), point1])
        main_line2 = LineString([(g1, g2), point2])

        # Find the intersection point
        intersection1 = vertical_line.intersection(main_line1)
        intersection2 = horizontal_line.intersection(main_line1)
        intersection3 = vertical_line.intersection(main_line2)
        intersection4 = horizontal_line.intersection(main_line2)
        pol = Polygon(convex_region)
        len1 = 0
        intersection_result1 = main_line1.intersection(pol)
        intersection_type1 = type(intersection_result1)
        if intersection_type1 == LineString:
            len1 = intersection_result1.length
        len2 = 0
        intersection_result2 = main_line2.intersection(pol)
        intersection_type2 = type(intersection_result2)
        if intersection_type2 == LineString:
            len2 = intersection_result2.length

        if len1 > len2:
            print("check1")
            if not intersection1.is_empty and not intersection2.is_empty:
                p1 = Point((g1, g2))
                p2 = Point((intersection1.x, intersection1.y))
                p3 = Point((intersection2.x, intersection2.y))
                dis1 = p1.distance(p2)
                dis2 = p1.distance(p3)
                if dis1 < dis2:
                    return intersection1.x, intersection1.y
                else:
                    return intersection2.x, intersection2.y
            elif not intersection1.is_empty:
                return intersection1.x, intersection1.y
            elif not intersection2.is_empty:
                return intersection2.x, intersection2.y
            else:
                print("type of ", type(main_line1.intersection(pol)))
                intersection_result = main_line1.intersection(pol)
                intersection_type = type(intersection_result)
                if intersection_type == LineString:
                    print(intersection_result.length)

                print("here")
                return (g1, g2), point1
        elif len2 > len1:
            print("check2")
            if not intersection3.is_empty and not intersection4.is_empty:
                p1 = Point((g1, g2))
                p2 = Point((intersection3.x, intersection3.y))
                p3 = Point((intersection4.x, intersection4.y))
                dis1 = p1.distance(p2)
                dis2 = p1.distance(p3)
                if dis1 < dis2:
                    return intersection3.x, intersection3.y
                else:
                    return intersection4.x, intersection4.y
            elif not intersection3.is_empty:
                return intersection3.x, intersection3.y
            elif not intersection4.is_empty:
                return intersection4.x, intersection4.y
            else:
                return (g1, g2), point2
        else:
            print("here")
            return (g1, g2), point1

    def intersection_of_lines3(self,vertical_line, horizontal_line, prev_point_of_pol,convex_region):
        dime = self.container_instance.calculate_total_dimensions()
        p4 = self.find_perpendicular_point_on_convex_region(prev_point_of_pol, convex_region)
        angle_ch = self.calculate_angle_in_degrees(prev_point_of_pol, p4)
        angle_ch1 = (angle_ch + 180) % 360
        angle_ch2 = angle_ch % 360
        vx, vy = (
            math.cos(math.radians(angle_ch1)), math.sin(math.radians(angle_ch1)))
        vx2, vy2 = (
            math.cos(math.radians(angle_ch2)), math.sin(math.radians(angle_ch2)))
        g1, g2 = prev_point_of_pol
        point1 = self.calculate_endpoint_from_direction(g1, g2, vx, vy, dime)
        point2 = self.calculate_endpoint_from_direction(g1, g2, vx2, vy2, dime)

        # Define the coordinates of the endpoints of the two lines
        hor = horizontal_line
        vert = vertical_line
        vertical_line = LineString(vertical_line)
        horizontal_line = LineString(horizontal_line)
        main_line1 = LineString([(g1, g2), point1])
        main_line2 = LineString([(g1, g2), point2])

        # Find the intersection point
        intersection1 = vertical_line.intersection(main_line1)
        intersection2 = horizontal_line.intersection(main_line1)
        intersection3 = vertical_line.intersection(main_line2)
        intersection4 = horizontal_line.intersection(main_line2)
        pol = Polygon(convex_region)
        len1 = 0
        intersection_result1 = main_line1.intersection(pol)
        intersection_type1 = type(intersection_result1)
        if intersection_type1 == LineString:
            len1 = intersection_result1.length
        len2 = 0
        intersection_result2 = main_line2.intersection(pol)
        intersection_type2 = type(intersection_result2)
        if intersection_type2 == LineString:
            len2 = intersection_result2.length

        if len1 > len2:
            print("check1")
            if not intersection1.is_empty and not intersection2.is_empty:
                p1 = Point((g1, g2))
                p2 = Point((intersection1.x, intersection1.y))
                p3 = Point((intersection2.x, intersection2.y))
                dis1 = p1.distance(p2)
                dis2 = p1.distance(p3)
                if dis1 < dis2:
                    return (g1,g2) , point1
                else:
                    return (g1,g2) , point1
            elif not intersection1.is_empty:
                return (g1,g2) , point1
            elif not intersection2.is_empty:
                return (g1,g2) , point1
            else:
                print("type of ", type(main_line1.intersection(pol)))
                intersection_result = main_line1.intersection(pol)
                intersection_type = type(intersection_result)
                if intersection_type == LineString:
                    print(intersection_result.length)

                print("here")
                return (g1, g2), point1
        elif len2 > len1:
            print("check2")
            if not intersection3.is_empty and not intersection4.is_empty:
                p1 = Point((g1, g2))
                p2 = Point((intersection3.x, intersection3.y))
                p3 = Point((intersection4.x, intersection4.y))
                dis1 = p1.distance(p2)
                dis2 = p1.distance(p3)
                if dis1 < dis2:
                    return (g1,g2) , point2
                else:
                    return (g1,g2) , point2
            elif not intersection3.is_empty:
                return (g1,g2) , point2
            elif not intersection4.is_empty:
                return (g1,g2) , point2
            else:
                return (g1, g2), point2
        else:
            print("here")
            return (g1, g2), point2

    def extend_polygon(self,polygon, angle_degrees, distance):
        polygon = Polygon(polygon)
        # Convert angle to radians
        angle_radians = radians(angle_degrees)

        # Calculate the new x and y coordinates for each vertex
        extended_vertices = [(x + distance * cos(angle_radians), y + distance * sin(angle_radians))
                             for x, y in polygon.exterior.coords]

        # Find the min and max x-coordinates of the original and extended vertices
        min_x = min(coord[0] for coord in extended_vertices)
        max_x = max(coord[0] for coord in extended_vertices)

        # Create a rectangle that covers the entire width of the original polygon
        extended_polygon = Polygon([(min_x, polygon.bounds[1]), (max_x, polygon.bounds[1]),
                                    (max_x, polygon.bounds[3]), (min_x, polygon.bounds[3])])

        return extended_polygon

    def calculate_midpoint_bet_2_points(self,x1, y1, x2, y2):
        midpoint_x = (x1 + x2) / 2
        midpoint_y = (y1 + y2) / 2
        return midpoint_x, midpoint_y

    def find_weighted_point(self,x1, y1, x2, y2, t):
        new_x = (1 - t) * x1 + t * x2
        new_y = (1 - t) * y1 + t * y2
        return new_x, new_y

    def project_point_to_convex_edge(self,convex_region, interior_point):
        """
        Project a point inside a convex region onto the nearest edge of the convex hull.

        Parameters:
        convex_region (list of tuples): Vertices of the convex region in counter-clockwise order.
        interior_point (tuple): Coordinates of the point inside the convex region.

        Returns:
        tuple: Coordinates of the projected point on the convex hull edge.
        """
        # Create a Shapely Polygon from the convex region
        polygon = Polygon(convex_region)

        # Create a Shapely Point for the interior point
        point = Point(interior_point)

        # Project the interior point onto the boundary of the convex hull
        projected_point = polygon.exterior.interpolate(polygon.exterior.project(point))

        return projected_point.x, projected_point.y

    def project_point_to_convex_edge_angle(self, convex_region, interior_point, angle_degrees):
        """
        Project a point inside a convex region onto the nearest edge of the convex hull.

        Parameters:
        convex_region (list of tuples): Vertices of the convex region in counter-clockwise order.
        interior_point (tuple): Coordinates of the point inside the convex region.
        angle_degrees (float): Angle in degrees to guide the projection.

        Returns:
        tuple: Coordinates of the projected point on the convex hull edge.
        """
        # Create a Shapely Polygon from the convex region
        polygon = Polygon(convex_region)

        # Create a Shapely Point for the interior point
        point = Point(interior_point)

        # Convert angle from degrees to radians
        angle_radians = math.radians(angle_degrees)

        # Calculate the direction vector based on the given angle
        direction_vector = (math.cos(angle_radians), math.sin(angle_radians))

        # Get the centroid of the polygon's exterior (a single point on the convex hull)
        centroid_point = polygon.exterior.centroid

        # Project the interior point onto the boundary of the convex hull
        projected_point = Point(centroid_point.x + direction_vector[0], centroid_point.y + direction_vector[1])

        # Return the coordinates directly
        return projected_point.x, projected_point.y
    def min_radius_of_shape(self,points):
        # Create a Shapely MultiPoint object
        multi_point = MultiPoint(points)

        # Get the minimum bounding rectangle
        min_rectangle = multi_point.minimum_rotated_rectangle

        # Calculate the minimum radius (half of the minimum bounding rectangle's diagonal)
        min_radius = min_rectangle.exterior.length / 2.0

        return min_radius

    def count_crossings_with_convex_region(self,line, convex_region):
        """
            Count how many times a line crosses a convex region.

            Parameters:
            line (LineString): The line to check for crossings.
            convex_region (Polygon): The convex region represented as a Polygon.

            Returns:
            int: Number of crossings.
            """
        # Break the line into segments using MultiLineString
        segments = MultiLineString([line])

        # Count the number of line segments that cross the exterior of the convex region
        crossings = sum(segment.crosses(convex_region.exterior) for segment in segments)

        return crossings


    def plot(self):
        angle = 0
        sorted_items = sorted(self.item_instances, key=lambda item: item.calculate_total_dimensions(), reverse=False)
        middle_point = self.calculate_centroid(self.container_instance.coordinates)
        convex_region = self.container_instance.coordinates
        convex_region_original = self.container_instance.coordinates

        another_list = []
        temp_po = []
        temp_list = []
        value = 0
        start_time = time.time()
        previous_polygon = None

        for dex, polygon in enumerate(sorted_items):
            if dex == 700:
                break
            print(dex)

            x, y = middle_point
            polygon.move_item(x, y)
            copied = copy.deepcopy(polygon)
            f_p = None
            t_p = None
            pol2 = Polygon(polygon.coordinates)
            pol1 = Polygon(convex_region)
            if pol2.within(pol1):
                if dex == 0:
                    extended_polygon, right_line, left_line = self.extend_pol_for_first_time(angle, polygon,
                                                                                               middle_point)
                    extended_polygon2, right_line2, left_line2 = self.extend_pol_for_first_time2(angle, polygon,
                                                                                             middle_point)
                    l_p, r_p = self.find_points_that_intersect(left_line2, right_line2,convex_region)
                    polygon.left_intersection_point = l_p
                    polygon.right_intersection_point = r_p




                    f_p, t_p, list_of_lines, list_of_points = self.place_poly(polygon, extended_polygon, convex_region,
                                                                              angle, right_line, left_line)
                    polygon.move_from_to2(f_p, t_p)
                    the_point, sec_point, left_list = self.check_ep(angle, polygon, middle_point)
                    polygon.left_point = the_point

                    # polygon.sec_left_point = sec_point
                    # left_list = self.check_ep2(angle, polygon)
                    polygon.left_list = left_list
                    polygon.curr_angle = angle

                    new_angle = self.calculate_angle_in_degrees(f_p, t_p)

                    li = self.extend_pol(new_angle, convex_region, polygon)

                    list_of_new_region = self.for_edges_that_intersect(Polygon(convex_region),
                                                                       Polygon(li))
                    convex_region = list_of_new_region
                    middle_point = self.calculate_centroid(convex_region)
                    another_list.append(polygon)
                    value = value + polygon.value
                    previous_polygon = polygon

                if dex >= 1:
                    list_of_lines = []
                    list_of_points = []
                    # Get the polygon before the one at index dex
                    # previous_polygon = sorted_items[dex - 1]
                    flag_temp = False
                    sec_flag = False
                    while not flag_temp:
                        extended_polygon = None
                        right_line = None
                        left_line = None
                        min = float('inf')
                        poi = []
                        a = None

                        this_angle = previous_polygon.curr_angle
                        ang = self.calculate_angle_in_degrees((self.calculate_centroid(previous_polygon.coordinates)),
                                                              middle_point)

                        vertical_line, horizontal_line = self.create_lines(convex_region)
                        """
                        if dex >= 8:
                            temp_list.append(horizontal_line)
                            temp_list.append(vertical_line)

                            one, to = self.intersection_of_lines3(vertical_line, horizontal_line,
                                                                  previous_polygon.left_intersection_point,convex_region_original)

                            #one,to= p

                            copied8 = copy.deepcopy(polygon)
                            copied8.set_coordinates(convex_region)
                            an = []
                            an.append(copied8)

                            temp_list.append([one, to])
                            print(one,to)
                            # print(p)
                            temp_po.append(to)
                            temp_po.append(one)
                            #temp_po.append(previous_polygon.left_intersection_point)

                            draw_instance = Draw(self.container_instance, an, (1, 1), (1, 1), (1, 1),
                                                 (1, 1),
                                                 temp_po,
                                                 None,
                                                 None, temp_list)
                            draw_instance.plot()
                            temp_list.pop()
                            temp_list.pop()
                            temp_po.pop()
                            temp_po.pop()
                        """



                        p = self.intersection_of_lines2(vertical_line, horizontal_line,
                                                             previous_polygon.left_intersection_point, convex_region_original)
                        deter_angle_point = self.calculate_angle_in_degrees(p,previous_polygon.left_intersection_point)



                        sign_yes = False
                        sign_yes_ver2 = False

                        new_x, new_y = p
                        copied20 = copy.deepcopy(polygon)


                        check_co = polygon.move_item_value(new_x, new_y)
                        #copied20.set_coordinates(check_co)


                        pol_check = Polygon(check_co)
                        if pol_check.within(pol1):
                            polygon.move_item(new_x, new_y)
                        else:
                            sign_yes = True


                        flag000 = False
                        to_point_temp = None
                        to_point = None
                        from_point = None
                        left_line2 = None
                        right_line2 = None
                        extended_pol2 = None
                        left_line22 = None
                        right_line22 = None
                        extended_pol22 = None
                        extended_poly_var2 = None
                        right_line_var2 = None
                        left_line_var2 = None
                        angle_temp = None
                        while not flag000:
                            for index in range(2):
                                if index == 1 and not sign_yes:
                                    check_co2 = polygon.move_from_to2_value(from_point, (new_x, new_y))
                                    pol_check2 = Polygon(check_co2)
                                    if pol_check2.within(pol1):
                                        polygon.move_from_to2(from_point, (new_x, new_y))
                                elif index == 1 and sign_yes:
                                    break
                                points = self.check_if_line_cross(previous_polygon, polygon)
                                # cen = self.calculate_centroid(polygon.coordinates)
                                # right = self.check_ep2(ang, points,cen)

                                for point in points:
                                    line = []
                                    angle = self.calculate_angle_in_degrees(point, previous_polygon.left_point)
                                    while True:
                                        a, b, c = self.check_ep(angle, previous_polygon, point)
                                        angle = self.calculate_angle_in_degrees(point, a)
                                        l = None
                                        if index == 1:
                                            dime = self.container_instance.calculate_total_dimensions()
                                            xx, yy = point
                                            this_angle = (angle + 0.01 % 360)
                                            vx, vy = (
                                                math.cos(math.radians(this_angle)),
                                                math.sin(math.radians(this_angle)))
                                            xxx, yyy = self.calculate_endpoint_from_direction(xx, yy, vx, vy, dime)
                                            l = LineString([point, (xxx, yyy)])
                                        elif index == 0:
                                            l = LineString([point, a])

                                        p = Polygon(previous_polygon.coordinates)
                                        p = p.buffer(0.1)
                                        if not l.crosses(p):
                                            to_point_temp = a
                                            # angle = angle_before
                                            break

                                    angle = (angle + 0.01 % 360)

                                    flag, d1, d2, d3, d4, d5, d6, extended_poly, right_li, left_li = self.placement(
                                        angle,
                                        polygon.coordinates,
                                        previous_polygon)

                                    print(flag)

                                    line.append([point, a])
                                    poi.append(point)
                                    poi.append(a)

                                    copied2 = copy.deepcopy(polygon)
                                    copied2.set_coordinates(convex_region)

                                    copied.set_coordinates(extended_poly.exterior.coords)
                                    another_list.append(copied)
                                    another_list.append(polygon)
                                    aru = []
                                    aru.append(copied)
                                    aru.append(copied2)
                                    aru.append(polygon)
                                    # aru.append(previous_polygon)
                                    if dex >= 1000:
                                        draw_instance = Draw(self.container_instance, aru, (1, 1), (1, 1), (1, 1),
                                                             (1, 1),
                                                             poi,
                                                             None,
                                                             None, line)
                                        draw_instance.plot()

                                    another_list.pop()
                                    another_list.pop()

                                    if flag:
                                        flag2, d12, d22, d32, d42, d52, d62, extended_poly2, right_li2, left_li2 = self.placement2(
                                            angle,
                                            polygon.coordinates,
                                            previous_polygon)
                                        sec_flag = True
                                        extended_polygon = extended_poly
                                        right_line = right_li
                                        left_line = left_li
                                        left_line2 = left_li2
                                        right_line2 = right_li2
                                        extended_pol2 = extended_poly2

                                        from_point = point
                                        to_point = to_point_temp
                                        break



                            if sign_yes:
                                break
                            points = self.check_if_line_cross(previous_polygon, copied20)

                            for point in points:
                                line = []
                                angle_temp = self.calculate_angle_in_degrees(point, previous_polygon.left_point)
                                while True:
                                    a, b, c = self.check_ep(angle_temp, previous_polygon, point)
                                    angle_temp = self.calculate_angle_in_degrees(point, a)
                                    l = LineString([point, a])
                                    p = Polygon(previous_polygon.coordinates)
                                    p = p.buffer(0.1)
                                    if not l.crosses(p):
                                        to_point_temp = a
                                        break

                                angle_temp = (angle_temp + 0.01 % 360)

                                flag_temp, d1_temp, d2_temp, d3_temp, d4_temp, d5_temp, d6_temp, extended_poly_temp, right_li_temp, left_li_temp = self.placement(
                                    angle_temp,
                                    copied20.coordinates,
                                    previous_polygon)

                                line.append([point, a])
                                poi.append(point)
                                poi.append(a)

                                copied2 = copy.deepcopy(copied20)
                                copied2.set_coordinates(convex_region)
                                copied.set_coordinates(extended_poly_temp.exterior.coords)
                                another_list.append(copied)
                                another_list.append(copied20)
                                aru = []
                                aru.append(copied)
                                aru.append(copied2)
                                aru.append(copied20)
                                # aru.append(previous_polygon)
                                """
                                if dex >= 13:
                                    draw_instance = Draw(self.container_instance, aru, (1, 1), (1, 1), (1, 1),
                                                         (1, 1),
                                                         poi,
                                                         None,
                                                         None, line)
                                    draw_instance.plot()
                                """

                                another_list.pop()
                                another_list.pop()

                                if flag_temp:
                                    sec_flag = True
                                    extended_poly_var2 = extended_poly_temp
                                    right_line_var2 = right_li_temp
                                    left_line_var2 = left_li_temp

                                    flag2_temp, d12_temp, d22_temp, d32_temp, d42_temp, d52_temp, d62_temp, extended_poly2_temp, right_li2_temp, left_li2_temp = self.placement2(
                                        angle_temp,
                                        copied20.coordinates,
                                        previous_polygon)
                                    left_line22 = left_li2_temp
                                    right_line22 = right_li2_temp
                                    extended_pol22 = extended_poly2_temp
                                    break


                            ppol1 = Polygon(polygon.coordinates)
                            #ppol2 = Polygon(previous_polygon.coordinates)
                            point_of_intersection = left_line22.intersection(left_line)
                            point_of_intersection2 = right_line22.intersection(left_line)

                            dist = ppol1.distance(point_of_intersection)
                            dist2 = ppol1.distance(point_of_intersection2)
                            if dist2 < dist:
                                dist = dist2
                            flag000, (px000, py000), p00, (px200, py200), p000, (cx000, cy000), (
                            x100, y100), filled_polygon000, right_line000, left_line000 = self.placement3(angle,
                                                                                                          polygon.coordinates,
                                                                                                 convex_region,
                                                                                             dist,dist)
                            if dex >= 1000:
                                listtt = []
                                listtt.append(list(left_line22.coords))
                                listtt.append(list(right_line22.coords))

                                listtt.append(list(left_line.coords))
                                print(flag000)
                                copied90 = copy.deepcopy(polygon)
                                copied90.set_coordinates(filled_polygon000.exterior.coords)
                                another_list.append(copied90)

                                draw_instance = Draw(self.container_instance, another_list, (1, 1), (1, 1), (1, 1),
                                                     (1, 1),
                                                     None,
                                                     None,
                                                     None, listtt)
                                draw_instance.plot()
                            if not flag000:
                                print("*************************************************8")
                                polygon.set_coordinates(copied20.coordinates)

                                extended_polygon = extended_poly_var2
                                right_line = right_line_var2
                                left_line = left_line_var2
                                left_line2 = left_line22
                                right_line2 = right_line22
                                extended_pol2 = extended_pol22
                                angle = angle_temp
                                deter_angle_point = angle_temp
                                sec_flag = True

                                break
                            else:
                                break


                        if sec_flag:
                            f_p, t_p, list_of_lines, list_of_points = self.place_poly(polygon, extended_polygon,
                                                                                      convex_region, angle, right_line,
                                                                                      left_line)
                            l_p, r_p = self.find_points_that_intersect(left_line2, right_line2, convex_region_original)

                            #polygon.left_intersection_point = l_p
                            polygon.right_intersection_point = r_p
                            polygon.extended_pol = extended_pol2
                            polygon.move_from_to2(f_p, t_p)
                            another_list.append(polygon)
                            mid_of_ol = self.calculate_centroid(polygon.coordinates)
                            the_point, sec_point, left_list = self.check_ep(angle, polygon, middle_point)

                            new_l_p = self.project_point_to_convex_edge(convex_region_original, the_point)

                            polygon.left_intersection_point = new_l_p

                            print("the new left point",new_l_p,dex)

                            polygon.left_point = the_point
                            # polygon.sec_left_point = sec_point
                            # left_list = self.check_ep2(angle, polygon)
                            polygon.left_list = left_list
                            polygon.curr_angle = angle

                            previous_polygon = polygon
                            if dex >= 300:

                                draw_instance = Draw(self.container_instance, another_list, (1, 1), (1, 1), (1, 1),
                                                     (1, 1),
                                                     None,
                                                     None,
                                                     None, None)
                                draw_instance.plot()
                            li = self.extend_pol(deter_angle_point, convex_region, polygon)

                            list_of_new_region = self.for_edges_that_intersect(Polygon(convex_region),
                                                                               Polygon(li))
                            convex_region = list_of_new_region
                            middle_point = self.calculate_centroid(convex_region)

                            break

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(elapsed_time)
        print("num of polygons", len(another_list), "out of", len(self.item_instances), "time", elapsed_time, "value",
              value)

        draw_instance = Draw(self.container_instance, another_list, (1, 1), (1, 1), (1, 1), (1, 1), None,
                             None,
                             None, None)
        draw_instance.plot()





