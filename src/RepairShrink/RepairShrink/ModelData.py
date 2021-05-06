import collections

#Paradigm control
#whether conduct delauney decomposition of intersected triangles (True == delaunay decompose, False == triangle split)
#should always be True
global_DELAUNAY_TESS = True
#invert the normal of the input
global_INVERT_NORMAL = False

#whether to truncate coordinates before repair (input) 
#rotterdam 5(good results with modertate failed cases) 1 (modertate results with some errorneous) 201708
#others false
global_DO_TRUNCATE  = False
global_TOL_TRUNCATE = 5

#whether to welding coordinates (after decomposition) 0.03  
#rotterdam dataset 201708 True 10
global_DO_WELDING = False
global_TOL_WELDING = 10

#whether to discard degenerated dictFaces before repair
global_DISCARD_DEG = False

#whether to discard tiny dictFaces before CDT and repair (test 602.obj)0.1
#rotterdam dataset 201708 True 7
global_DISCARD_TINY = False
global_TOL_AREA_DISCARD = 7

#whether to optimise the tiny dictFaces after repair
global_OPTIMAL_SHP = True 
global_TOL_LARGEST_ANGLE = -0.99 #175 degree

#whether restore the normal of the final result
global_isRestoreNormal = True
#all the input geometric primitives, use functions below to manipulate
#dictFaces can be added at anytime but should be cleaned up by first mark the face that to be delete and then clean them all
#dictFaces is an ordered dictionary of {faceid:ClassFace}
#dictVertices is an ordered dictionary of {vertexid:tuple}
#dictTetrahedrons is a dictionary of {tetrahedronid:ClassTetrahedron}
#strModelID is the id of the model to be repaired
#isSolid is a CityGML specific tag
strModelID = ''
isSolid = ''
dictFaces = collections.OrderedDict()
dictVertices = collections.OrderedDict()

#record the center vertex of the dictVertices and translate all the input verts to the origin and scaled the vertex with 1e3
centerVertex = (0.0, 0.0, 0.0)
scaleVertex = 1
maxpt = 0
minpt = 0
dictTetrahedrons = {}
#all the faces on the shell of the model 
listShellFaceIDs = []
#all the geometry primitives of the result
#Hull_faces is a dictionary of {faceid:ClassFace}
#Hull_faces = collections.OrderedDict({})

#record the first 4 principle direction of all the faces
listPrincipleNormal = []

#smallest avalible unique ID start from 0
#they should be always in an ascending order and keep unchanged for the same primitive
faceID = 0
vertexID = 0

#for experiment use
UUID = 0

#for the input filename
strInputFileName = ''


######for experiment only restore and recover thedata
ownFaces = collections.OrderedDict()
ownVerts = collections.OrderedDict()
ownTetrahedron = {}
ownlistShellFaceIDs = []
ownlistPrincipleNormal = []
ownfaceID = 0
ownvertexID = 0
