import ModelData
import SimpleMath
#the condition of a face
#INF means postponed (used in carving) DEL means needs deletion, FIX means the input faces, TMP means generated face, KEEP means the kept face (differ from FIX), the list can be extended
INF = 0
DEL = 1
FIX = 2
TMP = 3
KEEP = 4 #defined because only the normal of FIX can be trusted
FLIP = 5

class Class_face(object):
    """description of class"""
    #the triangle is represented by three vertex indices v (vid1, vid2, vid3) two attributes id and type, and a tag (To be delete, In the result, etc.)
    def __init__(self, v, tag = TMP, id = '', type = ''):
        self.__v = v
        self.__tag = tag
        #record neighourfaceids and tetids
        self.__neighbour = []
        self.__incidentTids = []
        #semantics (id and type)
        self.__strId = id
        self.__strType = type
        #uid (for detecting redundancy)
        self.__uId = v[0] + v[1] + v[2]

    #calculate the area of the face
    def get_area(self):
        pt1 = ModelData.dictVertices[self.__v[0]]
        pt2 = ModelData.dictVertices[self.__v[1]]
        pt3 = ModelData.dictVertices[self.__v[2]]
        pt1pt2 = SimpleMath.tuple_minus(pt2, pt1)
        pt1pt3 = SimpleMath.tuple_minus(pt3, pt1)
        return 0.5 * SimpleMath.vector_length_3(SimpleMath.cross_product_3(pt1pt2, pt1pt3))
     
    #calculate the normal of the face
    def get_normal(self):
        pt1 = ModelData.dictVertices[self.__v[0]]
        pt2 = ModelData.dictVertices[self.__v[1]]
        pt3 = ModelData.dictVertices[self.__v[2]]
        return tuple(SimpleMath.get_face_normal((pt1, pt2, pt3)))
       
    #
    def set_vids(self, vids):
        self.__v = vids
    #
    def get_vids(self):
        return self.__v
    #
    def set_tag(self, tag):
        self.__tag = tag
    #
    def get_tag(self):
        return self.__tag
    #
    def set_id(self, strId):
        self.__strId = strId
    def get_id(self):
        return self.__strId

    #
    def get_uid(self):
        return self.__uId

    def update_uid(self):
        self.__uId = self.__v[0] + self.__v[1] + self.__v[2]

    #for speed up
    def set_tid(self, tid):
        self.__incidentTids.append(tid)
    def get_tids(self):
        return self.__incidentTids
    #
    def set_type(self, strType):
        self.__strType = strType
    #
    def get_type(self):
        return self.__strType

    #
    def is_equal_geometry(self, f):
        if f.get_uid() != self.get_uid():
            return False
        for v in f.get_vids():
            if v not in self.__v:
                return False
        return True
    #
    def is_equal_semantics(self, f):
        if self.get_id() == f.get_id() and \
        self.get_type() == f.get_type() and \
        self.get_tag() == f.get_tag():
            return True
        else:
            return False
    #
    def is_identical(self, f):
        if is_equal_geometry(f) and is_equal_semantics(f):
            return True
        else:
            return False