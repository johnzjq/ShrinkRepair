from math import sqrt
from math import cos
from math import pi
import ctypes

#the main Tol Rotterdam 201708 1e-6 building_2 1e-8
Tol = 1e-8
#Tol for degeneracy tetrahedorn (flat)  Rotterdam 201708 1e-2
DegTol = 1e-2
#Theshold that decide the flatness between two neighbor dictFaces  Rotterdam 201708 20 building_2 0.5
NeighborAngle = cos(0.5 * pi / 180)

#Tuple minus tuple (t1 - t2) (3D vector)
def tuple_minus(t1, t2):
    if len(t1) != len(t2):
        print("Tuples with different sizes!")
        return []
    c = []
    for i in range(0, len(t1)):
        c.append(t1[i] - t2[i])
    return c

#Tuple add tuple (t1 + t2) (3D vector)
def tuple_plus(t1, t2):
    if len(t1) != len(t2):
        print("Tuples with different sizes!")
        return []
    c = []
    for i in range(0, len(t1)):
        c.append(t1[i] + t2[i])
    return c

#Product a number with a tuple
def tuple_numproduct(num, t):
    o = []
    for i in t:
        o.append(i * num)
    return o

#CrossProduct of 3D vectors
def cross_product_3(v1, v2):
    if len(v1) != len(v2):
        print("Vectors with different sizes!")
        return []
    v = []
    v.append(v1[1] * v2[2] - v1[2] * v2[1])
    v.append(v1[2] * v2[0] - v1[0] * v2[2])
    v.append(v1[0] * v2[1] - v1[1] * v2[0])

    return v

#DotProduct of 3D vectors
def dot_product_3(v1, v2):
    if len(v1) != len(v2):
        print("Vectors with different sizes!")
        return 0
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

#the squared length of a 3Dvector
def vector_length_3Ex(v):
    return v[0]*v[0] + v[1]*v[1] + v[2]*v[2]

#the  length of a 3Dvector
def vector_length_3(v):
    return sqrt(vector_length_3Ex(v))

#Calculate the squared distance from a Point to a Point
#INPUT: Point1 and Point2
#OUTPUT: 
#RETURN: the squared distance
def square_dist_point_to_point(pt1, pt2):
    return (pt1[0] - pt2[0]) * (pt1[0] - pt2[0]) + (pt1[1] - pt2[1]) * (pt1[1] - pt2[1]) + (pt1[2] - pt2[2]) * (pt1[2] - pt2[2]) 

#Calculate the squared distance from a Point to a Line
#INPUT: pt is the point (x, y, z), line is along (pt1, pt2)
#OUTPUT: pFootPt is the foot point
#RETURN: the squared distance
def square_dist_point_to_line(pt, pt1, pt2, pFootPt):

    tmp1 = tuple_minus(pt2, pt1)
    tmp2 = tuple_minus(pt, pt1)

    c1 = dot_product_3 (tmp1, tmp2)
    c2 = dot_product_3 (tmp1, tmp1)

    if vector_length_3(tmp1) < Tol:
        print("Degenerated line", pt, pt1, pt2)
        pFootPt = pt1
        return square_dist_point_to_point(pt,pt1)

    para = c1/c2
    pFootPt = tuple_plus(pt1, tuple_numproduct(para, tmp1))
    return square_dist_point_to_point(pt, pFootPt)
   
#Calculate the squared distance from a Point to a Plane
#INPUT: Pt is the point and plane is defined by three points
#OUTPUT: 
#RETURN: the squared distance
def square_dist_point_to_plane(pt, pt1_plane, pt2_plane, pt3_plane):
    planeNormal = cross_product_3(tuple_minus(pt1_plane, pt2_plane), tuple_minus(pt1_plane, pt3_plane))
    lengthNormal = vector_length_3(planeNormal)
    if lengthNormal < Tol:
        print("degenerated triangle")
        return 0
    else:
        planeNormal = tuple_numproduct(1/lengthNormal, planeNormal)
        planeA = planeNormal[0]
        planeB = planeNormal[1]
        planeC = planeNormal[2]
        planeD = -dot_product_3(planeNormal, pt1_plane)
        value = planeA * pt[0] + planeB * pt[1] + planeC * pt[2] + planeD
        return value * value

#Calculate the intersection point of a line and a plane
#INPUT: ptStr and ptEnd are two points defining the line and plane is defined by three points
#OUTPUT: ptOut is the intersection point
#RETURN: True means succeed in geting a result
def RLineWithPlane(ptStr, ptEnd, pt1_plane, pt2_plane, pt3_plane, ptOut):
    planeNormal = cross_product_3(tuple_minus(pt1_plane, pt2_plane), tuple_minus(pt1_plane, pt3_plane))
    lengthNormal = vector_length_3(planeNormal)
    if lengthNormal < Tol:
        print("degenerated triangle")
        return 0
    else:
        planeNormal = tuple_numproduct(1/lengthNormal, planeNormal)
        planeA = planeNormal[0]
        planeB = planeNormal[1]
        planeC = planeNormal[2]
        planeD = -dot_product_3(planeNormal, pt1_plane)
        #the vector of the line
        vLine = tuple_minus(ptEnd, ptStr)
        n = dot_product_3(vLine, planeNormal)
        if abs(n) < Tol:
            print("parallel or overlapping")
            return False
        u = - (dot_product_3(ptStr, planeNormal) + planeD) / n
        ptOut[0] = tuple_plus(tuple_numproduct(u, vLine), ptStr)
        return True

#Calculate the normalized normal of a triangle
#INPUT: vertexList is a list of three dictVertices
#OUTPUT: 
#RETURN: a vector representing the normal, if degenerated return (0.0, 0.0, 0.0)
def get_face_normal(vertexList):
    p1p2 = tuple_minus(vertexList[1], vertexList[0])
    p1p3 = tuple_minus(vertexList[2], vertexList[0])
    Normal = cross_product_3(p1p2, p1p3)
    lengthNorm = vector_length_3(Normal)
    if lengthNorm - 0.0 > Tol:
        Normal = tuple_numproduct(1/lengthNorm, Normal) 
        return Normal
    else:
        return (0.0, 0.0, 0.0)

#check whether vertex Vt1 is on the line segment along [Pt1, Pt2]
#INPUT: Vt and Pt are three tuples (x, y, z); 
#OUTPUT: 
#RETURN: True means on the line (may be on the end points)
def is_point_in_linesegment(Vt, Pt1, Pt2):
    pFootPt = [0]
    d = sqrt(square_dist_point_to_line(Vt,Pt1,Pt2,pFootPt))
    if d < Tol:
        bbox = get_bbox_of_points([Pt1, Pt2])
        if Vt[0] < bbox[1][0] + Tol and Vt[0] > bbox[0][0] - Tol and\
           Vt[1] < bbox[1][1] + Tol and Vt[1] > bbox[0][1] - Tol and\
           Vt[2] < bbox[1][2] + Tol and Vt[2] > bbox[0][2] - Tol:
                return True
        else:
            return False
    else:
        return False
        
#check whether vertex Vt1 is on the ray along (Pt1, Pt2)
#INPUT: Vt and Pt are three tuples (x, y, z); 
#OUTPUT: 
#RETURN: True means on the ray
def is_point_on_line(Vt, Pt1, Pt2):
    pFootPt = [0]
    d = sqrt(square_dist_point_to_line(Vt,Pt1,Pt2,pFootPt))
    if d < Tol:
        return True
    else:
        return False


#check whether vertex Vt1 is within the range of Tri (if Tri is degenerated, False is returned)
#INPUT: Vt is a three tuple (x, y, z), Tri is a tuple of three 3d dictVertices (v1, v2, v3); 
#OUTPUT: 
#RETURN: True means in the range
def is_point_in_triangle_3(Vt, Tri):
    bbox = get_bbox_of_points(Tri)
    if is_point_in_bbox(Vt, bbox):
        if sqrt(square_dist_point_to_plane(Vt, Tri[0], Tri[1], Tri[2])) < Tol:
            #project to 2D
            #the projection plane
            vt01 = Tri[0]
            vt02 = Tri[1]
            vt03 = Tri[2]

            #convert to 2D (simply select an axis aligned projection plane)
            v1 = tuple_minus(vt02, vt01)
            v2 = tuple_minus(vt03, vt01)
            normal = cross_product_3(v1, v2)

            #check degeneration
            if vector_length_3(normal) < Tol:
                #degnerated face does not has interior
                return False

            axisProject = get_axis_aligned_projection_plane(normal)

            Vt2D = []
            Tri2D = []

            Vt2D += get_projected_coords(Vt, axisProject)
            for v in Tri:
                Tri2D.append(get_projected_coords(v, axisProject)) 

            #process in 2D
            return is_point_in_triangle_2(Vt2D, Tri2D)
    return False

#check whether vertex Vt1 is within the range of Tri
#INPUT: Vt is a two tuple (x, y), Tri is a tuple of three 2d dictVertices (v1, v2, v3); 
#OUTPUT: 
#RETURN: True means in the range
def is_point_in_triangle_2(Vt, Tri):

    b1 = is_point_on_line_side_2(Vt, Tri[0], Tri[1])
    b2 = is_point_on_line_side_2(Vt, Tri[1], Tri[2])
    b3 = is_point_on_line_side_2(Vt, Tri[2], Tri[0])

    return ((b1 == b2) and (b2 == b3))
  
#test whether a pt is on the left or right side of a line
#pt1, pt2, pt3 are all two tuple (x, y)
#RETURN: 1 means left -1 means right 0 means on the line
def is_point_on_line_side_2(pt1, pt2, pt3):
    fSign = (pt1[0] - pt3[0]) * (pt2[1] - pt3[1]) - (pt2[0] - pt3[0]) * (pt1[1] - pt3[1]) 
    if fSign > Tol:
        return 1
    elif fSign < -Tol:
        return -1
    else:
        return 0

#the 2D version of lines intersection test
#the return value is the same as the 3D version
def line_intersect_line_2d(vt1, vt2, pt1, pt2):
    denominator = (vt1[0] - vt2[0]) * (pt1[1] - pt2[1]) - (vt1[1] - vt2[1]) * (pt1[0] - pt2[0]) 
    if abs(denominator) < Tol:
        return [], False
    determinantsX = (vt1[0]*vt2[1] - vt1[1]*vt2[0]) * (pt1[0] - pt2[0]) - (vt1[0] - vt2[0]) * (pt1[0]*pt2[1] - pt1[1]*pt2[0]) 
    determinantsY = (vt1[0]*vt2[1] - vt1[1]*vt2[0]) * (pt1[1] - pt2[1]) - (vt1[1] - vt2[1]) * (pt1[0]*pt2[1] - pt1[1]*pt2[0])
    return [determinantsX, determinantsY], True

#the 2D version of line segments intersection test (using orientation)
#the return value is either True or False
def is_lineseg_intersect_lineseg_2d(vt1, vt2, pt1, pt2):
    signVt = []
    signVt.append(is_point_on_line_side_2(vt1, pt1, pt2))
    signVt.append(is_point_on_line_side_2(vt2, pt1, pt2))
    signVt.append(is_point_on_line_side_2(pt1, vt1, vt2))
    signVt.append(is_point_on_line_side_2(pt2, vt1, vt2))
    if signVt[0] * signVt[1] == -1:
        if signVt[2] * signVt[3] == -1:
            return True
    if 0 in signVt[:2]:
        if signVt[2] * signVt[3] == -1:
            return True
    if 0 in signVt[2:]:
        if signVt[0] * signVt[1] == -1:
            return True
    return False

#Modify to 2D may be more robust (to be check)
#Intersection between line segment (Vt1, Vt2) and (Pt1, Pt2)(from geoscope geometry linewithlineseg)
#return the intersect point and whether such a vertex exists
#INPUT: Vt and Pt are three tuples (x, y, z); 
#OUTPUT: 
#RETURN: NewVt the intersected vertex (x, y, z) True means do intersect
def lineseg_intersect_lineseg(Vt1, Vt2, Pt1, Pt2):
    v1 = tuple_minus(Vt2, Vt1)
    v2 = tuple_minus(Pt2, Pt1)

    #prevent degeneration
    lengthV1 = vector_length_3(v1)
    lengthV2 = vector_length_3(v2)
    if lengthV1 < Tol:
        v1 = tuple_numproduct(100, v1)

    if lengthV2 < Tol:
        v2 = tuple_numproduct(100, v2)

    v = cross_product_3(tuple_numproduct(1/lengthV1, v1), tuple_numproduct(1/lengthV2, v2))
    #parallel
    if vector_length_3(v) < Tol:
        if is_point_in_linesegment(Vt1, Pt1, Pt2) or is_point_in_linesegment(Vt2, Pt1, Pt2) or\
            is_point_in_linesegment(Pt1, Vt1, Vt2) or is_point_in_linesegment(Pt2, Vt1, Vt2):
            #overlapping
            return [], True
        else:
            #separate
            return [], False

    v3 = tuple_minus(Pt1, Vt1)

    v4 = cross_product_3 (v3, v2)
    v5 = cross_product_3 (v1, v2)
    v6 = cross_product_3 (v3, v1)

    u = vector_length_3(v4) / vector_length_3(v5)
    x = vector_length_3(v6) / vector_length_3(v5)

    if dot_product_3(v4, v5) < -Tol:
        u = -u
    if dot_product_3(v6, v5) < -Tol:
        x = -x

    #check the correctness
    if u > -Tol and 1-u > -Tol and x > -Tol and 1-x > -Tol:
        crosspt = tuple_plus(Vt1, tuple_numproduct(u, v1))
        if is_point_in_linesegment(crosspt,  Pt1, Pt2) and is_point_in_linesegment(crosspt,  Vt1, Vt2):
            return crosspt, True
    return [], False

#Modify to 2D may be more robust (to be check)
#Intersection between line segment (Vt1, Vt2) and STRAIGT LINE along (Pt1, Pt2)(from geoscope geometry linewithlineseg)
#return the intersect point and whether such a vertex exists
#INPUT: Vt and Pt are three tuples (x, y, z); 
#OUTPUT: 
#RETURN: NewVt the intersected vertex (x, y, z) True means do intersect
def is_lineseg_intersect_ray(Vt1, Vt2, Pt1, Pt2):
    v1 = tuple_minus(Vt2, Vt1)
    v2 = tuple_minus(Pt2, Pt1)

    #prevent degeneration
    lengthV1 = vector_length_3(v1)
    lengthV2 = vector_length_3(v2)
    if lengthV1 < Tol:
        v1 = tuple_numproduct(100, v1)

    if lengthV2 < Tol:
        v2 = tuple_numproduct(100, v2)

    v = cross_product_3(tuple_numproduct(1/lengthV1, v1), tuple_numproduct(1/lengthV2, v2))
    #parallel
    if vector_length_3(v) < Tol:
        if is_point_on_line(Vt1, Pt1, Pt2):
            #collinear
            return [], True
        else:
            #separate
            return [], False

    v3 = tuple_minus(Pt1, Vt1)

    v4 = cross_product_3 (v3, v2)
    v5 = cross_product_3 (v1, v2)
    v6 = cross_product_3 (v3, v1)

    u = vector_length_3(v4) / vector_length_3(v5)
    x = vector_length_3(v6) / vector_length_3(v5)

    if dot_product_3(v4, v5) < -Tol:
        u = -u
    if dot_product_3(v6, v5) < -Tol:
        x = -x

    #check the correctness
    if u > -Tol and 1-u > - Tol:
        crosspt = tuple_plus(Vt1, tuple_numproduct(u, v1))
        return crosspt, True
    else:
        return [], False


#convert from list to double array (used for ctypes)
def list_to_c_double_array(list):
    result = (ctypes.c_double * len(list))()
    for i in range(0, len(list)):
        result[i] = list[i]
    return result

#extract the bounding box a set of points
#INPUT: ptlist is a list of pt coordinates, canbe 3d (x, y, z), 2d(x, y) and 1d (x)
#RETURN: 2 tuple
def get_bbox_of_points(ptlist):
    if len(ptlist[0]) == 3:
        bbox = [[ptlist[0][0], ptlist[0][1], ptlist[0][2]], [ptlist[0][0], ptlist[0][1], ptlist[0][2]]]
        for v in ptlist:
            #min
            if v[0] < bbox[0][0]:
                bbox[0][0] = v[0]
            if v[1] < bbox[0][1]:
                bbox[0][1] = v[1]
            if v[2] < bbox[0][2]:
                bbox[0][2] = v[2]
            #max
            if v[0] > bbox[1][0]:
                bbox[1][0] = v[0]
            if v[1] > bbox[1][1]:
                bbox[1][1] = v[1]
            if v[2] > bbox[1][2]:
                bbox[1][2] = v[2]
        return bbox
    elif len(ptlist[0]) == 2:
        bbox = [[ptlist[0][0], ptlist[0][1]], [ptlist[0][0], ptlist[0][1]]]
        for v in ptlist:
            #min
            if v[0] < bbox[0][0]:
                bbox[0][0] = v[0]
            if v[1] < bbox[0][1]:
                bbox[0][1] = v[1]
            #max
            if v[0] > bbox[1][0]:
                bbox[1][0] = v[0]
            if v[1] > bbox[1][1]:
                bbox[1][1] = v[1]
        return bbox
    elif len(ptlist[0]) == 1:
        bbox = [[ptlist[0][0]], [ptlist[0][0]]]
        for v in ptlist:
            #min
            if v[0] < bbox[0][0]:
                bbox[0][0] = v[0]
            #max
            if v[0] > bbox[1][0]:
                bbox[1][0] = v[0]
        return bbox

#test whether a vt is in a boundingbox
#pt is a tuple of coordinates 3D 2D or 1D
#RETURN: True means in False means out
def is_point_in_bbox(Vt, bbox):
    if len(Vt) == 3:
        if Vt[0] < bbox[0][0] or Vt[1] < bbox[0][1] or Vt[2] < bbox[0][2] or\
        Vt[0] > bbox[1][0] or Vt[1] > bbox[1][1] or Vt[2] > bbox[1][2]:
            return False
    elif len(Vt) == 2:
        if Vt[0] < bbox[0][0] or Vt[1] < bbox[0][1] or\
        Vt[0] > bbox[1][0] or Vt[1] > bbox[1][1]:
            return False
    elif len(Vt) == 1:
        if Vt[0] < bbox[0][0] or Vt[0] > bbox[1][0]:
            return False
    return True


#self explained
#return a three tuple 
def get_axis_aligned_projection_plane(normal):

    if vector_length_3(normal) < Tol:
        print("degenerate face")

    compareYZ = abs(dot_product_3(normal, (1.0, 0.0, 0.0)))
    compareXZ = abs(dot_product_3(normal, (0.0, 1.0, 0.0)))
    compareYX = abs(dot_product_3(normal, (0.0, 0.0, 1.0)))

    nProject = []

    #Note: should be >= not >
    if compareYZ >= compareXZ and compareYZ >= compareYX:
        #choose yz
        nProject = (1, 0, 0)
    elif compareXZ >= compareYZ and compareXZ >= compareYX:
        #choose xz
        nProject = (0, 1, 0)
    else:
        #choose xy
        nProject = (0, 0, 1)

    return nProject


#return the projected 2D coordinates of a 3D coordinate based on the given projection plane
def get_projected_coords(coords3D, axisProject):
    coords2D = []
    if axisProject[0]:
        #choose yz
        coords2D.append(coords3D[1]) 
        coords2D.append(coords3D[2])
    elif axisProject[1]:
        #choose xz
        coords2D.append(coords3D[0]) 
        coords2D.append(coords3D[2])
    else:
        #choose xy
        coords2D.append(coords3D[0]) 
        coords2D.append(coords3D[1])
    return coords2D