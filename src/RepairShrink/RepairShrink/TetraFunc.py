import ModelData
import ModelDataFuncs
import os
import ClassFace
import SimpleMath
import CarveFunc
from ClassTetrahedron import Class_tetrahedron
import ClassTetrahedron
from collections import Counter
from ctypes import *

#deduce semantics for a valid shell
def deduce_semantics_of_poly(bIsSemantics):
    for fkey in ModelData.dictFaces:
        deduce_semantics_of_face(fkey)
    if ModelData.strModelID == '' and bIsSemantics:
        ModelData.strModelID = 'NonID'
        #multi surface
        ModelData.isSolid = '0' 

#Reconstruct the mesh from tetrahedron
#Delete dictFaces that have two neighbor tets from dictFaces dict
def extract_mesh_from_tet(bIsSemantics = False):
    print("----Extract the output mesh----")
    #check
    if len(ModelData.dictTetrahedrons) == 0:
        print("invalid call extract Mesh")
        return
    
    #deletion and deduce semantics
    for fkey in ModelData.dictFaces:
        #for testing 10 14 13
        if 10 in ModelData.dictFaces[fkey].get_vids():
            if 14 in ModelData.dictFaces[fkey].get_vids(): 
                if 13 in ModelData.dictFaces[fkey].get_vids():
                    fweaf = 3232 #faceid 8 fix not in shellfaceid!!!
        if fkey not in ModelData.listShellFaceIDs:
            ModelDataFuncs.pre_remove_face_by_faceids([fkey])

    #clearup
    if ModelDataFuncs.remove_faces() > 0:
        print ("Mesh extracted")
    
    #optimisazation
    if ModelDataFuncs.optimise_illshaped_shellfaces():
        ModelDataFuncs.remove_faces()
    ModelDataFuncs.clean_duplicated_vertices()
    ModelDataFuncs.clean_unreferenced_vertices()
    if ModelData.global_isRestoreNormal:
        ModelDataFuncs.restore_normals()
    #deduce semantics
    if bIsSemantics:
        deduce_semantics_of_poly(bIsSemantics)

#Find all the tets that contain the face (instance of ClassFace)
#needs speed up
def find_tetids_by_face(face, iNum = 2):
    tids = face.get_tids()
    if len(tids) > 0:
        return tids
    else:
        tetids = []
        for tid in ModelData.dictTetrahedrons:
            if ModelData.dictTetrahedrons[tid].is_triangle_in_tet(face):
                tetids.append(tid)
                if len(tetids) == iNum:
                    break
        return tetids

#Find all the tets that contain the face by its id
#needs speed up
def find_tetids_by_faceid(fid, iNum = 2):
    return find_tetids_by_face(ModelData.dictFaces[fid], iNum)

#Find all the tets that contain the vertex by its id
#needs speed up
def find_tetids_by_vertexid(vid):
    tetids = []
    for tid in ModelData.dictTetrahedrons:
        if vid in ModelData.dictTetrahedrons[tid].get_vids():
            tetids.append(tid)
    return tetids

#Extract all the recorded dictFaces from a tetrahedron by its index
def get_faceids_from_tetid_fast(tid):
    return ModelData.dictTetrahedrons[tid].get_fids()

#Extract all the recorded dictFaces from a tetrahedron by its index
#needs speed up 40%
#when the tets are created and when a new face is added or is deleted
def get_faceids_from_tetid(tid):
    faceids = []
    for key in ModelData.dictFaces:
        if ModelData.dictTetrahedrons[tid].is_triangle_in_tet(ModelData.dictFaces[key]):
            faceids.append(key)
            if len(faceids) == 4:
                break
    return faceids
#Extract all the recorded shellFaces from a tetrahedron by its index
def get_shell_faceids_from_tetid(tid):
    faceids = []
    for key in ModelData.listShellFaceIDs:
        if ModelData.dictTetrahedrons[tid].is_triangle_in_tet(ModelData.dictFaces[key]):
            faceids.append(key)
            if len(faceids) == 4:
                break
    return faceids

#Extract the cos of the dihedral angle between two faces
def get_dihedral_cos_angle(vids1, vids2):
    fNormal1 =  SimpleMath.get_face_normal((ModelData.dictVertices[vids1[0]], ModelData.dictVertices[vids1[1]], ModelData.dictVertices[vids1[2]]))
    fNormal2 =  SimpleMath.get_face_normal((ModelData.dictVertices[vids2[0]], ModelData.dictVertices[vids2[1]], ModelData.dictVertices[vids2[2]]))
    return SimpleMath.dot_product_3(fNormal1, fNormal2)

#building constrained delauney tetrahedralization CDT for models saved in ModelData
#The input should be free of intersection
def CDT():
    print("Start tetrahedralization....")
    curDirBefore = os.getcwd() 
    path = os.path.dirname(os.path.realpath(__file__))
    if sizeof(c_voidp) == 4:
        #win32
        path = os.path.join(path, '..\\tetgendll\\Release')
        os.chdir(path)
        if not os.path.exists("tetgendll.dll"):
            print("DLL missing: " + path + "tetgendll.dll")
        Tetrahedralator = CDLL("tetgendll.dll")
    elif sizeof(c_voidp) == 8:
        #x64
        path = os.path.join(path, '..\\tetgendll\\x64\\Release')
        os.chdir(path)
        if not os.path.exists("tetgendll.dll"):
            print("DLL missing: " + path + "tetgendll.dll")
        Tetrahedralator = CDLL("tetgendll.dll")
    os.chdir(curDirBefore)
    #be careful with the indices
    #record the indices of inserted dictVertices and map the indices in the dictFaces and tetrahedron to the finally added indices
    mapVertTet = {}
    iCount = 0
    cVertices = (c_double * (len(ModelData.dictVertices) * 3))() #the size of dictVertices *3
    for key in ModelData.dictVertices:
        cVertices[3*iCount] = c_double(ModelData.dictVertices[key][0])
        cVertices[3*iCount+1] = c_double(ModelData.dictVertices[key][1])
        cVertices[3*iCount+2] = c_double(ModelData.dictVertices[key][2])
        mapVertTet[iCount] = key
        iCount += 1

    iCount = 0
    cFaces = (c_int * (len(ModelData.dictFaces) * 3))() #the size of dictFaces * 3
    for key in ModelData.dictFaces:
        #be careful with the indices
        cFaces[3*iCount] = c_int(ModelDataFuncs.find_key_from_dict_by_exact_value(mapVertTet, ModelData.dictFaces[key].get_vids()[0]))
        cFaces[3*iCount+1] = c_int(ModelDataFuncs.find_key_from_dict_by_exact_value(mapVertTet, ModelData.dictFaces[key].get_vids()[1]))
        cFaces[3*iCount+2] = c_int(ModelDataFuncs.find_key_from_dict_by_exact_value(mapVertTet, ModelData.dictFaces[key].get_vids()[2]))
        iCount += 1

    numberOfOutputVerts = c_int(0);
    numberOfOutputTriangles = c_int(0);
    numberOfOutputTetrahedrons = c_int(0);

    try:
        Tetrahedralator.simpleTetrahedralize(byref(cVertices), c_int(len(ModelData.dictVertices)), byref(cFaces), c_int(len(ModelData.dictFaces)),
                                         byref(numberOfOutputVerts), byref(numberOfOutputTriangles), byref(numberOfOutputTetrahedrons))
    except ValueError:
        print("CDT failed")
        return False

    #check
    if numberOfOutputTetrahedrons.value == 0:
        print("tetrahedralization failed")
        return False
    #Get the results
    outputVerts = (c_double * (numberOfOutputVerts.value *3))()
    outputConvexhullTris = (c_int * (numberOfOutputTriangles.value *3))()
    outputTetrahedrons = (c_int * (numberOfOutputTetrahedrons.value *4))()

    Tetrahedralator.getResults(pointer(outputVerts), pointer(outputConvexhullTris), pointer(outputTetrahedrons))
   
    #update the ModelData
    #dictVertices
    if numberOfOutputVerts.value > len(ModelData.dictVertices):
        print("{} steiner points inserted (at the back of the original list)").format(numberOfOutputVerts.value - len(ModelData.dictVertices))
        for i in range(len(ModelData.dictVertices) * 3, numberOfOutputVerts.value * 3, 3):
            #be carefull with the indices (start with 0)
            mapVertTet[len(mapVertTet)] = ModelDataFuncs.add_vertex((outputVerts[i], outputVerts[i+1], outputVerts[i+2]))
    print("start building datastructure")
    #dictTetrahedrons
    for i in range(0, numberOfOutputTetrahedrons.value * 4, 4):
        ModelData.dictTetrahedrons[i/4] = Class_tetrahedron((mapVertTet[outputTetrahedrons[i]], mapVertTet[outputTetrahedrons[i+1]], mapVertTet[outputTetrahedrons[i+2]], mapVertTet[outputTetrahedrons[i+3]]))

    #extract the the triangles on the shell
    print("extract the triangles on the shell")
    isFaceDeleted = False
    for i in range(0, numberOfOutputTriangles.value*3, 3):
        print ("\r" + str(numberOfOutputTriangles.value - i/3) + "triangles left"),
        tris = (mapVertTet[outputConvexhullTris[i]], mapVertTet[outputConvexhullTris[i+1]], mapVertTet[outputConvexhullTris[i+2]])
        isExt = False
        for f in ModelData.dictFaces:
            if ModelData.dictFaces[f].is_equal_geometry(ClassFace.Class_face(tris)):
                #found the existing face
                isExt = True
                #add to the list of shell face
                ModelData.listShellFaceIDs.append(f)
                break
        if isExt == False:
            #distance mapping in case this geometry is produced by flipping the coplanar triangle
            fId = ModelDataFuncs.find_face_by_mapping(tris)
            if fId:
                ModelData.listShellFaceIDs.append(ModelDataFuncs.add_face(ClassFace.Class_face(tris, ClassFace.FIX, ModelData.dictFaces[fId].get_id(), ModelData.dictFaces[fId].get_type())))
                ModelDataFuncs.pre_remove_face_by_faceids([fId])
                isFaceDeleted = True
            else:
                #add the new face and add the face to the list of shell face
                ModelData.listShellFaceIDs.append(ModelDataFuncs.add_face(ClassFace.Class_face(tris)))
    #remove faces 
    if isFaceDeleted:
        ModelDataFuncs.remove_faces()
    
    #init the face members of a tet
    for tet in ModelData.dictTetrahedrons:
        fids = get_faceids_from_tetid(tet)
        ModelData.dictTetrahedrons[tet].set_fids(fids)

    #
    print ("After CDT: " + str(len(ModelData.dictTetrahedrons)) + " tetrahedra and " + str(len(ModelData.dictFaces)) + " dictFaces and " + str(len(ModelData.dictVertices)) + " dictVertices")
    return True

#deduce the id and type of a face by its geometry
def deduce_semantics_of_face(fid):
    #detect coplaner neighbours
    vertexList = ModelData.dictFaces[fid].get_vids()
    curNormal = SimpleMath.get_face_normal([ModelData.dictVertices[vertexList[0]], ModelData.dictVertices[vertexList[1]], ModelData.dictVertices[vertexList[2]]])
    if SimpleMath.vector_length_3(curNormal) > SimpleMath.Tol:
        #Get the normals of neighbors of this face
        tag = [fid]
        ModelDataFuncs.coplaner_neighbors_byDist(fid, tag)
        #statistic of dominant semantics within tagged faces
        counterSemantics = Counter()
        for fid in tag:
            counterSemantics[(ModelData.dictFaces[fid].get_id(), ModelData.dictFaces[fid].get_type())] += 1
        res = counterSemantics.most_common(2)
        #get the semantics
        strId = ''
        strType = ''
        if len(res) == 1 and res[0][0] == ('', ''):
            #deduce the semantics based on direction 
            strId = ModelDataFuncs.generate_uuid()
            angle = SimpleMath.dot_product_3(curNormal, (0.0, 0.0, 1.0))
            if angle <= 1 and angle > 0.087:
                #roof 0 to 85
                strType = 'BUILDING_ROOF_SURFACE'
            elif angle < -0.999:
                #ground -0 to -1
                strType = 'BUILDING_GROUND_SURFACE'
            else:
                #wall
                strType = 'BUILDING_WALL_SURFACE'
        else:
            if res[0][0] != ('', ''):
                strId = res[0][0][0]
                strType = res[0][0][1]
            elif res[1][0] != ('', ''):
                strId = res[1][0][0]
                strType = res[1][0][1]
        #assign the semantics to all the raw face in tag
        for f in tag:
            if ModelData.dictFaces[f].get_id() == '' :
                 ModelData.dictFaces[f].set_id(strId)
            if ModelData.dictFaces[f].get_type() == '' :
                 ModelData.dictFaces[f].set_type(strType)
    else:
        ModelData.dictFaces[fid].set_id(ModelDataFuncs.generate_uuid())
        ModelData.dictFaces[fid].set_type('BUILDING_WALL_SURFACE')

