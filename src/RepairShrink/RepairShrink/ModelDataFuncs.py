import os
import operator
from ctypes import *
import ModelData
import ClassFace
import ClassTetrahedron
from ClassFace import Class_face
import SimpleMath
from TetraFunc import find_tetids_by_face
import CarveFunc
import sys
import copy
#sys.setrecursionlimit(10000000)

def Init():
    ModelData.dictFaces.clear()
    ModelData.dictVertices.clear()
    ModelData.dictTetrahedrons.clear()
    ModelData.listShellFaceIDs = []
    ModelData.listPrincipleNormal = []
    ModelData.faceID = 0
    ModelData.vertexID = 0
    ModelData.centerVertex = (0.0, 0.0, 0.0)
    ModelData.scaleVertex = 1e3
    ModelData.maxpt = [-9999999999.0, -9999999999.0, -9999999999.0]
    ModelData.minpt = [9999999999.0, 9999999999.0, 9999999999.0]

#orientate given vertices, according to the given orientation
#vIds is a tuple of (idV1, idV2, idV3), normalFace is the normal of the correct orientation
def create_orientated_vids(vids, normal):
    if SimpleMath.vector_length_3Ex(normal) < SimpleMath.Tol:
        print('Degeneracy!!')
        return vids
    fNormal = SimpleMath.get_face_normal([ModelData.dictVertices[vids[0]], ModelData.dictVertices[vids[1]], ModelData.dictVertices[vids[2]]])
    if SimpleMath.dot_product_3(normal, fNormal) > 0:
        return vids
    else:
        return (vids[1], vids[0], vids[2])

#Add a face objec to ModelData.dictFaces, return the index of current face and also check redundency
def add_face(f):
    for v in f.get_vids():
        if f.get_vids().count(v) > 1:
            #degenerated face
            return -1
    for key in ModelData.dictFaces:
        if ModelData.dictFaces[key].is_equal_geometry(f):
            if ModelData.dictFaces[key].is_equal_semantics(f):
                return key
            else:
                print("replace same face geometry with different semantics")
                #rules to preserve the ModelData.dictFaces
                #if ClassFace.DEL in [ModelData.dictFaces[key].get_tag(), f.get_tag()]:
                #    ModelData.dictFaces[key].get_tag() = ClassFace.DEL
                #if f.get_tag() == ClassFace.FIX and ModelData.dictFaces[key].get_tag() == ClassFace.TMP:
                #    ModelData.dictFaces[key].get_tag() = ClassFace.TMP
                ModelData.dictFaces[key] = f
                return key
    #update tet information 160911 for speeding up
    if len(ModelData.dictTetrahedrons) > 0:
        tets = find_tetids_by_face(f)
        for tet in tets:
            ModelData.dictTetrahedrons[tet].add_fid(ModelData.faceID)

    ModelData.dictFaces[ModelData.faceID] = f
    ModelData.faceID = ModelData.faceID + 1
    if ModelData.faceID-1 == 20:
        feafea = 99
    return ModelData.faceID-1

#mark a set of ModelData.dictFaces to be deleted
def pre_remove_face_by_faceids(fids):
    for fid in fids:
        ModelData.dictFaces[fid].set_tag(ClassFace.DEL)

#Add a v(x, y, z) to ModelData.dictVertices and add the ModelData.vertexID, return the index of current vertex and also check redundency
def add_vertex(v):
    for key in ModelData.dictVertices:
        if is_have_same_vert(ModelData.dictVertices[key], [v]):
            return key
    ModelData.dictVertices[ModelData.vertexID] = v
    ModelData.vertexID = ModelData.vertexID + 1
    if ModelData.vertexID-1 == 20:
        fewfw = 99
    return ModelData.vertexID-1

#directly add a v(x, y, z) to ModelData.dictVertices and add the ModelData.vertexID, return the index of current vertex should be used together with CleanUpvertices()
def add_vertexEx(v):
    ModelData.dictVertices[ModelData.vertexID] = v
    ModelData.vertexID = ModelData.vertexID + 1
    return ModelData.vertexID-1

#remove a vertex by its id
def remove_vertex_by_vid(vid):
     try:
        ModelData.dictVertices.pop(vid)
     except KeyError:
        print("Delete wrong vertex")

#read the tessellated Obj file
#INPUT: FILEPATH is the fullpath of the obj file
#OUTPUT: ModelData.dictFaces and ModelData.dictVertices in ModelData
#RETURN: True means successed False means failed
def reader_obj(FILEPATH):
    try:
        f_obj = file(FILEPATH, 'r')
    except:
        print ("Invalide file: " + MIDFILEPATH)
        return False
    #read vertics and ModelData.dictFaces
    statFace = 0
    for line in f_obj:
        #print '.',
        if line.startswith('v') and line[1] == ' ':
            line = line[1:-1].strip()
            vertList = map(float, line.split(' '))
            add_vertexEx([vertList[0], vertList[1], vertList[2]])
        elif line.startswith('f') and line[1] == ' ':
            indexList = []
            #to filter out the /
            for index in line[1:-1].strip().split(' '):
                indexList.append(index.split('/')[0])
            statFace = statFace + 1
            print "\rread faces: " + str(statFace),
            if len(indexList) > 2:
                #index - 1
                indexList = [int(i)-1 for i in indexList]
                add_face(Class_face((indexList[0], indexList[1], indexList[2]), ClassFace.FIX))
    #check the content
    if len(ModelData.dictFaces) == 0 or len(ModelData.dictVertices) == 0:
        print "Invalid Obj file!\n"
        return False
    else:
        print("Remove " + str(statFace - len(ModelData.dictFaces)) + " invalid ModelData.dictFaces")
        print("Read " + str(len(ModelData.dictFaces)) + " ModelData.dictFaces and " + str(len(ModelData.dictVertices)) + " ModelData.dictVertices")

    f_obj.close()

    #optimise the coordinates by translate and scale
    for key in ModelData.dictVertices:
        ModelData.centerVertex = SimpleMath.tuple_plus(ModelData.centerVertex, ModelData.dictVertices[key])
    ModelData.centerVertex = SimpleMath.tuple_numproduct(1.0/len(ModelData.dictVertices),ModelData.centerVertex)
    #ModelData.maxpt = [-9999999999.0, -9999999999.0, -9999999999.0]
    #ModelData.minpt = [9999999999.0, 9999999999.0, 9999999999.0]
    for key in ModelData.dictVertices:
        ModelData.dictVertices[key] = SimpleMath.tuple_minus(ModelData.dictVertices[key], ModelData.centerVertex)
        if ModelData.dictVertices[key][0] > ModelData.maxpt[0]:
            ModelData.maxpt[0] = ModelData.dictVertices[key][0]
        if ModelData.dictVertices[key][1] > ModelData.maxpt[1]:
            ModelData.maxpt[1] = ModelData.dictVertices[key][1]
        if ModelData.dictVertices[key][2] > ModelData.maxpt[2]:
            ModelData.maxpt[2] = ModelData.dictVertices[key][2]

        if ModelData.dictVertices[key][0] < ModelData.minpt[0]:
            ModelData.minpt[0] = ModelData.dictVertices[key][0]
        if ModelData.dictVertices[key][1] < ModelData.minpt[1]:
            ModelData.minpt[1] = ModelData.dictVertices[key][1]
        if ModelData.dictVertices[key][2] < ModelData.minpt[2]:
            ModelData.minpt[2] = ModelData.dictVertices[key][2]
    ModelData.scaleVertex = ModelData.scaleVertex / SimpleMath.vector_length_3(SimpleMath.tuple_minus(ModelData.maxpt, ModelData.minpt))
    for key in ModelData.dictVertices:
        ModelData.dictVertices[key] = SimpleMath.tuple_numproduct(ModelData.scaleVertex, ModelData.dictVertices[key])
    if ModelData.global_DO_TRUNCATE:
        truncate_verts(ModelData.global_TOL_TRUNCATE)
    print(">>>>>>Eliminate degeneracies...")
    clean_duplicated_vertices()
    print("{} illshaped ModelData.dictFaces are removed").format(discard_illshaped_faces())
    print("After cleaning redundant ModelData.dictVertices there are " + str(len(ModelData.dictFaces)) + " ModelData.dictFaces and " + str(len(ModelData.dictVertices)) + " ModelData.dictVertices")
    return True

#write the ModelData.dictFaces, ModelData.dictVertices and Hull_faces, Hull_vertices to the output file
#FILEPATH1 for ModelData.ModelData.dictFaces and ModelData.ModelData.dictVertices
def writer_obj (FILEPATH1):
    if len(ModelData.dictVertices) > 0 and len (ModelData.dictFaces) > 0:
        try:
            f_obj1 = file(FILEPATH1, 'w')
        except:
            print ("Invalide file: " + FILEPATH1)
            raise Exception

        #write the ModelData.dictFaces and ModelData.dictVertices
        f_obj1.write("# Created by obj2poly from ModelData.ModelData.dictFaces and ModelData.ModelData.dictVertices \n")
        f_obj1.write("# Object\n")
        #using mtl to show the face statues
        f_obj1.write("mtllib shrinkwrapping.mtl \n")
        #indicemap
        verticeMap = {}
        iVertCount = 1
        #ModelData.dictVertices
        for vert in ModelData.dictVertices:
            verticeMap[iVertCount] = vert
            iVertCount += 1
            f_obj1.write("v ")
            #f_obj1.write(str(SimpleMath.tuple_plus(SimpleMath.tuple_numproduct(1/ ModelData.scaleVertex, ModelData.dictVertices[vert]), ModelData.centerVertex)).replace(',', '')[1:-1] + '\n')
            f_obj1.write(str(SimpleMath.tuple_plus(ModelData.dictVertices[vert], ModelData.centerVertex)).replace(',', '')[1:-1] + '\n')
        f_obj1.write("# ")
        f_obj1.write(str(len(ModelData.dictVertices)) + ' ')
        f_obj1.write("ModelData.dictVertices\n")

        #ModelData.dictFaces 
        for face in ModelData.dictFaces:
            #write the mtl
            if ModelData.dictFaces[face].get_tag() == ClassFace.FIX:
                f_obj1.write("usemtl Fix\n")
            elif ModelData.dictFaces[face].get_tag() == ClassFace.TMP:
                f_obj1.write("usemtl Tmp\n")
            elif ModelData.dictFaces[face].get_tag() == ClassFace.KEEP:
                f_obj1.write("usemtl Keep\n")
            #correct indice mapping
            f = []
            for vert in ModelData.dictFaces[face].get_vids():
                f.append(find_key_from_dict_by_exact_value(verticeMap, vert))
            f_obj1.write("f ")
            f_obj1.write(str(f).replace(',', '')[1:-1] + '\n')
        f_obj1.write("# ")
        f_obj1.write(str(len(ModelData.dictFaces)) + ' ')
        f_obj1.write("ModelData.dictFaces\n")
        f_obj1.close()
        #end __WriteObj
    return True

#read poly files with semantics
#the polygon will be triangulated and semantics will be inherited
def reader_poly_with_semantics(str_filepath):
    fin = file(str_filepath, 'r')
    #read the first line and try to extract semantics
    strFirstLine = fin.readline().split()
    if strFirstLine[0] == '#':
        #read the building id
        ModelData.strModelID = strFirstLine[1]
        #whether the geometry is a solid:1 or a multisurface:0
        ModelData.isSolid = fin.readline().split()[1]
        #the point information
        strFirstLine = int(fin.readline().split()[0])
    else:
        #no semanics
        ModelData.strModelID = '-1'
        #we assume it is a solid
        ModelData.isSolid = '1'
        #the point information
        strFirstLine = int(strFirstLine[0])
    #read all the points
    for i in range(strFirstLine):
        vertList = map(float, fin.readline().split()[1:4])
        add_vertexEx((vertList[0], vertList[1], vertList[2]))
    #read each face
    nof = int(fin.readline().split()[0])
    strPolygonid = ''
    strPolygontype = ''
    for i in range(nof):
        strPolygoninfo = fin.readline().split()
        numRings = int(strPolygoninfo[0])
        if numRings != 1:
            print ('The input has not been tesselated')
            return False
        if len(strPolygoninfo) >= 4:
            strPolygonid = strPolygoninfo[3]
        if len(strPolygoninfo) >= 6:
            strPolygontype = strPolygoninfo[5]
        oring = map(int, fin.readline().split())
        if len(oring) > 4:
            print ('The input has not been tesselated')
            return False
        oring.pop(0)
        if len(oring) == 3:
            add_face(Class_face((oring[0], oring[1], oring[2]), ClassFace.FIX, strPolygonid, strPolygontype))

    #check the content
    if len(ModelData.dictFaces) == 0 or len(ModelData.dictVertices) == 0:
        print "Invalid Poly file!\n"
        return False
    else:
        print("Remove " + str(nof - len(ModelData.dictFaces)) + " invalid Faces")
        print("Read " + str(len(ModelData.dictFaces)) + " Faces and " + str(len(ModelData.dictVertices)) + " Vertices")
    fin.close()
    
    #optimise the coordinates by translate and scale
    for key in ModelData.dictVertices:
        ModelData.centerVertex = SimpleMath.tuple_plus(ModelData.centerVertex, ModelData.dictVertices[key])
    ModelData.centerVertex = SimpleMath.tuple_numproduct(1.0/len(ModelData.dictVertices), ModelData.centerVertex)

    #added 20170903
    for key in ModelData.dictVertices:
        ModelData.dictVertices[key] = SimpleMath.tuple_minus(ModelData.dictVertices[key], ModelData.centerVertex)
        if ModelData.dictVertices[key][0] > ModelData.maxpt[0]:
            ModelData.maxpt[0] = ModelData.dictVertices[key][0]
        if ModelData.dictVertices[key][1] > ModelData.maxpt[1]:
            ModelData.maxpt[1] = ModelData.dictVertices[key][1]
        if ModelData.dictVertices[key][2] > ModelData.maxpt[2]:
            ModelData.maxpt[2] = ModelData.dictVertices[key][2]

        if ModelData.dictVertices[key][0] < ModelData.minpt[0]:
            ModelData.minpt[0] = ModelData.dictVertices[key][0]
        if ModelData.dictVertices[key][1] < ModelData.minpt[1]:
            ModelData.minpt[1] = ModelData.dictVertices[key][1]
        if ModelData.dictVertices[key][2] < ModelData.minpt[2]:
            ModelData.minpt[2] = ModelData.dictVertices[key][2]

    ModelData.scaleVertex = ModelData.scaleVertex / SimpleMath.vector_length_3(SimpleMath.tuple_minus(ModelData.maxpt, ModelData.minpt))
    for key in ModelData.dictVertices:
        ModelData.dictVertices[key] = SimpleMath.tuple_numproduct(ModelData.scaleVertex, ModelData.dictVertices[key])

    if ModelData.global_DO_TRUNCATE:
        truncate_verts(ModelData.global_TOL_TRUNCATE)
    print("--Eliminate degeneracies")
    clean_duplicated_vertices()
    print("{} illshaped ModelData.dictFaces are removed").format(discard_illshaped_faces())
    print("After cleaning redundant ModelData.dictVertices there are " + str(len(ModelData.dictFaces)) + " Faces and " + str(len(ModelData.dictVertices)) + " Vertices")
    return True

#write poly files with semantics
#triangles with he same id will not be merged
def writer_poly_with_semantics(str_filepath):
    fout = file(str_filepath, 'w')
    #write the model information
    fout.write('# ' + ModelData.strModelID + '\n')
    fout.write('# ' + ModelData.isSolid + '\n')
    #write all the points
    fout.write(str(len(ModelData.dictVertices))+ '  3 0 0\n')
    iVertCount = 0
    #ModelData.dictVertices
    verticeMap = {}
    for vert in ModelData.dictVertices:
        verticeMap[iVertCount] = vert
        fout.write(str(iVertCount) + '  ')
        fout.write(str(SimpleMath.tuple_plus(ModelData.dictVertices[vert], ModelData.centerVertex)).replace(',', '')[1:-1] + '\n')
        #fout.write(str(SimpleMath.tuple_plus(SimpleMath.tuple_numproduct(1/ ModelData.scaleVertex, ModelData.dictVertices[vert]), ModelData.centerVertex)).replace(',', '')[1:-1] + '\n')
        iVertCount += 1
    #write ModelData.dictFaces and remapping the indices
    fout.write(str(len(ModelData.dictFaces)) + ' 0\n')
    for face in ModelData.dictFaces:
            #write the face information
        fout.write('1 0 ')
        if ModelData.dictFaces[face].get_id() != '':
            fout.write('# ' + ModelData.dictFaces[face].get_id() + ' ')
        if ModelData.dictFaces[face].get_type() != '':
            fout.write('# ' + ModelData.dictFaces[face].get_type())
        fout.write('\n')
        #correct indice mapping
        f = []
        for vert in ModelData.dictFaces[face].get_vids():
            f.append(find_key_from_dict_by_exact_value(verticeMap, vert))
        fout.write('3  ')
        fout.write(str(f).replace(',', '')[1:-1] + '\n')
    fout.write('0\n')
    fout.write('0\n')
    fout.close()


#truncate vert coordinates to alleiave rounding off error (should only use after importing)
#vts is the ModelData.dictVertices
def truncate_verts(digit):
    for v in ModelData.dictVertices:
        ModelData.dictVertices[v] = [round(vt, digit) for vt in ModelData.dictVertices[v]]

#welding vert coordinates to alleiave rounding off error (simple version)
#vts is the ModelData.dictVertices
def welding_verts(tol):
    for i in range(0, ModelData.vertexID):
        for j in range(i+1, ModelData.vertexID):
            if i in ModelData.dictVertices and j in ModelData.dictVertices:
                if SimpleMath.square_dist_point_to_point(ModelData.dictVertices[i] , ModelData.dictVertices[j]) < tol * tol:
                     ModelData.dictVertices[j] =  ModelData.dictVertices[i] 


#check whether a triangle is one of the ModelData.dictFaces of a tetrahedron
#tri is a list of 3 ints and tet is a list of 4 ints
#def is_triangle_in_tet(tri, tet):
#    for v in tri:
#        if v not in tet:
#            return False
#    return True

##check whether two triangles/polygons are equal
##tri is a list of ints
#def is_triangle_equal_triangle(tri1, tri2):
#    for v in tri1:
#        if v not in tri2:
#            return False
#    return True

#only for int and string, not float
def find_key_from_dict_by_exact_value(dict, value):
    if len(dict) > 1000:
        return dict.keys()[dict.values().index(value)]
    else:
        for k in dict:
            if dict[k] == value:
                return k

#remove the illshaped ModelData.dictFaces at once
def discard_illshaped_faces():
    iCount = 0
    for key in ModelData.dictFaces:
        if ModelData.global_DISCARD_TINY:
            if ModelData.dictFaces[key].get_area() < ModelData.global_TOL_AREA_DISCARD:
                pre_remove_face_by_faceids([key])
                iCount = iCount + 1
                continue
        if ModelData.global_DISCARD_DEG:
            vert0 = ModelData.dictVertices[ModelData.dictFaces[key].get_vids()[0]]
            vert1 = ModelData.dictVertices[ModelData.dictFaces[key].get_vids()[1]]
            vert2 = ModelData.dictVertices[ModelData.dictFaces[key].get_vids()[2]]
            if SimpleMath.vector_length_3(SimpleMath.get_face_normal([vert0, vert1, vert2])) < SimpleMath.Tol:
                pre_remove_face_by_faceids([key])
                iCount = iCount + 1
    #
    remove_faces()
    clean_unreferenced_vertices()       
    return iCount
    

#clean up the ModelData.dictFaces at once should be used to remove pre-deleted ModelData.dictFaces
def remove_faces():
    for key in ModelData.dictFaces:
        if ModelData.dictFaces[key].get_tag() == ClassFace.DEL:
            try:
                ModelData.dictFaces.pop(key)
                if key in ModelData.listShellFaceIDs:
                    if key == 156:
                        fewafeaw = 9
                    ModelData.listShellFaceIDs.remove(key)
            except KeyError:
                print("Delete wrong face")
                return False
    #
    #clean_unreferenced_vertices()
    return True

#remove the unreferenced ModelData.dictVertices from Modeldata, use it only when needed
def clean_unreferenced_vertices():
    #collected ModelData.dictVertices
    referencedVertIds = []
    if len(ModelData.dictTetrahedrons) > 0:
        for tkey in ModelData.dictTetrahedrons:
            for i in range(0,4):
                if ModelData.dictTetrahedrons[tkey].get_vids()[i] not in referencedVertIds:
                    referencedVertIds.append(ModelData.dictTetrahedrons[tkey].get_vids()[i])
    if len(ModelData.dictFaces) > 0:
        for fkey in ModelData.dictFaces:
            for i in range(0,3):
                if ModelData.dictFaces[fkey].get_vids()[i] not in referencedVertIds:
                    referencedVertIds.append(ModelData.dictFaces[fkey].get_vids()[i])
    for vkey in ModelData.dictVertices:
        if vkey not in referencedVertIds:
            try:
                ModelData.dictVertices.pop(vkey)
            except IndexError:
                print("delete the wrong vertex")

#remove the duplicated ModelData.dictVertices and modify the corresponding face indice
#a bug was fixed 20170826 when the face being updated the uid should also be updated
def clean_duplicated_vertices():
    for key1 in ModelData.dictVertices:
        for key2 in ModelData.dictVertices:
            if key1 >= key2:
                continue
            if is_have_same_vert(ModelData.dictVertices[key1], [ModelData.dictVertices[key2]]):
                #replace key2 with key1 in ModelData.dictFaces
                for fk in ModelData.dictFaces:
                    f = list(ModelData.dictFaces[fk].get_vids())
                    if f[0] == key2:
                        f[0] = key1
                    if f[1] == key2:
                        f[1] = key1
                    if f[2] == key2:
                        f[2] = key1
                    ModelData.dictFaces[fk].set_vids(f)
                    ModelData.dictFaces[fk].update_uid()
                    if f.count(f[0]) > 1 or f.count(f[1]) > 1 or f.count(f[2]) > 1:
                        ModelData.dictFaces.pop(fk)
                        if fk in ModelData.listShellFaceIDs:
                            ModelData.listShellFaceIDs.remove(fk)
                #delete key2
                try:
                    ModelData.dictVertices.pop(key2)
                except ValueError:
                    print ("Delete wrong vertex")
                    return False
    return True

def reorder_datastructure():
    #reorder ModelData.dictVertices
    #creat the map
    vertMap = {}
    vertCache = []
    iCount = 0
    for key in ModelData.dictVertices:
        vertCache.append(ModelData.dictVertices[key])
        vertMap[key] = iCount
        iCount = iCount + 1
    #reorder ModelData.dictFaces
    #faceCache = []
    for key in ModelData.dictFaces:
        for v in ModelData.dictFaces[key].get_vids():
            v = vertMap[v]
        #faceCache.append(ModelData.dictFaces[key])
    #reorder ModelData.dictTetrahedrons
    for key in ModelData.dictTetrahedrons:
        for v in ModelData.dictTetrahedrons[key].get_vids():
            v = vertMap[v]
    #refill ModelData.dictVertices
    del ModelData.dictVertices[:]
    ModelData.vertexID = 0
    for v in vertCache :
        add_vertex(v)
    #refill ModelData.dictFaces
    #del ModelData.dictFaces[:]
    #ModelData.faceID = 0
    #for f in faceCache :
    #    add_face(f)

#detect all the degenerated ModelData.dictFaces and resolve them by edge collapsing or flipping (only used in the result)
def optimise_illshaped_shellfaces():
    iCount = 0
    for key in ModelData.listShellFaceIDs:
        if key not in ModelData.dictFaces:
            continue
        if ModelData.global_OPTIMAL_SHP and ModelData.dictFaces[key].get_tag() != ClassFace.FLIP and ModelData.dictFaces[key].get_area() < ModelData.global_TOL_AREA_DISCARD:
            vert0 = ModelData.dictVertices[ModelData.dictFaces[key].get_vids()[0]]
            vert1 = ModelData.dictVertices[ModelData.dictFaces[key].get_vids()[1]]
            vert2 = ModelData.dictVertices[ModelData.dictFaces[key].get_vids()[2]]
            #face collapse or flip
            #calculate vectors
            vector01 = SimpleMath.tuple_minus(vert0, vert1)
            length01 = SimpleMath.vector_length_3(vector01)
            if length01 > SimpleMath.Tol:
                vector01 = SimpleMath.tuple_numproduct(1.0/length01, vector01)
            else:
                iCount += 1
                collapse_edge(ModelData.dictFaces[key].get_vids()[0], ModelData.dictFaces[key].get_vids()[1])
                continue

            vector21 = SimpleMath.tuple_minus(vert2, vert1)
            length21 = SimpleMath.vector_length_3(vector21)
            if length21 > SimpleMath.Tol:
                vector21 = SimpleMath.tuple_numproduct(1.0/length21, vector21)
            else:
                iCount += 1
                collapse_edge(ModelData.dictFaces[key].get_vids()[2], ModelData.dictFaces[key].get_vids()[1])
                continue

            vector02 = SimpleMath.tuple_minus(vert0, vert2)
            length02 = SimpleMath.vector_length_3(vector02)
            if length02 > SimpleMath.Tol:
                vector02 = SimpleMath.tuple_numproduct(1.0/length02, vector02)
            else:
                iCount += 1
                collapse_edge(ModelData.dictFaces[key].get_vids()[0], ModelData.dictFaces[key].get_vids()[2])
                continue
                
            #calculate angles
            Ang012 =  SimpleMath.dot_product_3(vector01, vector21)
            Ang102 =  SimpleMath.dot_product_3(vector01, vector02)
            vector12 = SimpleMath.tuple_numproduct(-1, vector21)
            Ang021 =  SimpleMath.dot_product_3(vector02, vector12)
            #cos value
            if Ang012 < ModelData.global_TOL_LARGEST_ANGLE:
                #flip 20
                iCount += 1
                flip_edge(ModelData.dictFaces[key].get_vids()[2], ModelData.dictFaces[key].get_vids()[0])
            elif Ang102 < ModelData.global_TOL_LARGEST_ANGLE:
                #flip 12
                iCount += 1
                flip_edge(ModelData.dictFaces[key].get_vids()[1], ModelData.dictFaces[key].get_vids()[2])
            elif Ang021 < ModelData.global_TOL_LARGEST_ANGLE:
                #flip 01
                iCount += 1
                flip_edge(ModelData.dictFaces[key].get_vids()[0], ModelData.dictFaces[key].get_vids()[1])
    #
    #clean_unreferenced_vertices()       
    print("{} illshaped ModelData.dictFaces are optimized").format(iCount)
    if iCount > 0:
        return True
    else:
        return False


#collapse edge and update local ModelData.dictFaces(vid1, vid2)
def collapse_edge(vid1, vid2):
    ModelData.dictVertices[vid1] = ModelData.dictVertices[vid2]
    clean_duplicated_vertices()

#flip edge and update local ModelData.dictFaces(vid1, vid2)
#the order of vids is important!
def flip_edge(vid1, vid2):
    #
    IncidentFaces = []
    OppoVerts = []
    for fkey in ModelData.dictFaces:
        if vid1 in ModelData.dictFaces[fkey].get_vids() and vid2 in ModelData.dictFaces[fkey].get_vids():
            IncidentFaces.append(fkey)
            for vid in ModelData.dictFaces[fkey].get_vids():
                if vid not in [vid1, vid2]:
                    OppoVerts.append(vid)
            if len(IncidentFaces) == 2:
                break
    #
    #fnormal1 = SimpleMath.get_face_normal([ModelData.dictVertices[ModelData.dictFaces[IncidentFaces[0]].get_vids()[0]], ModelData.dictVertices[ModelData.dictFaces[IncidentFaces[0]].get_vids()[1]], ModelData.dictVertices[ModelData.dictFaces[IncidentFaces[0]].get_vids()[2]]])
    #fnormal2 = SimpleMath.get_face_normal([ModelData.dictVertices[ModelData.dictFaces[IncidentFaces[1]].get_vids()[0]], ModelData.dictVertices[ModelData.dictFaces[IncidentFaces[1]].get_vids()[1]], ModelData.dictVertices[ModelData.dictFaces[IncidentFaces[1]].get_vids()[2]]])
    #if abs(SimpleMath.dot_product_3(fnormal1, fnormal2)) > SimpleMath.NeighborAngle:
    #    print("Caution! Flipping an edge of two noncoplaner ModelData.dictFaces!")
    #    return False
    #    #raise ValueError
    #if ModelData.dictFaces[IncidentFaces[0]].get_tag() != ModelData.dictFaces[IncidentFaces[1]].get_tag():
    #    print("Caution! Flipping an edge of two different kinds of ModelData.dictFaces!")
    #    return False
    #    #raise ValueError
    #if ModelData.dictFaces[IncidentFaces[0]].get_id() != ModelData.dictFaces[IncidentFaces[1]].get_id():
    #    print("Caution! Flipping an edge of two ModelData.dictFaces having different ids!")
    #    return False

    #add new ModelData.dictFaces
    #ModelData.listShellFaceIDs.append(add_face(Class_face((OppoVerts[0], vid1, OppoVerts[1]), ModelData.dictFaces[IncidentFaces[0]].get_tag(), ModelData.dictFaces[IncidentFaces[0]].get_id(),
    #                    ModelData.dictFaces[IncidentFaces[0]].get_type())))
    #ModelData.listShellFaceIDs.append(add_face(Class_face((OppoVerts[1], vid2, OppoVerts[0]), ModelData.dictFaces[IncidentFaces[1]].get_tag(), ModelData.dictFaces[IncidentFaces[1]].get_id(),
    #                    ModelData.dictFaces[IncidentFaces[1]].get_type())))
    ModelData.listShellFaceIDs.append(add_face(Class_face((OppoVerts[0], vid1, OppoVerts[1]), ClassFace.FLIP, ModelData.dictFaces[IncidentFaces[0]].get_id(),
                        ModelData.dictFaces[IncidentFaces[0]].get_type())))
    ModelData.listShellFaceIDs.append(add_face(Class_face((OppoVerts[1], vid2, OppoVerts[0]), ClassFace.FLIP, ModelData.dictFaces[IncidentFaces[1]].get_id(),
                        ModelData.dictFaces[IncidentFaces[1]].get_type())))
    #remove
    pre_remove_face_by_faceids(IncidentFaces)
    return True

#restore normals of all the triangles, take the FIX boundary triangle as the seed should be used before outputing of surface
def restore_normals():
    #extract the seed triangle
    restoredFids = []
    for fkey in ModelData.listShellFaceIDs:
        if ModelData.dictFaces[fkey].get_tag() == ClassFace.FIX:
            #if len(ModelData.dictTetrahedrons) > 0:
            #    if len(find_tetids_by_faceid(fkey)) == 1:
            #        restoredFids.append(fkey)
            #        break
            #else:
            restoredFids.append(fkey)
            break

    #recursivly propagate the ModelData.dictVertices order
    if len(restoredFids) == 0:
        raise ValueError

    fid = restoredFids[0]
    restore_normal(fid, [ModelData.dictFaces[fid].get_vids()[0], ModelData.dictFaces[fid].get_vids()[1]], restoredFids)
    restore_normal(fid, [ModelData.dictFaces[fid].get_vids()[1], ModelData.dictFaces[fid].get_vids()[2]], restoredFids)
    restore_normal(fid, [ModelData.dictFaces[fid].get_vids()[2], ModelData.dictFaces[fid].get_vids()[0]], restoredFids)
                                    
#recursivly restoring the normal of the face
#fid is the id of the seed face, edge is the adjacent edge, restoredFids are fids that have been restored
def restore_normal(fid, edge, restoredFids):
    for fkey in ModelData.dictFaces:
        if fkey != fid and edge[0] in ModelData.dictFaces[fkey].get_vids() and edge[1] in ModelData.dictFaces[fkey].get_vids():
            if fkey not in restoredFids:
                #found the neighbor
                if edge in [[ModelData.dictFaces[fkey].get_vids()[0], ModelData.dictFaces[fkey].get_vids()[1]], [ModelData.dictFaces[fkey].get_vids()[1], ModelData.dictFaces[fkey].get_vids()[2]], [ModelData.dictFaces[fkey].get_vids()[2], ModelData.dictFaces[fkey].get_vids()[0]]]:
                    #need restore=m
                    invert_orientation(fkey)
                restoredFids.append(fkey)
                if edge != [ModelData.dictFaces[fkey].get_vids()[1], ModelData.dictFaces[fkey].get_vids()[0]]:
                    restore_normal(fkey, [ModelData.dictFaces[fkey].get_vids()[0], ModelData.dictFaces[fkey].get_vids()[1]], restoredFids)
                if edge != [ModelData.dictFaces[fkey].get_vids()[2], ModelData.dictFaces[fkey].get_vids()[1]]:
                    restore_normal(fkey, [ModelData.dictFaces[fkey].get_vids()[1], ModelData.dictFaces[fkey].get_vids()[2]], restoredFids)
                if edge != [ModelData.dictFaces[fkey].get_vids()[0], ModelData.dictFaces[fkey].get_vids()[2]]:
                    restore_normal(fkey, [ModelData.dictFaces[fkey].get_vids()[2], ModelData.dictFaces[fkey].get_vids()[0]], restoredFids)
            #    break
            #else:
            #    break

#Invert the orientation of a face
def invert_orientation(fid):
    verts = []
    for i in range (0, 3):
        verts.append(ModelData.dictFaces[fid].get_vids()[2-i])
    ModelData.dictFaces[fid].set_vids(verts)

#merge all the collinear ModelData.dictVertices of a face keep the ModelData.dictVertices with more than two neighbors
#INPUT: vertexList is the list of vertex ids of a face
#RETURN: a new vertexList
def CollinearVerticesMerge(f):
    pass
#Join two neighbor ModelData.dictFaces into a larger polygon
#INPUT: fid1 and fid2 are two face ids, bOrient == True mean two ModelData.dictFaces share the same orientation
#RETURN: True means succeed
def join_faces(fid1, fid2, bOrient):
    pass
    #if ModelData.dictFaces[fid1].get_tag() != ModelData.dictFaces[fid2].get_tag():
    #    return False

    #if bOrient:
    #    for v in ModelData.dictFaces[fid1].get_vids():
    #        pass
    #else:
    #    pass

#merge all the coplaner ModelData.dictFaces and also consider the semantics, id, type.
#should be used right after decomposition
def coplaner_face_merge():
    pass
    ##Join coplaner ModelData.dictFaces


    ##Merge collinear vertics
    #for f in ModelData.dictFaces:
    #    if len(f.get_vids()) > 3:
    #        f.get_vids() = CollinearVerticeMerge(f.get_vids())
    ##Retriangulate the polygon
    #for f in ModelData.dictFaces:
    #    if len(f.get_vids()) > 3:
    #        #polygon trianglulation
    #        pass
    #        #add all the new generated ModelData.dictFaces
    #        pass
    #        #eliminate the polygon
    #        f.get_tag() = ClassFace.DEL
    ##reorder all the ModelData.dictVertices and ModelData.dictFaces
    #reorder_datastructure()

    
#Compare the coordinates of a vertex with a group of vetices
#INPUT: Vt1 is a vertex (x, y, z), Vts is a list of verices
#OUTPUT: 
#RETURN: True means the same dictVertices False means different dictVertices
def is_have_same_vert(Vt, Vts):
    for v in Vts:
        if abs(Vt[0] - v[0]) < SimpleMath.Tol * 100 and abs(Vt[1] - v[1]) < SimpleMath.Tol * 100 and abs(Vt[2] - v[2]) < SimpleMath.Tol * 100:#enlarge the Tol to remove duplicated vertics 20170902
            return True
    return False

#generate uuid
def generate_uuid():
    ModelData.UUID += 1
    return 'UUID_TEST_ID_TO_BE_DONE_' + str(ModelData.UUID)

#find the overlapping face object based on the distance of the midpoint of tris
#INPUT: tris is a three tuple of vertex id
#OUTPUT: 
#RETURN: the faceId of the overlapping face
def find_face_by_mapping(tris):
    #the mid point
    centerPoint = SimpleMath.tuple_numproduct(1.0/3.0, SimpleMath.tuple_plus(ModelData.dictVertices[tris[0]], SimpleMath.tuple_plus(ModelData.dictVertices[tris[1]],ModelData.dictVertices[tris[2]]))) 
    #mapping by distance
    for fKey in ModelData.dictFaces:
        fVertices = ModelData.dictFaces[fKey].get_vids()
        if SimpleMath.is_point_in_triangle_3(centerPoint, (ModelData.dictVertices[fVertices[0]], ModelData.dictVertices[fVertices[1]], ModelData.dictVertices[fVertices[2]])):
            return fKey

#calculate the bounding box of a list of faces
#INPUT: fList, is a list of face ids
#RETURN: a two tuple of max point and min point
def get_bbox_faces(fList):
    vertList = []
    for f in fList:
        vertList += ModelData.dictFaces[f].get_vids()
    return get_bbox_vertices(vertList)

#calculate the bounding box of a list of vertices
#INPUT: vList, is a list of vertex ids
#RETURN: a two tuple of max point and min points
def get_bbox_vertices(vList):
    ptList = []
    for v in vList:
        ptList.append(ModelData.dictVertices[v])
    return SimpleMath.get_bbox_of_points(ptList)

#invert the normal of the model
def invert_poly_normal():
    for f in ModelData.dictFaces:
        invert_face_normal(f)
    print ('Model faces flipped!')
#invert the normal of the face
def invert_face_normal(fid):
    vids = ModelData.dictFaces[fid].get_vids()
    vids = [vids[0], vids[2], vids[1]]
    ModelData.dictFaces[fid].set_vids(vids)

#calculate gaussian curvatures for faces
def cal_curvature_faces(fids):
    #extract geometry
    v_list = []#double coords 3*num of v
    v_oid_list = []#corresponding vid in the global vertex list
    f_list = []#int vids 3*num of f
    
    for f in fids:
        vids = ModelData.dictFaces[f].get_vids()
        for vid in vids:
            if vid not in v_oid_list:
                v_oid_list.append(vid)
                v_list.append(ModelData.dictVertices[vid][0])
                v_list.append(ModelData.dictVertices[vid][1])
                v_list.append(ModelData.dictVertices[vid][2])
                f_list.append(len(v_list) / 3 - 1)
            else:
                f_list.append(v_oid_list.index(vid))
                
    #calculate curvature
    curDirBefore = os.getcwd() 
    path = os.path.dirname(os.path.realpath(__file__))
    if sizeof(c_voidp) == 4:
        #win32
        path = os.path.join(path, '..\\iglDLL\\Release')
        os.chdir(path)
        if not os.path.exists("iglDLL.dll"):
            print("DLL missing: " + path + "iglDLL.dll")
        gaussianCurvature = CDLL("iglDLL.dll")

    elif sizeof(c_voidp) == 8:
        #x64
        path = os.path.join(path, '..\\iglDLL\\x64\\Release')
        os.chdir(path)
        if not os.path.exists("iglDLL.dll"):
            print("DLL missing: " + path + "iglDLL.dll")
        gaussianCurvature = CDLL("iglDLL.dll")
    os.chdir(curDirBefore)

    cVertices = (c_double * len(v_list))()
    for i in range(0, len(v_list)):
        cVertices[i] = c_double(v_list[i])

    cFaces = (c_int * len(f_list))()
    for i in range(0, len(f_list)):
        cFaces[i] = c_int(f_list[i])
    
    outputCurvatures = (c_float * (len(v_list) / 3))()

    try:
        gaussianCurvature.simpleMeanCurvature(byref(cVertices), c_int(len(v_list)/3), byref(cFaces), c_int(len(f_list)/3),
                                    pointer(outputCurvatures),c_bool(0), c_bool(0))
        #gaussianCurvature.simpleGaussianCurvature(byref(cVertices), c_int(len(v_list)/3), byref(cFaces), c_int(len(f_list)/3),
        #                            pointer(outputCurvatures),c_bool(1), c_bool(0))
    except:
        print("curvature cal error")
        return []

    f_curvatures = []
    for i in range(len(fids)):
        f_curvatures.append(abs((outputCurvatures[f_list[i*3]] + outputCurvatures[f_list[i*3 + 1]] + outputCurvatures[f_list[i*3 + 2]]))/3)    
        #f_curvatures.append(max(outputCurvatures[f_list[i*3]], outputCurvatures[f_list[i*3 + 1]], outputCurvatures[f_list[i*3 + 2]]))    
    
    return f_curvatures


#Recursively search the coplaner dictFaces of a given face by checking the coplanarity
#Note the normals should be consistent, otherwise coplanerity can be errorneous 20170817
#INPUT: fid is the id of the current face, fNormal is the normal of the current face, tag is a list of visited dictFaces, 
#RETURN
def coplaner_neighbors_byNormal(fid, fNormal, tag):
    vertexIds = ModelData.dictFaces[fid].get_vids()
    for i in range(0, 3):
        j = 0
        if i < 2:
            j = i + 1
        face = CarveFunc.get_neighbor_shellface([vertexIds[i], vertexIds[j]], fid)
        if face not in tag and face is not None:
            newVertids = ModelData.dictFaces[face].get_vids()
            Normal = SimpleMath.get_face_normal([ModelData.dictVertices[newVertids[0]], ModelData.dictVertices[newVertids[1]], ModelData.dictVertices[newVertids[2]]])
            if SimpleMath.vector_length_3(Normal) > SimpleMath.Tol and SimpleMath.dot_product_3(fNormal, Normal) > SimpleMath.NeighborAngle:
                tag.append(face)
                #only select the adjacent neighbors ????20170817
                #coplaner_neighbors_byNormal(face, Normal, tag)

#check the coplanarity of two faces by point distance (or normal) 201708
# a bug was found and fixed 20170904 when two adjacent folded triangles oriented the same
#INPUT: fid1 and fid2 are face ids
#RETURN true means coplanar, false means not coplanar
def is_coplanar_byDist(fid1, fid2):
    
    #plane by normal and a point
    normal = ModelData.dictFaces[fid1].get_normal()
    if SimpleMath.vector_length_3Ex(normal) == 0:
        return False
    fNormal = ModelData.dictFaces[fid2].get_normal()

    #test the orientataion
    vertex1 = ModelData.dictFaces[fid1].get_vids()
    vertex2 = ModelData.dictFaces[fid2].get_vids()
    
    edge1 = [[vertex1[0], vertex1[1]],[vertex1[1], vertex1[2]],[vertex1[2], vertex1[0]]]
    edge2 = [[vertex2[0], vertex2[1]],[vertex2[1], vertex2[2]],[vertex2[2], vertex2[0]]]
    for e in edge1:
        if e in edge2:
            #need re-orient
            fNormal = SimpleMath.tuple_numproduct(-1, fNormal)
            break

    #modified 20170904
    if SimpleMath.dot_product_3(fNormal, normal) > SimpleMath.NeighborAngle:
        return True
    else:
        return False

    #not needed
    vertex = ModelData.dictFaces[fid1].get_vids()[0]
    count = 0
    for v in ModelData.dictFaces[fid2].get_vids():
        w = SimpleMath.tuple_minus(ModelData.dictVertices[vertex], ModelData.dictVertices[v])
        #projected onto normal
        d = SimpleMath.dot_product_3(normal, w)
        if abs(d) < SimpleMath.DegTol * 50:#Note abs
            count += 1
    if count == 3:
        return True
    else:
        return False

#Recursively search the coplaner dictFaces of a given face by checking the coplanarity20170817
#INPUT: fid is the id of the current face, fNormal is the normal of the current face, tag is a list of visited dictFaces, 
#RETURN
def coplaner_neighbors_byDist(fid, tag):
    vertexIds = ModelData.dictFaces[fid].get_vids()
    for i in range(0, 3):
        j = 0
        if i < 2:
            j = i + 1
        face = CarveFunc.get_neighbor_shellface([vertexIds[i], vertexIds[j]], fid)
        if face not in tag and face is not None:
            newVertids = ModelData.dictFaces[face].get_vids()
            if is_coplanar_byDist(face, fid):
                tag.append(face)
                coplaner_neighbors_byDist(face, tag)
                
                

#############used only for experiment
def preserveModelData():
    #####copy datacopy
    ModelData.ownFaces = copy.deepcopy(ModelData.dictFaces)
    ModelData.ownVerts =  copy.deepcopy(ModelData.dictVertices)
    ModelData.ownTerahedron =  copy.deepcopy(ModelData.dictTetrahedrons)
    ModelData.ownlistShellFaceIDs =  copy.deepcopy(ModelData.listShellFaceIDs)
    ModelData.ownlistPrincipleNormal =  copy.deepcopy(ModelData.listPrincipleNormal)
    ModelData.ownfaceID = copy.deepcopy( ModelData.faceID)
    ModelData.ownvertexID =  copy.deepcopy(ModelData.vertexID)


def restoreModelData():
    #####restore dataset
    ModelData.dictFaces = copy.deepcopy(ModelData.ownFaces)
    ModelData.dictVertices =  copy.deepcopy(ModelData.ownVerts)
    ModelData.dictTetrahedrons = copy.deepcopy(ModelData.ownTerahedron)
    ModelData.listShellFaceIDs = copy.deepcopy(ModelData.ownlistShellFaceIDs)
    ModelData.listPrincipleNormal = copy.deepcopy(ModelData.ownlistPrincipleNormal)
    ModelData.faceID = copy.deepcopy(ModelData.ownfaceID)
    ModelData.vertexID = copy.deepcopy(ModelData.ownvertexID)