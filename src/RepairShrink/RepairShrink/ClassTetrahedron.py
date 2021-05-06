import ModelData
import ClassFace
import SimpleMath
class Class_tetrahedron(object):
    """description of class"""
    #the tetrahedon is represented by four vertex indices t(vid1, vid2, vid3, vid4) and a tag (To be delete or In the result, etc.)
    def __init__(self, v, level = 0, curvature = 9999, tag = ClassFace.TMP):
        self.__v = v
        #added for speedup
        self.__fids = []
        #tag is used to indicate the carving order, fix  = tet is kept, del = tet should be handled later
        self.__tag = tag
        #record carving level (0 means initial, 1 means boundary)
        self.__level = level
        #record related curvature on the boundary
        self.__curvature = curvature
        #record neighourtetids (not used yet)
        self.__neighbour = {}

  

    #return the volume of this tetrahedron
    def get_volume(self):
        f = ClassFace.Class_face((self.__v[0], self.__v[1], self.__v[2]))
        pt = ModelData.dictVertices[self.__v[3]]
        return (1.0/3) * f.get_area() * SimpleMath.sqrt(SimpleMath.square_dist_point_to_plane(pt, ModelData.dictVertices[f.get_vids()[0]],  ModelData.dictVertices[f.get_vids()[1]],  ModelData.dictVertices[f.get_vids()[2]]))

    #return the area of this tetrahedron
    def get_area(self):
        f1 = ClassFace.Class_face((self.__v[0], self.__v[1], self.__v[2]))
        f2 = ClassFace.Class_face((self.__v[0], self.__v[2], self.__v[3]))
        f3 = ClassFace.Class_face((self.__v[0], self.__v[3], self.__v[1]))
        f4 = ClassFace.Class_face((self.__v[3], self.__v[1], self.__v[2]))
        return f1.get_area() + f2.get_area() + f3.get_area() + f4.get_area()

    #return the depth of the tetrahedron for a facet
    def get_depth(self, vIds):
        #check
        for v in vIds:
            if v not in self.__v:
                return -1
        #
        for v in self.__v:
            if v not in vIds:
                pt = ModelData.dictVertices[v]
                return SimpleMath.sqrt(SimpleMath.square_dist_point_to_plane(pt, ModelData.dictVertices[vIds[0]],  ModelData.dictVertices[vIds[1]],  ModelData.dictVertices[vIds[2]]))

    #update the neighbour infromation
    def updateNeighbours(self):
        pass

    #
    def is_triangle_in_tet(self, f):
        vIds = f.get_vids()
        for v in vIds:
           if v not in self.__v:
               return False
        return True

    #
    def set_tag(self, tag):
        self.__tag = tag
    #
    def get_tag(self):
        return self.__tag
    #
    def get_vids(self):
        return self.__v
    #
    def set_level(self, level):
        self.__level = level
    def get_level(self):
        return self.__level
    #
    def set_curvature(self, curvature):
        self.__curvature = curvature
    def get_curvature(self):
        return self.__curvature
    #
    def set_fids(self, fids):
        self.__fids = fids
    def add_fid(self, fid):
        self.__fids.append(fid)
    def get_fids(self):
        return self.__fids