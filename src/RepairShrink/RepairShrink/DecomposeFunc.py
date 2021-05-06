import os
from ctypes import *
import ModelDataFuncs
import ModelData
import ClassFace
from ClassFace import Class_face
from SimpleMath import *
from math import sqrt
import operator

#deprecated
#Decompose the intersected segments between segments1 and segments2, the two lists should not contain any intersection
#INPUT: segments1 and segments2 are lists of vertex id pair which indicates a segment: ([a, b], [c, d], [e, f])
#RETURN: return the segments free of intersection
def decompose_segment(segments1, segments2):
    #record the segments that should be removed
    segmentsDellist1 = []
    segmentsDellist2 = []

    for seg1 in segments1:
        for seg2 in segments2:
            if seg1 in segmentsDellist1:
                break
            #if segments.index(seg1) >= segments.index(seg2) or seg2 in segmentsDellist:
            if seg2 in segmentsDellist2:
                continue
            vt1 = seg1[0]
            vt2 = seg1[1]
            pt1 = seg2[0]
            pt2 = seg2[1]

            #duplicated
            if vt1 in seg2 and vt2 in seg2:
                continue
            #
            if vt1 == vt2:
                print("impossible 123 or degenerated triangle")
                raise Exception
                if pt1 == pt2:
                    #vertex-vertex
                    if ModelDataFuncs.is_have_same_vert(ModelData.dictVertices[vt1], [ModelData.dictVertices[pt1]]):
                        segmentsDellist1.append(seg1)
                        print("impossible567")
                        raise Exception
                else:
                    #vertex-line
                    if is_point_in_linesegment(ModelData.dictVertices[vt1], ModelData.dictVertices[pt1], ModelData.dictVertices[pt2]):
                        segmentsDellist1.append(seg1)
                        #intersection but not overlapping
                        if not ModelDataFuncs.is_have_same_vert(ModelData.dictVertices[vt1], [ModelData.dictVertices[pt1], ModelData.dictVertices[pt2]]):
                            segmentsDellist2.append(seg2)
                            if [pt1, vt1] not in segments2 and [vt1, pt1] not in segments2:
                                segments2.append([pt1, vt1])
                            if [vt1, pt2] not in segments2 and [pt2, vt1] not in segments2:
                                segments2.append([vt1, pt2])
            else:
                if pt1 == pt2:
                    #line-vertex
                    if is_point_in_linesegment(ModelData.dictVertices[pt1], ModelData.dictVertices[vt1], ModelData.dictVertices[vt2]):
                        segmentsDellist2.append(seg2)
                        #intersection but not overlapping
                        if not ModelDataFuncs.is_have_same_vert(ModelData.dictVertices[pt1], [ModelData.dictVertices[vt1], ModelData.dictVertices[vt2]]):
                            segmentsDellist1.append(seg1)
                            if [vt1, pt1] not in segments1 and [pt1, vt1] not in segments1:
                                segments1.append([vt1, pt1])
                            if [pt1, vt2] not in segments1 and [vt2, pt1] not in segments1:
                                segments1.append([pt1, vt2])
                        else:
                            #vertex is presented in the line
                            continue
                else:
                    #line-line
                    NewVert, bResult = lineseg_intersect_lineseg(ModelData.dictVertices[vt1], ModelData.dictVertices[vt2], ModelData.dictVertices[pt1], ModelData.dictVertices[pt2])
                    if bResult:
                        if len(NewVert) > 0 :
                            #print(NewVert)
                            #this bug was found on 20151214
                            if ModelDataFuncs.is_have_same_vert(NewVert,[ModelData.dictVertices[vt1], ModelData.dictVertices[vt2]]) or ModelDataFuncs.is_have_same_vert(NewVert,[ModelData.dictVertices[pt1], ModelData.dictVertices[pt2]]):
                                    #intersect at the end point
                                    continue
                            prevID = ModelData.vertexID
                            newVertID = ModelDataFuncs.add_vertex(NewVert)
                            if newVertID == prevID:
                                #new vertex
                                segmentsDellist1.append(seg1)
                                segmentsDellist2.append(seg2)
                                if [vt1, newVertID] not in segments1 and [newVertID, vt1] not in segments1:
                                    segments1.append([vt1, newVertID])
                                if [newVertID, vt2] not in segments1 and [vt2, newVertID] not in segments1:
                                    segments1.append([newVertID, vt2])
                                if [pt1, newVertID] not in segments2 and [newVertID, pt1] not in segments2:
                                    segments2.append([pt1, newVertID])
                                if [newVertID, pt2] not in segments2 and [pt2, newVertID] not in segments2:
                                    segments2.append([newVertID, pt2])
                            else:
                                #existing vertex
                                if newVertID not in seg1:
                                    segmentsDellist1.append(seg1)
                                    if [vt1, newVertID] not in segments1 and [newVertID, vt1] not in segments1:
                                        segments1.append([vt1, newVertID])
                                    if [newVertID, vt2] not in segments1 and [vt2, newVertID] not in segments1:
                                        segments1.append([newVertID, vt2])
                                if newVertID not in seg2:
                                    segmentsDellist2.append(seg2)
                                    if [pt1, newVertID] not in segments2 and [newVertID, pt1] not in segments2:
                                        segments2.append([pt1, newVertID])
                                    if [newVertID, pt2] not in segments2 and [pt2, newVertID] not in segments2:
                                        segments2.append([newVertID, pt2])
                        
                        elif len(NewVert) == 0:
                            #overlapping segments
                            #sort collinear verts
                            dictSort = [vt1, vt2, pt1, pt2]
                            # for item in dictSort:
                                # if item != vt1:
                            if abs(ModelData.dictVertices[vt2][0] - ModelData.dictVertices[vt1][0]) > Tol:
                                dictSort = sorted(dictSort, key = lambda vert:ModelData.dictVertices[vert][0])
                            elif abs(ModelData.dictVertices[vt2][1] - ModelData.dictVertices[vt1][1]) > Tol:
                                dictSort = sorted(dictSort, key = lambda vert:ModelData.dictVertices[vert][1])
                            elif abs(ModelData.dictVertices[vt2][2] - ModelData.dictVertices[vt1][2]) > Tol:
                                dictSort = sorted(dictSort, key = lambda vert:ModelData.dictVertices[vert][2])
                                    # break
                            
                            if (dictSort[0], dictSort[1]) not in [(vt1, vt2), (vt2, vt1), (pt1, pt2), (pt2, pt1)] and dictSort[0] != dictSort[1]:
                                segments1.append([dictSort[0], dictSort[1]])
                            if (dictSort[1], dictSort[2]) not in [(vt1, vt2), (vt2, vt1), (pt1, pt2), (pt2, pt1)] and dictSort[1] != dictSort[2]:
                                segments1.append([dictSort[1], dictSort[2]])
                            if (dictSort[2], dictSort[3]) not in [(vt1, vt2), (vt2, vt1), (pt1, pt2), (pt2, pt1)] and dictSort[2] != dictSort[3]:
                                segments1.append([dictSort[2], dictSort[3]])

                            if seg1 not in [[dictSort[0], dictSort[1]], [dictSort[1], dictSort[2]],[dictSort[2], dictSort[3]]] and\
                                seg1 not in [[dictSort[1], dictSort[0]], [dictSort[2], dictSort[1]],[dictSort[3], dictSort[2]]]:
                                segmentsDellist1.append(seg1)
                            if seg2 not in [[dictSort[0], dictSort[1]], [dictSort[1], dictSort[2]],[dictSort[2], dictSort[3]]] and\
                                seg2 not in [[dictSort[1], dictSort[0]], [dictSort[2], dictSort[1]],[dictSort[3], dictSort[2]]]:
                                segmentsDellist2.append(seg2)
                          
    #remove degenerated segments
    newSegment = []
    for seg in segments1:
        if seg not in segmentsDellist1 and \
            seg not in newSegment and [seg[1], seg[0]] not in newSegment and seg[0] != seg[1]:
            newSegment.append(seg)   
    for seg in segments2:
        if seg not in segmentsDellist2 and \
            seg not in newSegment and [seg[1], seg[0]] not in newSegment and seg[0] != seg[1]:
            newSegment.append(seg)  			
    return newSegment    
               
#Decompose the intersected segments
#INPUT: segments is a list of vertex id pair which indicates a segment: ([a, b], [c, d], [e, f])
#RETURN: return the segments free of intersection
def decompose_segment_ex(segments):
    #using a simple O(n*n) solution, can be improved using sweeping
    segments_result = []#record the result segments
    segmentsDellist = []#record the segment tobe deleted
    for seg1 in segments:
        if [seg1[0], seg1[1]] in segmentsDellist or [seg1[1], seg1[0]] in segmentsDellist:
            continue
        intersectedPoints = [seg1[0], seg1[1]]#all the points in seg1
        for seg2 in segments:
            #should test all the segments, do not filter them out using dellist
            vt1 = seg1[0]
            vt2 = seg1[1]
            pt1 = seg2[0]
            pt2 = seg2[1]
        
            #duplicated
            if vt1 in seg2 and vt2 in seg2:
                continue
            #test all the other segments for intersection
            if vt1 == vt2:
                #if segment1 is a point, simply check duplicated point and split intersected lines
                if pt1 == pt2:
                    #vertex-vertex
                    if ModelDataFuncs.is_have_same_vert(ModelData.dictVertices[vt1], [ModelData.dictVertices[pt1]]):
                        segmentsDellist.append(seg1)
                else:
                    #vertex-line
                    if is_point_in_linesegment(ModelData.dictVertices[vt1], ModelData.dictVertices[pt1], ModelData.dictVertices[pt2]):
                        segmentsDellist.append(seg1)
                        #intersection but not overlapping
                        if not ModelDataFuncs.is_have_same_vert(ModelData.dictVertices[vt1], [ModelData.dictVertices[pt1], ModelData.dictVertices[pt2]]):
                            segmentsDellist.append(seg2)
                            if [pt1, vt1] not in segments and [vt1, pt1] not in segments:
                                segments.append([pt1, vt1])
                            if [vt1, pt2] not in segments and [pt2, vt1] not in segments:
                                segments.append([vt1, pt2])
            else:
                #if segment 1 is a line, then intersect with all the other segments and rearrange segement 1
                if pt1 == pt2:
                    #line-vertex
                    if is_point_in_linesegment(ModelData.dictVertices[pt1], ModelData.dictVertices[vt1], ModelData.dictVertices[vt2]):
                        segmentsDellist.append(seg2)
                        #intersection but not overlapping
                        if not ModelDataFuncs.is_have_same_vert(ModelData.dictVertices[pt1], [ModelData.dictVertices[vt1], ModelData.dictVertices[vt2]]):
                            if pt1 not in intersectedPoints:
                                intersectedPoints.append(pt1)
                else:
                    #line-line
                    NewVert, bResult = lineseg_intersect_lineseg(ModelData.dictVertices[vt1], ModelData.dictVertices[vt2], ModelData.dictVertices[pt1], ModelData.dictVertices[pt2])
                    if bResult:
                        if len(NewVert) > 1 :
                            if not ModelDataFuncs.is_have_same_vert(NewVert,[ModelData.dictVertices[vt1], ModelData.dictVertices[vt2]]):
                                #intersect at the middle
                                VertID = ModelDataFuncs.add_vertex(NewVert)
                                if VertID not in intersectedPoints:
                                    intersectedPoints.append(VertID)                                
                        
                        elif len(NewVert) == 0:
                            #overlapping segments
                            if pt1 not in intersectedPoints:
                                intersectedPoints.append(pt1)
                            if pt2 not in intersectedPoints:
                                intersectedPoints.append(pt2)
        #after testing seg1 with all the other segments
        if len(intersectedPoints) > 2:
            #seg1 is intersected
            segmentsDellist.append(seg1)
            #sort all collinear verts of intersection
            dictSort = intersectedPoints
            #using the best axis to sort
            if abs(ModelData.dictVertices[vt2][0] - ModelData.dictVertices[vt1][0]) > Tol:
                dictSort = sorted(dictSort, key = lambda vert:ModelData.dictVertices[vert][0])
            elif abs(ModelData.dictVertices[vt2][1] - ModelData.dictVertices[vt1][1]) > Tol:
                dictSort = sorted(dictSort, key = lambda vert:ModelData.dictVertices[vert][1])
            elif abs(ModelData.dictVertices[vt2][2] - ModelData.dictVertices[vt1][2]) > Tol:
                dictSort = sorted(dictSort, key = lambda vert:ModelData.dictVertices[vert][2])
            
            selPoints = []
            isStart = False
            for pt in dictSort:
                if  ModelDataFuncs.is_have_same_vert(ModelData.dictVertices[pt], [ModelData.dictVertices[seg1[0]], ModelData.dictVertices[seg1[1]]]):
                    if isStart == True :
                        isStart = False
                        selPoints.append(pt)#the end point
                    else:
                        isStart = True
                if isStart == True:
                    selPoints.append(pt)
            #add segments to result
            for i in range(0, len(selPoints)-1):
                if [selPoints[i], selPoints[i+1]] not in segments_result and [selPoints[i+1], selPoints[i]] not in segments_result :
                    segments_result.append([selPoints[i], selPoints[i+1]])
        else:
            if [seg1[0], seg1[1]] not in segments_result and [seg1[1], seg1[0]]  not in segments_result:
                segments_result.append(seg1)
    #return all the segments
    return segments_result 

#tessellate two overlapping triangles
#INPUT: faceTessellate is a trianlge; vertIDlist2 is a list of vertex ids representing 
#a triangle when bType == 2, an edge when bType == 1, an vertex when bType == 0
#OUTPUT: modify the dictFaces and dictVertices lists in ModelDataFuncs directly
#RETURN: True means tessellated False means did not tessellate
def triangle_delaunay_tessellate_ex(faceTessellate, vertIDlist2, bType):
    #get the vids
    vertIDlist1 = faceTessellate.get_vids()
    #used to check the orientation
    normalOfTessFace = get_face_normal([ModelData.dictVertices[vertIDlist1[0]], ModelData.dictVertices[vertIDlist1[1]], ModelData.dictVertices[vertIDlist1[2]]])
    #get the segements based on the original vertex id
    segments = []
    #face1
    if [vertIDlist1[0], vertIDlist1[1]] not in segments and [vertIDlist1[1], vertIDlist1[0]] not in segments:
        segments.append([vertIDlist1[0], vertIDlist1[1]])
    if [vertIDlist1[1], vertIDlist1[2]] not in segments and [vertIDlist1[2], vertIDlist1[1]] not in segments:
        segments.append([vertIDlist1[1], vertIDlist1[2]])
    if [vertIDlist1[0], vertIDlist1[2]] not in segments and [vertIDlist1[2], vertIDlist1[0]] not in segments:
        segments.append([vertIDlist1[2], vertIDlist1[0]])
    
    segments_temp = []
    if bType == 2 and len(vertIDlist2) == 3:
        #vertIDs2 is a triangle (coplaner)
        if [vertIDlist2[0], vertIDlist2[1]] not in segments and [vertIDlist2[1], vertIDlist2[0]] not in segments:
            segments_temp.append([vertIDlist2[0], vertIDlist2[1]])
        if [vertIDlist2[1], vertIDlist2[2]] not in segments and [vertIDlist2[2], vertIDlist2[1]] not in segments:
            segments_temp.append([vertIDlist2[1], vertIDlist2[2]])
        if [vertIDlist2[0], vertIDlist2[2]] not in segments and [vertIDlist2[2], vertIDlist2[0]] not in segments:
            segments_temp.append([vertIDlist2[2], vertIDlist2[0]])
    elif bType == 1 and len(vertIDlist2) == 2:
        #vertIDs2 is an edge
        if [vertIDlist2[0], vertIDlist2[1]] not in segments and [vertIDlist2[1], vertIDlist2[0]] not in segments:
            segments_temp.append([vertIDlist2[0], vertIDlist2[1]])
    elif bType == 0 and len(vertIDlist2) == 1:
        #vertIDs2 is an vertex
        if [vertIDlist2[0], vertIDlist2[0]] not in segments:
            segments_temp.append([vertIDlist2[0], vertIDlist2[0]])
    else:
        print("Crashing!!!")
        raise Exception
    
    #pre decompose the segments and add new dictVertices
    segments = decompose_segment(segments, segments_temp)

    if bType == 0:
        #speedup by manually insert the triangles
        if len(segments) == 4:
            #add two new dictFaces
            foundsegs = []
            for seg in segments:
                if vertIDlist2[0] in seg:
                    foundsegs.append(seg)
            foundvt = -1
            for vt in vertIDlist1:
                if vt not in [foundsegs[0][0], foundsegs[0][1], foundsegs[1][0], foundsegs[1][1]]:
                    foundvt = vt
                    break
            if ModelData.global_DISCARD_DEG:
                if vector_length_3(get_face_normal([ModelData.dictVertices[foundvt], ModelData.dictVertices[foundsegs[0][0]], ModelData.dictVertices[foundsegs[0][1]]])) > Tol:
                    ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((foundvt, foundsegs[0][0], foundsegs[0][1]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
                else:
                    pass
                if vector_length_3(get_face_normal([ModelData.dictVertices[foundvt], ModelData.dictVertices[foundsegs[1][0]], ModelData.dictVertices[foundsegs[1][1]]])) > Tol:
                    ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((foundvt, foundsegs[1][0], foundsegs[1][1]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
                else:
                    pass
            else:
                ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((foundvt, foundsegs[0][0], foundsegs[0][1]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
                ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((foundvt, foundsegs[1][0], foundsegs[1][1]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
        elif len(segments) == 3:
            #add tree new dictFaces
            if ModelData.global_DISCARD_DEG:
                if vector_length_3(get_face_normal([ModelData.dictVertices[vertIDlist1[0]], ModelData.dictVertices[vertIDlist1[1]], ModelData.dictVertices[vertIDlist2[0]]])) > Tol:
                    ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIDlist1[0], vertIDlist1[1], vertIDlist2[0]), normalOfTessFace),ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
                else:
                    pass
                if vector_length_3(get_face_normal([ModelData.dictVertices[vertIDlist1[1]], ModelData.dictVertices[vertIDlist1[2]], ModelData.dictVertices[vertIDlist2[0]]])) > Tol:
                    ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIDlist1[1], vertIDlist1[2], vertIDlist2[0]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
                else:
                    pass
                if vector_length_3(get_face_normal([ModelData.dictVertices[vertIDlist1[2]], ModelData.dictVertices[vertIDlist1[0]], ModelData.dictVertices[vertIDlist2[0]]])) > Tol:
                    ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIDlist1[2], vertIDlist1[0], vertIDlist2[0]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
                else:
                    pass
            else:
                ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIDlist1[0], vertIDlist1[1], vertIDlist2[0]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
                ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIDlist1[1], vertIDlist1[2], vertIDlist2[0]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
                ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIDlist1[2], vertIDlist1[0], vertIDlist2[0]), normalOfTessFace), ClassFace.FIX, faceTessellate.get_id(), faceTessellate.get_type()))
        else:
            print("debugsegments")
            raise Exception
        bNewTri = True
        preserveID = []
    else:
        #collect the ids of dictVertices from segments
        vertexIds = []
        for seg in segments:
            if seg[0] not in vertexIds:
                vertexIds.append(seg[0])
            if seg[1] not in vertexIds:
                vertexIds.append(seg[1])

        vertexIdMap = {}#used for map segment ids
        iVertCount = 0
        for vid in vertexIds:
            vertexIdMap[vid] = iVertCount
            iVertCount += 1 

        #the projection plane
        vt01 = ModelData.dictVertices[vertexIds[0]]
        vt02 = ModelData.dictVertices[vertexIds[1]]
        vt03 = ModelData.dictVertices[vertexIds[2]]

        #convert to 2D (simply select an axis aligned projection plane)
        v1 = tuple_minus(vt02, vt01)
        v2 = tuple_minus(vt03, vt01)
        normal = cross_product_3(v1, v2)

        #check degeneration
        if vector_length_3(normal) < Tol:
            print("degenerate face")
            #raise Exception

        compareYZ = abs(dot_product_3(normal, (1.0, 0.0, 0.0)))
        compareXZ = abs(dot_product_3(normal, (0.0, 1.0, 0.0)))
        compareYX = abs(dot_product_3(normal, (0.0, 0.0, 1.0)))

        verts2d = []

        #the direction of the projection
        nProject = (0, 0, 0)

        if compareYZ > compareXZ and compareYZ > compareYX:
            #choose yz
            nProject = (1, 0, 0)

            for vid in vertexIds:
                verts2d.append(ModelData.dictVertices[vid][1]) 
                verts2d.append(ModelData.dictVertices[vid][2])

        elif compareXZ > compareYZ and compareXZ > compareYX:
            #choose xz
            nProject = (0, 1, 0)

            for vid in vertexIds:
                verts2d.append(ModelData.dictVertices[vid][0]) 
                verts2d.append(ModelData.dictVertices[vid][2])

        else:
            #choose xy
            nProject = (0, 0, 1)

            for vid in vertexIds:
                verts2d.append(ModelData.dictVertices[vid][0]) 
                verts2d.append(ModelData.dictVertices[vid][1])

        #triangulation
        curDirBefore = os.getcwd() 
        path = os.path.dirname(os.path.realpath(__file__))
        if sizeof(c_voidp) == 4:
            #win32
            path = os.path.join(path, '..\\triangledll\\Release')
            os.chdir(path)
            if not os.path.exists("triangledll.dll"):
                print("DLL missing: " + path + "triangledll.dll")
            Triangulator = CDLL("triangledll.dll")

        elif sizeof(c_voidp) == 8:
            #x64
            path = os.path.join(path, '..\\triangledll\\x64\\Release')
            os.chdir(path)
            if not os.path.exists("triangledll.dll"):
                print("DLL missing: " + path + "triangledll.dll")
            Triangulator = CDLL("triangledll.dll")
        os.chdir(curDirBefore)
        cVertices = (c_double * (len(vertexIds)*2))()
        for i in range(0, len(vertexIds) * 2):
            cVertices[i] = c_double(verts2d[i])

        c_segments = (c_int * (len(segments)*2))()
        isegcount = 0
        for seg in segments:
            c_segments[isegcount] = c_int(vertexIdMap[seg[0]])
            c_segments[isegcount + 1] = c_int(vertexIdMap[seg[1]])
            isegcount += 2
   
        #detect the intersection of segments and modifiy the 

        #triangulation
        numberOfOutputVerts = c_int(0)
        numberOfOutputTriangles = c_int(0)
    
        try:
            Triangulator.simpleTriangulate(byref(cVertices), c_int(len(vertexIds)), byref(c_segments), c_int(len(segments)),
                                      byref(numberOfOutputVerts), byref(numberOfOutputTriangles))
        except:
            return

        outputVerts = (c_double * (numberOfOutputVerts.value * 2))()
        outputTriangles = (c_int * (numberOfOutputTriangles.value * 3))()

        Triangulator.getResults(pointer(outputVerts), pointer(outputTriangles))

        #if there is new generated dictVertices do interpolation (impossible after pre-segmentation)
        if numberOfOutputVerts.value > len(vertexIds):
            print("Triangle found more vertices!")
            #raise Exception
            #add new dictVertices (the first 6 dictVertices are the input dictVertices)
            for i in range(len(vertexIds), numberOfOutputVerts.value):
                ptNew2d = []
                if nProject == (1, 0, 0):
                    ptNew2d.append(0.0)
                    ptNew2d.append(outputVerts[i*2])
                    ptNew2d.append(outputVerts[i*2 + 1])
                elif nProject == (0, 1, 0):
                    ptNew2d.append(outputVerts[i*2])
                    ptNew2d.append(0.0)
                    ptNew2d.append(outputVerts[i*2 + 1])
                elif nProject == (0, 0, 1):
                    ptNew2d.append(outputVerts[i*2])
                    ptNew2d.append(outputVerts[i*2 + 1])
                    ptNew2d.append(0.0)

                ptEnd = tuple_plus(ptNew2d,nProject) 
                ptOut = [0]
                if RLineWithPlane(ptNew2d, ptEnd, vt01, vt02, vt03, ptOut):
                    #add mapping for the new dictVertices
                    newVertID = ModelDataFuncs.add_vertex(ptOut[0])
                    if vertexIdMap.has_key(newVertID):
                        #revise outputTriangles accordingly
                        for i_tri in range (0, numberOfOutputTriangles.value * 3, 3):
                            if outputTriangles[i_tri] == i:
                                outputTriangles[i_tri] = vertexIdMap[newVertID]
                            if outputTriangles[i_tri+1] == i:
                                outputTriangles[i_tri+1] = vertexIdMap[newVertID]
                            if outputTriangles[i_tri+2] == i:
                                outputTriangles[i_tri+2] = vertexIdMap[newVertID]
                    else:
                        vertexIdMap[newVertID] = iVertCount
                    iVertCount += 1
                else:
                    print("Unexpected error!")
                    raise Exception

        #creat a mirror of vertexIdMap
        vertIdMapInvert = {}
        for key in vertexIdMap:
            vertIdMapInvert[vertexIdMap[key]] = key

        #whether a new triangle is added
        bNewTri = False
        preserveID = []
        if numberOfOutputTriangles.value > 0:
            #add new triangles
            iCount = 0
            for i in range(0, numberOfOutputTriangles.value * 3, 3):
                #check for degeneration
                #get the coordinates of dictVertices
                vt1 = ModelData.dictVertices[vertIdMapInvert[outputTriangles[i]]]
                vt2 = ModelData.dictVertices[vertIdMapInvert[outputTriangles[i+1]]]
                vt3 = ModelData.dictVertices[vertIdMapInvert[outputTriangles[i+2]]]
            
                v1 = tuple_minus(vt2, vt1)
                v2 = tuple_minus(vt3, vt1)
                normal = cross_product_3(v1, v2)

                if ModelData.global_DISCARD_DEG:
                    #check degeneration and discard the degenerated face
                    if vector_length_3(normal) > Tol:
                        prevfID = ModelData.faceID
                        newfID = ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIdMapInvert[outputTriangles[i]], vertIdMapInvert[outputTriangles[i+1]],
                                                                vertIdMapInvert[outputTriangles[i+2]]), normalOfTessFace), ClassFace.FIX))
                        if prevfID != newfID and newfID != -1:
                            preserveID.append(newfID)
                        iCount += 1
                    else:
                        iCount += 1
                else:
                    #degeneracy is introduced which is necessary
                    prevfID = ModelData.faceID
                    newfID = ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIdMapInvert[outputTriangles[i]], vertIdMapInvert[outputTriangles[i+1]],
                                                            vertIdMapInvert[outputTriangles[i+2]]), normalOfTessFace), ClassFace.FIX))
                    if prevfID != newfID and newfID != -1:
                        preserveID.append(newfID)
                    iCount += 1

            if iCount != 0:
                bNewTri = True
            else:
                bNewTri = False
        else:
            print("Zero triangle out of triangle")
    return bNewTri, preserveID

#deprecated function
#Calculate whether two tiangles tri1 and tri2 intersect with each other
#if intersect, both triangles will be decomposed and the new triangles and dictVertices will be generated
#@article{Moller97,
#  author = "Tomas M?ller",
#  title = "A Fast Triangle-Triangle Intersection Test",
#  journal = "journal of graphics, gpu, and game tools",
#  volume = "2",
#  number = "2",    
#  pages = "25-30",
#  year = "1997",
#}
#INPUT: fid is the key for the triangle in ModelData.dictFaces 
#OUTPUT: 
#RETURN: True means intersect, False means disjoin
def is_triangle_intersect(fid1, fid2):
    #if ModelData.dictFaces[fid2].get_vids()[0] in [22, 27, 14] and ModelData.dictFaces[fid2].get_vids()[1] in [22, 27, 14] and\
    #   ModelData.dictFaces[fid2].get_vids()[2] in [22, 27, 14] and\
    #   ModelData.dictFaces[fid1].get_vids()[0] in [22, 27, 26] and ModelData.dictFaces[fid1].get_vids()[1] in [22, 27, 26] and\
    #   ModelData.dictFaces[fid1].get_vids()[2] in [22, 27, 26]:
    #    intes = 999
    #if fid1 == 596 and fid2 == 683:
    #    intew = 98989
    #print("intersect check:", fid1, fid2)
    #pre check by the boundingbox
    bboxf1 = get_bbox_of_points([ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[0]], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[1]], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[2]]])
    bboxf2 = get_bbox_of_points([ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[0]], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[1]], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[2]]])
    if bboxf1[0][0] > bboxf2[1][0] or bboxf1[0][1] > bboxf2[1][1] or bboxf1[0][2] > bboxf2[1][2] or\
       bboxf2[0][0] > bboxf1[1][0] or bboxf2[0][1] > bboxf1[1][1] or bboxf2[0][2] > bboxf1[1][2]:
         return False

    #Input dictVertices
    vert0 = ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[0]]
    vert1 = ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[1]]
    vert2 = ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[2]]
    vert3 = ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[0]]
    vert4 = ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[1]]
    vert5 = ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[2]]
    v00 = list_to_c_double_array(vert0)
    v01 = list_to_c_double_array(vert1)
    v02 = list_to_c_double_array(vert2)
    v10 = list_to_c_double_array(vert3)
    v11 = list_to_c_double_array(vert4)
    v12 = list_to_c_double_array(vert5)

    #Intersection result
    curDirBefore = os.getcwd() 
    path = os.path.dirname(os.path.realpath(__file__))
    if sizeof(c_voidp) == 4:
        #win32
        path = os.path.join(path, '..\\TriangleIntersection\\Release')
        os.chdir(path)
        if not os.path.exists("TriangleIntersection.dll"):
            print("DLL missing: " + path + "TriangleIntersection.dll")
        Intersector = CDLL("TriangleIntersection.dll")
    elif sizeof(c_voidp) == 8:
        #x64
        path = os.path.join(path, '..\\TriangleIntersection\\x64\\Release')
        os.chdir(path)
        if not os.path.exists("TriangleIntersection.dll"):
            print("DLL missing: " + path + "TriangleIntersection.dll")
        Intersector = CDLL("TriangleIntersection.dll")
    os.chdir(curDirBefore)
    #coplanar returns whether the tris are coplanar
    #intersectPoint1, intersectPoint2 are the endpoints of the line of intersection
    intersectPoint1 = (c_double * 3)()
    intersectPoint2 = (c_double* 3)()
    isCoplaner = c_int(-1)
    returnValue = Intersector.tri_tri_intersect_with_isectline(byref(v00), byref(v01), byref(v02), byref(v10), byref(v11), byref(v12),
                                                                byref(isCoplaner), byref(intersectPoint1), byref(intersectPoint2))
    if 1 == returnValue:
        #intersecting
        #
        #if ModelData.dictFaces[fid1].get_vids()[0] in [153, 130, 11] and ModelData.dictFaces[fid1].get_vids()[1] in [153, 130, 11] and ModelData.dictFaces[fid1].get_vids()[2] in [153, 130, 11]:
        #    stop=888
        #
        if isCoplaner.value == 1:
            #pre process the coplaner dictFaces
            duplicateVts = []
            for vt in ModelData.dictFaces[fid1].get_vids():
                if vt in ModelData.dictFaces[fid2].get_vids():
                    duplicateVts.append(vt) 

            if len(duplicateVts) == 3:
                #remove one of the triangles
                ModelDataFuncs.pre_remove_face_by_faceids([fid2])
                return True
            elif len(duplicateVts) == 2:
                #may be adjacent via edge
                for vid1 in ModelData.dictFaces[fid1].get_vids():
                    if vid1 in duplicateVts:
                        continue
                    for vid2 in ModelData.dictFaces[fid2].get_vids():
                        if vid2 in duplicateVts:
                            continue
                        bNorm1 = get_face_normal([ModelData.dictVertices[vid1], ModelData.dictVertices[duplicateVts[0]], ModelData.dictVertices[duplicateVts[1]]])
                        bNorm2 = get_face_normal([ModelData.dictVertices[vid2], ModelData.dictVertices[duplicateVts[0]], ModelData.dictVertices[duplicateVts[1]]])
                        if ModelDataFuncs.is_have_same_vert(bNorm1, [tuple_numproduct(-1, bNorm2)]) or vector_length_3(bNorm1) < Tol or vector_length_3(bNorm2) < Tol :
                            #connected triangles
                            return False
            else:
                #may be adjacent via vertex
                bIntersect = False
                for vid1 in ModelData.dictFaces[fid1].get_vids():
                    if vid1 in duplicateVts:
                        continue
                    #if any of the dictVertices are in the other triangle or
                    #if any of the dictVertices are on the edge of the other triangle
                    if is_point_in_triangle_3(\
                        ModelData.dictVertices[vid1], \
                        [ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[0]],ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[1]],ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[2]]]\
                        ) or is_point_in_linesegment(\
                        ModelData.dictVertices[vid1], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[0]], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[1]]\
                        ) or is_point_in_linesegment(\
                        ModelData.dictVertices[vid1], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[1]], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[2]]\
                        ) or is_point_in_linesegment(\
                        ModelData.dictVertices[vid1], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[2]], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[0]]\
                        ):
                        bIntersect = True
                        break
                if not bIntersect:
                    for vid2 in ModelData.dictFaces[fid2].get_vids():
                        if vid2 in duplicateVts:
                            continue
                        #if any of the dictVertices are in the other triangle or
                        #if any of the dictVertices are on the edge of the other triangle
                        if is_point_in_triangle_3(\
                            ModelData.dictVertices[vid2], \
                            [ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[0]],ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[1]],ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[2]]]\
                            ) or is_point_in_linesegment(\
                            ModelData.dictVertices[vid2], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[0]], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[1]]\
                            ) or is_point_in_linesegment(\
                            ModelData.dictVertices[vid2], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[1]], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[2]]\
                            ) or is_point_in_linesegment(\
                            ModelData.dictVertices[vid2], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[2]], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[0]]\
                            ):
                            bIntersect = True
                            break
                if not bIntersect:
                    return False

            #coplanar retriangulate
            bDec, preserveIDs = triangle_delaunay_tessellate_ex(ModelData.dictFaces[fid1], ModelData.dictFaces[fid2].get_vids(), 2)
            if bDec:
                if fid1 not in preserveIDs:
                    ModelDataFuncs.pre_remove_face_by_faceids([fid1])
                else:
                    pass
                if fid2 not in preserveIDs:
                    ModelDataFuncs.pre_remove_face_by_faceids([fid2])
                else:
                    pass
                return True
            return False
        else:
            #handle intersection
            #there can be intersection between vertex-vertex, vertex-edge, vertex-face, edge-edge, edge-face, face-face
            #c_float do not have a value function
            Pt1 = [intersectPoint1[0], intersectPoint1[1], intersectPoint1[2]]
            Pt2 = [intersectPoint2[0], intersectPoint2[1], intersectPoint2[2]]
            bSplit = False

            #whether intersect at an existing edge/vertex
            bEqualPt = False
            if ModelDataFuncs.is_have_same_vert(Pt1, [Pt2]):
                bEqualPt = True
            
            bVertsInF1 = False
            bVertsInF2 = False
            if ModelDataFuncs.is_have_same_vert(Pt1, [vert0, vert1, vert2]):
                if ModelDataFuncs.is_have_same_vert(Pt2, [vert0, vert1, vert2]):
                    #intersect at an exist edge/vertex of tri1
                    bVertsInF1 = True
        
            if ModelDataFuncs.is_have_same_vert(Pt1, [vert3, vert4, vert5]):
                if ModelDataFuncs.is_have_same_vert(Pt2, [vert3, vert4, vert5]):
                    #intersect at an exist edge/vertex of tri2
                    bVertsInF2 = True

            #do nothing for v ^ v = ev(2) or e ^ e = ee(2)
            if bVertsInF1 and bVertsInF2:
                return False

            if ModelData.global_DELAUNAY_TESS == False:
                #directly triangle split
                #if ModelDataFuncs.is_have_same_vert(Pt1, [Pt2]):
                #    #intersect at a vertex
                #    return False

                ##cut tri1
                #if not bVertsInF1:
                #    if DoTriSplit(fid1, Pt1, Pt2):
                #        ModelData.pre_remove_face_by_faceids([fid1])
                #        bSplit = True
                ##cut tri2
                #if not bVertsInF2:
                #    if DoTriSplit(fid2, Pt1, Pt2):
                #        ModelData.pre_remove_face_by_faceids([fid2])
                #        bSplit = True
                print("replaced by tessellation")
            else:
                #triangle tessellation
                Pt1Index = ModelDataFuncs.add_vertex(Pt1)
                if not bEqualPt:
                    Pt2Index = ModelDataFuncs.add_vertex(Pt2)
                #if not bVertsInF1 and not bVertsInF2:
                #    #ordinary intersection
                #    #add two new dictVertices
                #    Pt1Index = ModelData.add_vertex(Pt1)
                #    Pt2Index = ModelData.add_vertex(Pt2)
                #else:
                #    #intersect at an edge of one of the tris
                #    Pt1Index = -1
                #    Pt2Index = -1
                #    if bVertsInF1:
                #        if ModelDataFuncs.is_have_same_vert(Pt1, [vert0]):
                #            Pt1Index = ModelData.dictFaces[fid1].get_vids()[0]
                #        elif ModelDataFuncs.is_have_same_vert(Pt1, [vert1]):
                #            Pt1Index = ModelData.dictFaces[fid1].get_vids()[1]
                #        elif ModelDataFuncs.is_have_same_vert(Pt1, [vert2]):
                #            Pt1Index = ModelData.dictFaces[fid1].get_vids()[2]
                #        if ModelDataFuncs.is_have_same_vert(Pt2, [vert0]):
                #            Pt2Index = ModelData.dictFaces[fid1].get_vids()[0]
                #        elif ModelDataFuncs.is_have_same_vert(Pt2, [vert1]):
                #            Pt2Index = ModelData.dictFaces[fid1].get_vids()[1]
                #        elif ModelDataFuncs.is_have_same_vert(Pt2, [vert2]):
                #            Pt2Index = ModelData.dictFaces[fid1].get_vids()[2]
                #    elif bVertsInF2:
                #        if ModelDataFuncs.is_have_same_vert(Pt1, [vert3]):
                #            Pt1Index = ModelData.dictFaces[fid2].get_vids()[0]
                #        elif ModelDataFuncs.is_have_same_vert(Pt1, [vert4]):
                #            Pt1Index = ModelData.dictFaces[fid2].get_vids()[1]
                #        elif ModelDataFuncs.is_have_same_vert(Pt1, [vert5]):
                #            Pt1Index = ModelData.dictFaces[fid2].get_vids()[2]
                #        if ModelDataFuncs.is_have_same_vert(Pt2, [vert3]):
                #            Pt2Index = ModelData.dictFaces[fid2].get_vids()[0]
                #        elif ModelDataFuncs.is_have_same_vert(Pt2, [vert4]):
                #            Pt2Index = ModelData.dictFaces[fid2].get_vids()[1]
                #        elif ModelDataFuncs.is_have_same_vert(Pt2, [vert5]):
                #            Pt2Index = ModelData.dictFaces[fid2].get_vids()[2]
                #    if Pt1Index*Pt2Index < 0:
                #        print("wrong index!!")
                #        return False

                #tessellation 
                #(should handle vertex intersection)
                #if not bVertsInF1 and not bVertsInF2:
                #    print("Have to handle")

                if not bVertsInF1:
                    if bEqualPt:
                        bDec, preserveIDs = triangle_delaunay_tessellate_ex(ModelData.dictFaces[fid1], [Pt1Index],0)
                        if bDec:
                            if fid1 not in preserveIDs:
                                ModelDataFuncs.pre_remove_face_by_faceids([fid1])
                                bSplit = True
                            else:
                                pass
                    else:
                        bDec, preserveIDs = triangle_delaunay_tessellate_ex(ModelData.dictFaces[fid1], [Pt1Index, Pt2Index], 1)
                        if bDec:
                            if fid1 not in preserveIDs:
                                ModelDataFuncs.pre_remove_face_by_faceids([fid1])
                                bSplit = True
                            else:
                                pass

                if not bVertsInF2:
                    if bEqualPt:
                        bDec, preserveIDs = triangle_delaunay_tessellate_ex(ModelData.dictFaces[fid2], [Pt1Index], 0)
                        if bDec:
                            if fid2 not in preserveIDs:
                                ModelDataFuncs.pre_remove_face_by_faceids([fid2])
                                bSplit = True
                            else:
                                pass
                    else:
                        bDec, preserveIDs = triangle_delaunay_tessellate_ex(ModelData.dictFaces[fid2], [Pt1Index, Pt2Index], 1)
                        if bDec:
                            if fid2 not in preserveIDs:
                                ModelDataFuncs.pre_remove_face_by_faceids([fid2])
                                bSplit = True
                            else:
                                pass
                    
            #if at least one of the Triangle is splitted then return True
            return bSplit
    else:
        #disjoin
        return False
    
#decompose all the triangles and retriangulate them
#find the interesction -> use the intersected primitive to decompose the triangle (not CT)
#INPUT: dictFaces and dictVertices in ModelData 
#OUTPUT: dictFaces and dictVertices in ModelData
#RETURN: NONE
#def model_decomposition():
#    print("----Start decomsosing the input model----")
#    #find the interesction
#    for fid1 in ModelData.dictFaces:
#        for fid2 in ModelData.dictFaces:
#            if ModelData.dictFaces[fid1].get_tag() == ClassFace.DEL:
#                break
#            if fid1 >= fid2 or ModelData.dictFaces[fid2].get_tag() == ClassFace.DEL:
#                continue
#            #if two triangle intersected with each other decompose both
#            if is_triangle_intersect(fid1, fid2):
#                #clean the intersection result to prevent the ill intersected result
#                ModelDataFuncs.clean_duplicated_vertices()
#                ModelDataFuncs.discard_illshaped_faces()
#                str_out = ("Intersecting: face {} and face {}").format(fid1, fid2)
#                os.sys.stdout.write(str_out + "\r")
#                os.sys.stdout.flush()
#    #delete all the marked dictFaces
#    if ModelDataFuncs.remove_faces() > 0:
#        os.sys.stdout.write("\r")
#        os.sys.stdout.flush()
#        #ModelDataFuncs.restore_normals()
#        print ("Decompose finished")
#    else:
#        print ("No decomposing take place")

#recursivel handle the coplanar geometry in the tesslation map
#geometry is the coplanar geometry of the current face fid
def recursively_merge_coplanar_geometry(geometry, fid, mapFaceTesslation, tag):
    if  ModelData.dictFaces[fid].get_id() != ModelData.dictFaces[geometry[0]].get_id():
        print ('Merge intersecting coplaner faces with different semantics')
    tag.append(geometry[0])
    #if geometry in mapFaceTesslation[fid]:
    #    mapFaceTesslation[fid].remove(geometry)
    for geom in mapFaceTesslation[geometry[0]]:
        if len(geom) != 4:
            mapFaceTesslation[fid].append(geom)
        elif geom[0] != fid and geom[0] not in tag:
            recursively_merge_coplanar_geometry( geom, fid, mapFaceTesslation, tag)
    mapFaceTesslation.pop(geometry[0])

#advance version of decomposition
#first extract all the intersection primitives for each triangle and then retriangulate the triangle
def model_decompositionEx():
    print("----Start decomposing the input model----")
    #calc the apaptive tol for global_TOL_WELDING
    #if ModelData.global_ADP_WELDING:
    #    ModelData.global_TOL_WELDING = ModelData.global_ADP_TOL_WELDING * ModelData.

    if ModelData.global_DO_WELDING:# move to here 20170901
        ModelDataFuncs.welding_verts(ModelData.global_TOL_WELDING)
        ModelDataFuncs.clean_duplicated_vertices()
    #detect all the intersections for each face
    mapFaceTesslation = ModelData.collections.OrderedDict()
    for fid in ModelData.dictFaces:
        mapFaceTesslation[fid] = [list(ModelData.dictFaces[fid].get_vids())]
    #find the interesction
    fCount = 0
    for fid1 in ModelData.dictFaces:
        print "\rDecomposed faces:" + str(fCount),
        fCount = fCount + 1
        for fid2 in ModelData.dictFaces:
            if ModelData.dictFaces[fid1].get_tag() == ClassFace.DEL:
                break
            if fid1 >= fid2 or ModelData.dictFaces[fid2].get_tag() == ClassFace.DEL:
                continue
            #can be point, edge or face
            listIntersectingGeometry = extract_intersection(fid1, fid2)
            if len(listIntersectingGeometry) != 0 :
                if len(listIntersectingGeometry) != 3 :
                    bExisit = True
                    for vid in listIntersectingGeometry:
                        if vid not in ModelData.dictFaces[fid1].get_vids():
                            bExisit = False
                            break
                    if not bExisit:
                        mapFaceTesslation[fid1].append(listIntersectingGeometry)
                    bExisit = True
                    for vid in listIntersectingGeometry:
                        if vid not in ModelData.dictFaces[fid2].get_vids():
                            bExisit = False
                            break
                    if not bExisit:
                        mapFaceTesslation[fid2].append(listIntersectingGeometry)
                else:
                    #add coplanar face 
                    mapFaceTesslation[fid1].append([fid2] + listIntersectingGeometry)
                    mapFaceTesslation[fid2].append([fid1] + list(ModelData.dictFaces[fid1].get_vids()))
    
    #predelete the face
    for fid in mapFaceTesslation:
        if len(mapFaceTesslation[fid]) > 1:
            ModelDataFuncs.pre_remove_face_by_faceids([fid])
                    
    #merge coplanar intersecting faces
    tag = []
    for fid in mapFaceTesslation:
        if fid not in tag:
            if len(mapFaceTesslation[fid]) > 1:
                for geometry in mapFaceTesslation[fid]:
                    if len(geometry) == 4 and geometry[0] not in tag:
                        recursively_merge_coplanar_geometry(geometry, fid, mapFaceTesslation, tag)
    for fid in mapFaceTesslation:
        if len(mapFaceTesslation[fid]) > 1:
            for geo in mapFaceTesslation[fid][:]:
                #trick in python (will not skip elements)
                if len(geo) == 4 and geo[0] in tag:
                    mapFaceTesslation[fid].remove(geo)
    #tesselating all the faces
    preservedIDs = []
    for fid in mapFaceTesslation:
        if len(mapFaceTesslation[fid]) > 1:
            print ('\rDecomposing ' + str(fid)),
            bDec, presIDs = face_delaunay_tessellate(fid, mapFaceTesslation[fid])
            if len(presIDs) > 0:
                preservedIDs += presIDs
    #save the preserved faces
    for fid in preservedIDs:
        if ModelData.dictFaces[fid].get_tag() == ClassFace.DEL:
            ModelData.dictFaces[fid].set_tag(ClassFace.FIX)
    
  
    #if ModelData.global_DO_TRUNCATE:
    #    ModelDataFuncs.truncate_verts(ModelData.global_TOL_TRUNCATE)
    #    ModelDataFuncs.clean_duplicated_vertices()
    #if ModelData.global_DO_WELDING:# move to front 20170901 otherwise may cause gap
    #    ModelDataFuncs.welding_verts(ModelData.global_TOL_WELDING)
    #    ModelDataFuncs.clean_duplicated_vertices()
          
    #clean the intersection result to prevent the ill intersected result
    ModelDataFuncs.clean_duplicated_vertices()
    ModelDataFuncs.discard_illshaped_faces()


    str_out = ("After decomposition: {} faces").format(len(ModelData.dictFaces))
    os.sys.stdout.write(str_out + "\r")
    os.sys.stdout.flush()
    #delete all the marked dictFaces
    if ModelDataFuncs.remove_faces() > 0:
        os.sys.stdout.write("\r")
        os.sys.stdout.flush()
        #ModelDataFuncs.restore_normals()
        print ("Decompose finished")
    else:
        print ("No decomposing take place")

#detect whether two faces intersect, if intersect return the intersection geometry. New points should be inserted
#INPUT: fids are ids of faces
#RETURN: the intersection geometry [vid1, vid2, vid3...], can be a point, a line or a face. If not intersect, return the empty list
def extract_intersection(fid1, fid2):
    bboxf1 = get_bbox_of_points([ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[0]], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[1]], ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[2]]])
    bboxf2 = get_bbox_of_points([ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[0]], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[1]], ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[2]]])
    if bboxf1[0][0] > bboxf2[1][0] + Tol or bboxf1[0][1] > bboxf2[1][1] + Tol or bboxf1[0][2] > bboxf2[1][2] + Tol or\
       bboxf2[0][0] > bboxf1[1][0] + Tol or bboxf2[0][1] > bboxf1[1][1] + Tol or bboxf2[0][2] > bboxf1[1][2] + Tol:
         return []

    #Input dictVertices
    vert0 = ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[0]]
    vert1 = ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[1]]
    vert2 = ModelData.dictVertices[ModelData.dictFaces[fid1].get_vids()[2]]
    vert3 = ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[0]]
    vert4 = ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[1]]
    vert5 = ModelData.dictVertices[ModelData.dictFaces[fid2].get_vids()[2]]
    v00 = list_to_c_double_array(vert0)
    v01 = list_to_c_double_array(vert1)
    v02 = list_to_c_double_array(vert2)
    v10 = list_to_c_double_array(vert3)
    v11 = list_to_c_double_array(vert4)
    v12 = list_to_c_double_array(vert5)

    #Intersection result
    curDirBefore = os.getcwd() 
    path = os.path.dirname(os.path.realpath(__file__))
    if sizeof(c_voidp) == 4:
        #win32
        path = os.path.join(path, '..\\TriangleIntersection\\Release')
        os.chdir(path)
        if not os.path.exists("TriangleIntersection.dll"):
            print("DLL missing: " + path + "TriangleIntersection.dll")
        Intersector = CDLL("TriangleIntersection.dll")
    elif sizeof(c_voidp) == 8:
        #x64
        path = os.path.join(path, '..\\TriangleIntersection\\x64\\Release')
        os.chdir(path)
        if not os.path.exists("TriangleIntersection.dll"):
            print("DLL missing: " + path + "TriangleIntersection.dll")
        Intersector = CDLL("TriangleIntersection.dll")
    os.chdir(curDirBefore)

    #isCoplanar returns whether the tris are coplanar
    #intersectPoint1, intersectPoint2 are the endpoints of the line of intersection
    intersectPoint1 = (c_double * 3)()
    intersectPoint2 = (c_double* 3)()
    isCoplaner = c_int(-1)
    returnValue = Intersector.tri_tri_intersect_with_isectline(byref(v00), byref(v01), byref(v02), byref(v10), byref(v11), byref(v12),
                                                                byref(isCoplaner), byref(intersectPoint1), byref(intersectPoint2))
    if 1 == returnValue:
        #intersecting
        if isCoplaner.value == 1:
            #pre process the coplaner dictFaces
            duplicateVts = []
            for vt in ModelData.dictFaces[fid1].get_vids():
                if vt in ModelData.dictFaces[fid2].get_vids():
                    duplicateVts.append(vt) 

            if len(duplicateVts) == 3:
                #remove one of the triangles
                ModelDataFuncs.pre_remove_face_by_faceids([fid2])
                return []
            elif len(duplicateVts) == 2:
                #may be adjacent via edge
                for vid1 in ModelData.dictFaces[fid1].get_vids():
                    if vid1 not in duplicateVts:
                        for vid2 in ModelData.dictFaces[fid2].get_vids():
                            if vid2 not in duplicateVts:
                                bNorm1 = get_face_normal([ModelData.dictVertices[vid1], ModelData.dictVertices[duplicateVts[0]], ModelData.dictVertices[duplicateVts[1]]])
                                bNorm2 = get_face_normal([ModelData.dictVertices[vid2], ModelData.dictVertices[duplicateVts[1]], ModelData.dictVertices[duplicateVts[0]]])
                                #test orientation of triangles (whether points are on the same side of the edge)
                                if ModelDataFuncs.is_have_same_vert(bNorm1, [bNorm2]) or vector_length_3(bNorm1) < Tol or vector_length_3(bNorm2) < Tol :
                                    #connected triangles not overlapping triangles
                                    return []
            else:
                #convert to 2D (simply select an axis aligned projection plane)
                vids = ModelData.dictFaces[fid1].get_vids()
                normal = get_face_normal([ModelData.dictVertices[vids[0]], ModelData.dictVertices[vids[1]], ModelData.dictVertices[vids[2]]])
                #the direction of the projection
                axisProject = get_axis_aligned_projection_plane(normal)
                #extract all the projected vertices
                verts2d = []
                for vid in ModelData.dictFaces[fid1].get_vids():
                    verts2d.append(get_projected_coords(ModelData.dictVertices[vid], axisProject))
                verts2d.append(verts2d[0])
                for vid in ModelData.dictFaces[fid2].get_vids():
                    verts2d.append(get_projected_coords(ModelData.dictVertices[vid], axisProject))
                verts2d.append(verts2d[4])
                #detect intersections
                for i in range(3):
                    for j in range(4, 7):
                        if is_lineseg_intersect_lineseg_2d(verts2d[i], verts2d[i+1], verts2d[j], verts2d[j+1]):
                            return list(ModelData.dictFaces[fid2].get_vids())
                #no intersections
                return []

            #coplanar retriangulate
            return list(ModelData.dictFaces[fid2].get_vids())
        else:
            #handle intersection
            #there can be intersection between vertex-vertex, vertex-edge, vertex-face, edge-edge, edge-face, face-face
            #c_float do not have a value function
            Pt1 = [intersectPoint1[0], intersectPoint1[1], intersectPoint1[2]]
            Pt2 = [intersectPoint2[0], intersectPoint2[1], intersectPoint2[2]]

            #whether intersect at an existing edge/vertex
            bEqualPt = False
            if ModelDataFuncs.is_have_same_vert(Pt1, [Pt2]):
                bEqualPt = True
            
            bVertsInF1 = False
            bVertsInF2 = False
            if ModelDataFuncs.is_have_same_vert(Pt1, [vert0, vert1, vert2]):
                if ModelDataFuncs.is_have_same_vert(Pt2, [vert0, vert1, vert2]):
                    #intersect at an exist edge/vertex of tri1
                    bVertsInF1 = True
        
            if ModelDataFuncs.is_have_same_vert(Pt1, [vert3, vert4, vert5]):
                if ModelDataFuncs.is_have_same_vert(Pt2, [vert3, vert4, vert5]):
                    #intersect at an exist edge/vertex of tri2
                    bVertsInF2 = True

            #do nothing for v ^ v = ev(2) or e ^ e = ee(2)
            if bVertsInF1 and bVertsInF2:
                return []

            
            #triangle tessellation
            Pt1Index = ModelDataFuncs.add_vertex(Pt1)
            if not bEqualPt:
                Pt2Index = ModelDataFuncs.add_vertex(Pt2)

            if bEqualPt:
                return [Pt1Index]
            else:
                return [Pt1Index, Pt2Index]

    else:
        #disjoin
        return []

#tesselate a face (fid) with all the intersecting geometry in a geometryList
#the geometry can be a vertex [vid], an edge [vid1, vid2] or a face [vid1, vid2, vid3]
def face_delaunay_tessellate(fid, geometryList):
    #get the vids
    vertIDlist1 = ModelData.dictFaces[fid].get_vids()
    #used to check the orientation
    normalOfTessFace = get_face_normal([ModelData.dictVertices[vertIDlist1[0]], ModelData.dictVertices[vertIDlist1[1]], ModelData.dictVertices[vertIDlist1[2]]])
    #all the geometry with inverted orientation
    listInvertFaces = []
    for geometry in geometryList:
        if len(geometry) == 3:
            normal = get_face_normal([ModelData.dictVertices[geometry[0]], ModelData.dictVertices[geometry[1]], ModelData.dictVertices[geometry[2]]])
            if vector_length_3(normal) > Tol and dot_product_3(normal, normalOfTessFace) < NeighborAngle:
                #found a coplaner face with inverse orientation
                listInvertFaces.append(geometry)
    #get the segements based on the original vertex id
    segments = []
    #face1
    if [vertIDlist1[0], vertIDlist1[1]] not in segments and [vertIDlist1[1], vertIDlist1[0]] not in segments:
        segments.append([vertIDlist1[0], vertIDlist1[1]])
    if [vertIDlist1[1], vertIDlist1[2]] not in segments and [vertIDlist1[2], vertIDlist1[1]] not in segments:
        segments.append([vertIDlist1[1], vertIDlist1[2]])
    if [vertIDlist1[0], vertIDlist1[2]] not in segments and [vertIDlist1[2], vertIDlist1[0]] not in segments:
        segments.append([vertIDlist1[2], vertIDlist1[0]])
    
    segments_temp = []
    geometryList.pop(0)
    for geom in geometryList:
        if len(geom) == 1:
            segments_temp.append([geom[0], geom[0]])
        elif len(geom) == 2:
            segments_temp.append(geom)
        else:
            segments_temp.append([geom[0], geom[1]])
            segments_temp.append([geom[1], geom[2]])
            segments_temp.append([geom[2], geom[0]])

    segments_temp1 = segments+segments_temp
    #pre decompose the segments and add new dictVertices
    #segments1 = decompose_segment(segments, segments_temp)
    
    segments = decompose_segment_ex(segments_temp1)

    #tesselation
    #collect the ids of dictVertices from segments
    vertexIds = []
    for seg in segments:
        if seg[0] not in vertexIds:
            vertexIds.append(seg[0])
        if seg[1] not in vertexIds:
            vertexIds.append(seg[1])

    vertexIdMap = {}#used for map segment ids
    iVertCount = 0
    for vid in vertexIds:
        vertexIdMap[vid] = iVertCount
        iVertCount += 1 

    #
    vt01 = ModelData.dictVertices[vertIDlist1[0]]
    vt02 = ModelData.dictVertices[vertIDlist1[1]]
    vt03 = ModelData.dictVertices[vertIDlist1[2]]
    #convert to 2D (simply select an axis aligned projection plane)
    normal = get_face_normal([vt01, vt02, vt03])
    #the direction of the projection
    axisProject = get_axis_aligned_projection_plane(normal)
    verts2d = []
    for vid in vertexIds:
        verts2d += get_projected_coords(ModelData.dictVertices[vid], axisProject)

    #triangulation
    curDirBefore = os.getcwd() 
    path = os.path.dirname(os.path.realpath(__file__))
    if sizeof(c_voidp) == 4:
        #win32
        path = os.path.join(path, '..\\triangledll\\Release')
        os.chdir(path)
        if not os.path.exists("triangledll.dll"):
            print("DLL missing: " + path + "triangledll.dll")
        Triangulator = CDLL("triangledll.dll")

    elif sizeof(c_voidp) == 8:
        #x64
        path = os.path.join(path, '..\\triangledll\\x64\\Release')
        os.chdir(path)
        if not os.path.exists("triangledll.dll"):
            print("DLL missing: " + path + "triangledll.dll")
        Triangulator = CDLL("triangledll.dll")
    os.chdir(curDirBefore)
    cVertices = (c_double * (len(vertexIds)*2))()
    for i in range(0, len(vertexIds) * 2):
        cVertices[i] = c_double(verts2d[i])

    c_segments = (c_int * (len(segments)*2))()
    isegcount = 0
    for seg in segments:
        c_segments[isegcount] = c_int(vertexIdMap[seg[0]])
        c_segments[isegcount + 1] = c_int(vertexIdMap[seg[1]])
        isegcount += 2
   
    #triangulation
    numberOfOutputVerts = c_int(0)
    numberOfOutputTriangles = c_int(0)
    
    try:
        Triangulator.simpleTriangulate(byref(cVertices), c_int(len(vertexIds)), byref(c_segments), c_int(len(segments)),
                                    byref(numberOfOutputVerts), byref(numberOfOutputTriangles))
    except:
        print('Triangulator failed!')
        return False, []

    outputVerts = (c_double * (numberOfOutputVerts.value * 2))()
    outputTriangles = (c_int * (numberOfOutputTriangles.value * 3))()

    Triangulator.getResults(pointer(outputVerts), pointer(outputTriangles))

    #if there is new generated dictVertices do interpolation (impossible after pre-segmentation)
    if numberOfOutputVerts.value > len(vertexIds):
        print("Triangle found more vertices!")
        #raise Exception
        #add new dictVertices (the first 6 dictVertices are the input dictVertices)
        for i in range(len(vertexIds), numberOfOutputVerts.value):
            ptNew2d = []
            if axisProject[0]:
                ptNew2d.append(0.0)
                ptNew2d.append(outputVerts[i*2])
                ptNew2d.append(outputVerts[i*2 + 1])
            elif axisProject[1]:
                ptNew2d.append(outputVerts[i*2])
                ptNew2d.append(0.0)
                ptNew2d.append(outputVerts[i*2 + 1])
            elif axisProject[2]:
                ptNew2d.append(outputVerts[i*2])
                ptNew2d.append(outputVerts[i*2 + 1])
                ptNew2d.append(0.0)

            ptEnd = tuple_plus(ptNew2d, axisProject) 
            ptOut = [0]
           
            if RLineWithPlane(ptNew2d, ptEnd, vt01, vt02, vt03, ptOut):
                #add mapping for the new dictVertices
                newVertID = ModelDataFuncs.add_vertex(ptOut[0])
                if vertexIdMap.has_key(newVertID):
                    #revise outputTriangles accordingly
                    for i_tri in range (0, numberOfOutputTriangles.value * 3, 3):
                        if outputTriangles[i_tri] == i:
                            outputTriangles[i_tri] = vertexIdMap[newVertID]
                        if outputTriangles[i_tri+1] == i:
                            outputTriangles[i_tri+1] = vertexIdMap[newVertID]
                        if outputTriangles[i_tri+2] == i:
                            outputTriangles[i_tri+2] = vertexIdMap[newVertID]
                else:
                    vertexIdMap[newVertID] = iVertCount
                iVertCount += 1
            else:
                print("Unexpected error!")
                raise Exception

    #creat a mirror of vertexIdMap
    vertIdMapInvert = {}
    for key in vertexIdMap:
        vertIdMapInvert[vertexIdMap[key]] = key

    #whether a new triangle is added
    bNewTri = False
    preserveID = []
    if numberOfOutputTriangles.value > 0:
        #add new triangles
        iCount = 0
        for i in range(0, numberOfOutputTriangles.value * 3, 3):
            #check for degeneration
            #get the coordinates of dictVertices
            vt1 = ModelData.dictVertices[vertIdMapInvert[outputTriangles[i]]]
            vt2 = ModelData.dictVertices[vertIdMapInvert[outputTriangles[i+1]]]
            vt3 = ModelData.dictVertices[vertIdMapInvert[outputTriangles[i+2]]]
            
            v1 = tuple_minus(vt2, vt1)
            v2 = tuple_minus(vt3, vt1)
            normal = cross_product_3(v1, v2)

            if ModelData.global_DISCARD_DEG:
                #check degeneration and discard the degenerated face
                if vector_length_3(normal) > Tol:
                    prevfID = ModelData.faceID
                    newfID = ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIdMapInvert[outputTriangles[i]], vertIdMapInvert[outputTriangles[i+1]],
                                                            vertIdMapInvert[outputTriangles[i+2]]), normalOfTessFace), ClassFace.FIX))
                    if prevfID != newfID and newfID != -1:
                        preserveID.append(newfID)
                    if newfID != -1:
                        #test with the inverted face list
                        if len(listInvertFaces) > 0:
                            for vids in listInvertFaces:
                                if is_face_in_face(ModelData.dictFaces[newfID].get_vids(), vids):
                                    ModelDataFuncs.invert_face_normal(newfID)
                                    break
                    iCount += 1
                else:
                    iCount += 1
            else:
                #degeneracy is introduced which is necessary
                prevfID = ModelData.faceID
                newfID = ModelDataFuncs.add_face(Class_face(ModelDataFuncs.create_orientated_vids((vertIdMapInvert[outputTriangles[i]], vertIdMapInvert[outputTriangles[i+1]],
                                                        vertIdMapInvert[outputTriangles[i+2]]), normalOfTessFace), ClassFace.FIX))
                if prevfID != newfID and newfID != -1:
                    preserveID.append(newfID)
                if newfID != -1:
                    #test with the inverted face list
                    if len(listInvertFaces) > 0:
                        for vids in listInvertFaces:
                            if is_face_in_face(ModelData.dictFaces[newfID].get_vids(), vids):
                                ModelDataFuncs.invert_face_normal(newfID)
                                break
                iCount += 1

        if iCount != 0:
            bNewTri = True
        else:
            bNewTri = False
    else:
        print("Zero triangle out of triangle")
    return bNewTri, preserveID
#test whether one triangle face is within another triangle face
#INPUT vids? is the vids of a face
#RETURN True means is within
def is_face_in_face(vids1, vids2):
    for v in vids1:
        if not is_point_in_triangle_3(ModelData.dictVertices[v], [ModelData.dictVertices[vids2[0]], ModelData.dictVertices[vids2[1]], ModelData.dictVertices[vids2[2]]]):
            if is_point_in_linesegment(ModelData.dictVertices[v], ModelData.dictVertices[vids2[0]], ModelData.dictVertices[vids2[1]]) or\
                is_point_in_linesegment(ModelData.dictVertices[v], ModelData.dictVertices[vids2[1]], ModelData.dictVertices[vids2[2]]) or\
                is_point_in_linesegment(ModelData.dictVertices[v], ModelData.dictVertices[vids2[2]], ModelData.dictVertices[vids2[0]]):
                pass
            else:
                return False
    return True

#Modify to 2D may be more robust
#Split a triangle with a line along the linesegment (Pt1, Pt2), the intersection is already known
#INPUT: fid is the key of the triangle in ModelData.dictFaces, Pt is the node of the intersection line represented by a three tuple (x, y, z)
#OUTPUT: modify the dictFaces and dictVertices lists in ModelData directly
#RETURN: True means splitted False means did not split
#def DoTriSplit(fid, Pt1, Pt2):
#    
#    #get the coordinates of dictVertices
#    vids = ModelData.dictFaces[fid].get_vids()
#    vt1 = ModelData.dictVertices[vids[0]]
#    vt2 = ModelData.dictVertices[vids[1]]
#    vt3 = ModelData.dictVertices[vids[2]]

#    NewVt1, ExistVt1 = is_lineseg_intersect_ray(vt1, vt2, Pt1, Pt2)
#    NewVt2, ExistVt2 = is_lineseg_intersect_ray(vt2, vt3, Pt1, Pt2)
#    NewVt3, ExistVt3 = is_lineseg_intersect_ray(vt3, vt1, Pt1, Pt2)

#    #edge overlap    
#    if len(NewVt1) == 0 and ExistVt1:
#        return False
#    if len(NewVt2) == 0 and ExistVt2:
#        return False
#    if len(NewVt3) == 0 and ExistVt3:
#        return False

#    #must pass at least an original vertex
#    if ExistVt1 and ExistVt2 and ExistVt3:
#        
#        #
#        tag = 0
#        if ModelDataFuncs.is_have_same_vert(NewVt1, [vt1, vt2, vt3]):
#            tag = tag + 1
#        if ModelDataFuncs.is_have_same_vert(NewVt2, [vt1, vt2, vt3]):
#            tag = tag + 1
#        if ModelDataFuncs.is_have_same_vert(NewVt3, [vt1, vt2, vt3]):
#            tag = tag + 1
#        if tag >= 2:
#            #share an edge
#            print("intersect at an edge")
#            return False

#        #must pass at one original vertex
#        if ModelDataFuncs.is_have_same_vert(NewVt1, [NewVt2]):
#            if ModelDataFuncs.is_have_same_vert(NewVt1, [vt1, vt2, vt3]):
#                #add NewVt3 to edge V1V3
#                ModelData.add_vertex(NewVt3)
#                #add v1v2vnew
#                ModelData.add_face(Class_face(ClassFace.FIX, [vids[0], vids[1], ModelData.vertexID-1]))
#                #add v2v3vnew
#                ModelData.add_face(Class_face(ClassFace.FIX, [vids[1], vids[2], ModelData.vertexID-1]))
#            else:
#                print("Rounding off error!")
#                return False
#        if ModelDataFuncs.is_have_same_vert(NewVt1, [NewVt3]):
#            if ModelDataFuncs.is_have_same_vert(NewVt1, [vt1, vt2, vt3]):
#                #add NewVt2 to edge V2V3
#                ModelData.add_vertex(NewVt2)
#                #add v1v2vnew
#                ModelData.add_face(Class_face(ClassFace.FIX, [vids[0], vids[1], ModelData.vertexID-1]))
#                #add v3v1vnew
#                ModelData.add_face(Class_face(ClassFace.FIX, [vids[2], vids[0], ModelData.vertexID-1]))
#            else:
#                print("Rounding off error!")
#                return False
#        if ModelDataFuncs.is_have_same_vert(NewVt2, [NewVt3]):
#            if ModelDataFuncs.is_have_same_vert(NewVt2, [vt1, vt2, vt3]):
#                #add NewVt1 to edge V1V2
#                ModelData.add_vertex(NewVt1)
#                #add v2v3vnew
#                ModelData.add_face(Class_face(ClassFace.FIX, [vids[1], vids[2], ModelData.vertexID-1]))
#                #add v3v1vnew
#                ModelData.add_face(Class_face(ClassFace.FIX, [vids[2], vids[0], ModelData.vertexID-1]))
#            else:
#                print("Rounding off error!")
#                return False

#    #three cases
#    elif ExistVt1 and ExistVt2:
#        if ModelDataFuncs.is_have_same_vert(NewVt1, [NewVt2]):
#            #intersect at a vertex
#            return False
#        else:
#            #add NewVt1 to edge V1V2 and NewVt2 to edge V2V3
#            NewVt1Index = ModelData.add_vertex(NewVt1)
#            NewVt2Index = ModelData.add_vertex(NewVt2)
#            #add newv1 v2 newv2
#            ModelData.add_face(Class_face(ClassFace.FIX, [NewVt1Index, vids[1], NewVt2Index]))
#            #add newv1 newv2 v1
#            ModelData.add_face(Class_face(ClassFace.FIX, [NewVt1Index, NewVt2Index, vids[0]]))
#            #add newv2 v3 v1
#            ModelData.add_face(Class_face(ClassFace.FIX, [NewVt2Index, vids[2], vids[0]]))
#    elif ExistVt1 and ExistVt3:#intersect at a vertex
#        if ModelDataFuncs.is_have_same_vert(NewVt1, [NewVt3]):
#            #intersect at a vertex
#            return False
#        else:
#            #add NewVt1 to edge V1V2 and NewVt3 to edge V1V3
#            NewVt1Index = ModelData.add_vertex(NewVt1)
#            NewVt3Index = ModelData.add_vertex(NewVt3)
#            #add v1 newv1 newv3
#            ModelData.add_face(Class_face(ClassFace.FIX, [vids[0], NewVt1Index, NewVt3Index]))
#            #add newv1 v2 newv3
#            ModelData.add_face(Class_face(ClassFace.FIX, [NewVt1Index, vids[1], NewVt3Index]))
#            #add newv3 v2 v3
#            ModelData.add_face(Class_face(ClassFace.FIX, [NewVt3Index, vids[1], vids[2]]))
#    elif ExistVt2 and ExistVt3:#intersect at a vertex
#        if ModelDataFuncs.is_have_same_vert(NewVt2, [NewVt3]):
#            #intersect at a vertex
#            return False
#        else:
#            #add NewVt2 to edge V2V3 and NewVt3 to edge V1V3
#            NewVt2Index = ModelData.add_vertex(NewVt2)
#            NewVt3Index = ModelData.add_vertex(NewVt3)
#            #add newv2 v3 newv3
#            ModelData.add_face(Class_face(ClassFace.FIX, [NewVt2Index, vids[2], NewVt3Index]))
#            #add v1 newv2 newv3
#            ModelData.add_face(Class_face(ClassFace.FIX, [vids[0], NewVt2Index, NewVt3Index]))
#            #add v1 v2 newv2
#            ModelData.add_face(Class_face(ClassFace.FIX, [vids[0], vids[1], NewVt2Index]))

#    return True

#Modify to 2D may be more robust
#tessellate a triangle with a linesegment (Pt1, Pt2)
#INPUT: fid is the key of the triangle in ModelData.dictFaces, Pt is the node of the intersection line represented by a three tuple (x, y, z)
#OUTPUT: modify the dictFaces and dictVertices lists in ModelData directly
#RETURN: True means tessellated False means did not tessellate
#def DoTriDelaunayTessellate(fid, Pt1, Pt1Index, Pt2, Pt2Index):
#    #get the coordinates of dictVertices
#    vids = ModelData.dictFaces[fid].get_vids()
#    vt1 = ModelData.dictVertices[vids[0]]
#    vt2 = ModelData.dictVertices[vids[1]]
#    vt3 = ModelData.dictVertices[vids[2]]
#    #convert to 2D (simply select an axis aligned projection plane)
#    v1 = tuple_minus(vt2, vt1)
#    v2 = tuple_minus(vt3, vt1)
#    normal = cross_product_3(v1, v2)
#    #check degeneration
#    if vector_length_3(normal) < Tol:
#        print("degenerate dictFaces!")

#    compareYZ = abs(dot_product_3(normal, (1.0, 0.0, 0.0)))
#    compareXZ = abs(dot_product_3(normal, (0.0, 1.0, 0.0)))
#    compareYX = abs(dot_product_3(normal, (0.0, 0.0, 1.0)))
#    vt1_2d = []
#    vt2_2d = []
#    vt3_2d = []
#    Pt1_2d = []
#    Pt2_2d = []

#    nProject = (0, 0, 0)
#    if compareYZ > compareXZ and compareYZ > compareYX:
#        #choose yz
#        nProject = (1, 0, 0)

#        vt1_2d.append(vt1[1])
#        vt1_2d.append(vt1[2])

#        vt2_2d.append(vt2[1])
#        vt2_2d.append(vt2[2])

#        vt3_2d.append(vt3[1])
#        vt3_2d.append(vt3[2])

#        Pt1_2d.append(Pt1[1])
#        Pt1_2d.append(Pt1[2])

#        Pt2_2d.append(Pt2[1])
#        Pt2_2d.append(Pt2[2])
#    elif compareXZ > compareYZ and compareXZ > compareYX:
#        #choose xz
#        nProject = (0, 1, 0)

#        vt1_2d.append(vt1[0])
#        vt1_2d.append(vt1[2])

#        vt2_2d.append(vt2[0])
#        vt2_2d.append(vt2[2])

#        vt3_2d.append(vt3[0])
#        vt3_2d.append(vt3[2])

#        Pt1_2d.append(Pt1[0])
#        Pt1_2d.append(Pt1[2])

#        Pt2_2d.append(Pt2[0])
#        Pt2_2d.append(Pt2[2])
#    else:
#        #choose xy
#        nProject = (0, 0, 1)

#        vt1_2d.append(vt1[0])
#        vt1_2d.append(vt1[1])

#        vt2_2d.append(vt2[0])
#        vt2_2d.append(vt2[1])

#        vt3_2d.append(vt3[0])
#        vt3_2d.append(vt3[1])

#        Pt1_2d.append(Pt1[0])
#        Pt1_2d.append(Pt1[1])

#        Pt2_2d.append(Pt2[0])
#        Pt2_2d.append(Pt2[1])

#    #triangulation
#    if sizeof(c_voidp) == 4:
#        #win32
#        if not os.path.exists("..\\triangledll\\Release\\triangledll.dll"):
#            print("DLL missing: " + "..\\triangledll\\Release\\triangledll.dll")
#        Triangulator = CDLL("..\\triangledll\\Release\\triangledll.dll")
#    elif sizeof(c_voidp) == 8:
#        #x64
#        if not os.path.exists("..\\triangledll\\x64\\Release\\triangledll.dll"):
#            print("DLL missing: " + "..\\triangledll\\x64\\Release\\triangledll.dll")
#        Triangulator = CDLL("..\\triangledll\\x64\\Release\\triangledll.dll")
#    
#   
#    cVertices = (c_double * 10)()# 5 dictVertices *2
#    cVertices[0] = c_double(vt1_2d[0])
#    cVertices[1] = c_double(vt1_2d[1])

#    cVertices[2] = c_double(vt2_2d[0])
#    cVertices[3] = c_double(vt2_2d[1])

#    cVertices[4] = c_double(vt3_2d[0])
#    cVertices[5] = c_double(vt3_2d[1])

#    cVertices[6] = c_double(Pt1_2d[0])
#    cVertices[7] = c_double(Pt1_2d[1])

#    cVertices[8] = c_double(Pt2_2d[0])
#    cVertices[9] = c_double(Pt2_2d[1])

#    c_segments = (c_int * 8)()# 4 segements *2
#    c_segments[0] = c_int(0)
#    c_segments[1] = c_int(1)

#    c_segments[2] = c_int(1)
#    c_segments[3] = c_int(2)

#    c_segments[4] = c_int(2)
#    c_segments[5] = c_int(0)

#    c_segments[6] = c_int(3)
#    c_segments[7] = c_int(4)

#    #triangulation
#    numberOfOutputVerts = c_int(0)
#    numberOfOutputTriangles = c_int(0)
#    
#    Triangulator.simpleTriangulate(pointer(cVertices), c_int(5), pointer(c_segments), c_int(4),
#                                  byref(numberOfOutputVerts), byref(numberOfOutputTriangles))

#    outputVerts = (c_double * (numberOfOutputVerts.value * 2))()
#    outputTriangles = (c_int * (numberOfOutputTriangles.value * 3))()

#    Triangulator.getResults(pointer(outputVerts), pointer(outputTriangles))

#    #if there is new generated dictVertices do interpolation
#    #create mapping
#    vertsindex={0:vids[0], 1:vids[1], 2:vids[2], 3:Pt1Index, 4:Pt2Index}

#    if numberOfOutputVerts.value > 5:
#        #add new dictVertices the redundent one will be handled afterwards
#        for i in range(5, numberOfOutputVerts.value):
#            ptNew2d = []
#            if nProject == (1, 0, 0):
#                ptNew2d.append(0.0)
#                ptNew2d.append(outputVerts[i*2])
#                ptNew2d.append(outputVerts[i*2 + 1])
#            elif nProject == (0, 1, 0):
#                ptNew2d.append(outputVerts[i*2])
#                ptNew2d.append(0.0)
#                ptNew2d.append(outputVerts[i*2 + 1])
#            elif nProject == (0, 0, 1):
#                ptNew2d.append(outputVerts[i*2])
#                ptNew2d.append(outputVerts[i*2 + 1])
#                ptNew2d.append(0.0)

#            ptEnd = tuple_plus(ptNew2d,nProject) 
#            ptOut = [0]
#            if RLineWithPlane(ptNew2d, ptEnd, vt1, vt2, vt3, ptOut):
#                #add mapping for the new dictVertices
#                vertsindex[i] = ModelData.add_vertex(ptOut[0])
#            else:
#                print("Unexpected error!")
#                return
#  
#    #add new triangles
#    for i in range(0, numberOfOutputTriangles.value * 3, 3):
#        #check for degeneration
#        #get the coordinates of dictVertices
#        vt1 = ModelData.dictVertices[vertsindex[outputTriangles[i]]]
#        vt2 = ModelData.dictVertices[vertsindex[outputTriangles[i+1]]]
#        vt3 = ModelData.dictVertices[vertsindex[outputTriangles[i+2]]]
#            
#        v1 = tuple_minus(vt2, vt1)
#        v2 = tuple_minus(vt3, vt1)
#        normal = cross_product_3(v1, v2)
#        #check degeneration
#        if vector_length_3(normal) < Tol:
#            print("ignore degenerate dictFaces (generated from Triangle):" + str([vt1, vt2, vt3]) + "\n")
#        else:
#            ModelData.add_face(Class_face(ClassFace.FIX, [vertsindex[outputTriangles[i]], vertsindex[outputTriangles[i+1]],
#                                                    vertsindex[outputTriangles[i+2]]]))
#    return True

##tessellate with one additional vertex maually have to handle degenerated cases
#def DoTriDelaunayTessellateAtOneVertex2(fid, Pt, PtIndex):
#    #get the coordinates of dictVertices
#    vids = ModelData.dictFaces[fid].get_vids()
#    #01pt
#    ModelData.add_face(Class_face(ClassFace.FIX, [vids[0], vids[1], PtIndex]))
#    #12pt
#    ModelData.add_face(Class_face(ClassFace.FIX, [vids[1], vids[2], PtIndex]))
#    #20pt
#    ModelData.add_face(Class_face(ClassFace.FIX, [vids[2], vids[0], PtIndex]))
#    return True

##tessellate with one additional vertex
#def DoTriDelaunayTessellateAtOneVertex(fid, Pt, PtIndex):
#    #get the coordinates of dictVertices
#    vids = ModelData.dictFaces[fid].get_vids()
#    vt1 = ModelData.dictVertices[vids[0]]
#    vt2 = ModelData.dictVertices[vids[1]]
#    vt3 = ModelData.dictVertices[vids[2]]
#    #convert to 2D (simply select an axis aligned projection plane)
#    v1 = tuple_minus(vt2, vt1)
#    v2 = tuple_minus(vt3, vt1)
#    normal = cross_product_3(v1, v2)
#    #check degeneration
#    if vector_length_3(normal) < Tol:
#        print("degenerate dictFaces!")

#    compareYZ = abs(dot_product_3(normal, (1.0, 0.0, 0.0)))
#    compareXZ = abs(dot_product_3(normal, (0.0, 1.0, 0.0)))
#    compareYX = abs(dot_product_3(normal, (0.0, 0.0, 1.0)))
#    vt1_2d = []
#    vt2_2d = []
#    vt3_2d = []
#    Pt_2d = []
#    nProject = (0, 0, 0)
#    if compareYZ > compareXZ and compareYZ > compareYX:
#        #choose yz
#        nProject = (1, 0, 0)

#        vt1_2d.append(vt1[1])
#        vt1_2d.append(vt1[2])

#        vt2_2d.append(vt2[1])
#        vt2_2d.append(vt2[2])

#        vt3_2d.append(vt3[1])
#        vt3_2d.append(vt3[2])

#        Pt_2d.append(Pt[1])
#        Pt_2d.append(Pt[2])

#    elif compareXZ > compareYZ and compareXZ > compareYX:
#        #choose xz
#        nProject = (0, 1, 0)

#        vt1_2d.append(vt1[0])
#        vt1_2d.append(vt1[2])

#        vt2_2d.append(vt2[0])
#        vt2_2d.append(vt2[2])

#        vt3_2d.append(vt3[0])
#        vt3_2d.append(vt3[2])

#        Pt_2d.append(Pt[0])
#        Pt_2d.append(Pt[2])

#    else:
#        #choose xy
#        nProject = (0, 0, 1)

#        vt1_2d.append(vt1[0])
#        vt1_2d.append(vt1[1])

#        vt2_2d.append(vt2[0])
#        vt2_2d.append(vt2[1])

#        vt3_2d.append(vt3[0])
#        vt3_2d.append(vt3[1])

#        Pt_2d.append(Pt[0])
#        Pt_2d.append(Pt[1])

#    #triangulation
#    if sizeof(c_voidp) == 4:
#        #win32
#        if not os.path.exists("..\\triangledll\\Release\\triangledll.dll"):
#            print("DLL missing: " + "..\\triangledll\\Release\\triangledll.dll")
#        Triangulator = CDLL("..\\triangledll\\Release\\triangledll.dll")

#    elif sizeof(c_voidp) == 8:
#        #x64
#        if not os.path.exists("..\\triangledll\\x64\\Release\\triangledll.dll"):
#            print("DLL missing: " + "..\\triangledll\\x64\\Release\\triangledll.dll")
#        Triangulator = CDLL("..\\triangledll\\x64\\Release\\triangledll.dll")
#   
#    cVertices = (c_double * 8)()# 4 dictVertices *2
#    cVertices[0] = c_double(vt1_2d[0])
#    cVertices[1] = c_double(vt1_2d[1])

#    cVertices[2] = c_double(vt2_2d[0])
#    cVertices[3] = c_double(vt2_2d[1])

#    cVertices[4] = c_double(vt3_2d[0])
#    cVertices[5] = c_double(vt3_2d[1])

#    cVertices[6] = c_double(Pt_2d[0])
#    cVertices[7] = c_double(Pt_2d[1])

#    c_segments = (c_int * 6)()# 3 segements *2
#    c_segments[0] = c_int(0)
#    c_segments[1] = c_int(1)

#    c_segments[2] = c_int(1)
#    c_segments[3] = c_int(2)

#    c_segments[4] = c_int(2)
#    c_segments[5] = c_int(0)

#    #triangulation
#    numberOfOutputVerts = c_int(0)
#    numberOfOutputTriangles = c_int(0)
#    
#    Triangulator.simpleTriangulate(pointer(cVertices), c_int(4), pointer(c_segments), c_int(3),
#                                  byref(numberOfOutputVerts), byref(numberOfOutputTriangles))

#    outputVerts = (c_double * (numberOfOutputVerts.value * 2))()
#    outputTriangles = (c_int * (numberOfOutputTriangles.value * 3))()

#    Triangulator.getResults(pointer(outputVerts), pointer(outputTriangles))

#    #if there is new generated dictVertices do interpolation
#    #create mapping
#    vertsindex={0:vids[0], 1:vids[1], 2:vids[2], 3:PtIndex}

#    if numberOfOutputVerts.value > 4:
#        #add new dictVertices the redundent one will be handled afterwards
#        for i in range(4, numberOfOutputVerts.value):
#            ptNew2d = []
#            if nProject == (1, 0, 0):
#                ptNew2d.append(0.0)
#                ptNew2d.append(outputVerts[i*2])
#                ptNew2d.append(outputVerts[i*2 + 1])
#            elif nProject == (0, 1, 0):
#                ptNew2d.append(outputVerts[i*2])
#                ptNew2d.append(0.0)
#                ptNew2d.append(outputVerts[i*2 + 1])
#            elif nProject == (0, 0, 1):
#                ptNew2d.append(outputVerts[i*2])
#                ptNew2d.append(outputVerts[i*2 + 1])
#                ptNew2d.append(0.0)

#            ptEnd = tuple_plus(ptNew2d,nProject) 
#            ptOut = [0]
#            if RLineWithPlane(ptNew2d, ptEnd, vt1, vt2, vt3, ptOut):
#                #add mapping for the new dictVertices
#                vertsindex[i] = ModelData.add_vertex(ptOut[0])
#            else:
#                print("Unexpected error!")
#                return
#  
#    #add new triangles
#    for i in range(0, numberOfOutputTriangles.value * 3, 3):
#        #check for degeneration
#        #get the coordinates of dictVertices
#        vt1 = ModelData.dictVertices[vertsindex[outputTriangles[i]]]
#        vt2 = ModelData.dictVertices[vertsindex[outputTriangles[i+1]]]
#        vt3 = ModelData.dictVertices[vertsindex[outputTriangles[i+2]]]
#            
#        v1 = tuple_minus(vt2, vt1)
#        v2 = tuple_minus(vt3, vt1)
#        normal = cross_product_3(v1, v2)
#        #check degeneration
#        if vector_length_3(normal) < Tol:
#            print("ignore degenerate dictFaces:" + str([vt1, vt2, vt3]) + "\n")
#        else:
#            ModelData.add_face(Class_face(ClassFace.FIX, [vertsindex[outputTriangles[i]], vertsindex[outputTriangles[i+1]],
#                                                    vertsindex[outputTriangles[i+2]]]))
#    return True