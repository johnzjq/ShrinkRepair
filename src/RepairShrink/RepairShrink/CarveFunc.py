#this module provide the heurist carving function on dictTetrahedrons
import ModelData
import ModelDataFuncs
import ClassFace
import os
import SimpleMath
import TetraFunc
import operator
import collections
#MODULE description: carve the tetrahedralization at tmp dictFaces
#detailed information plz refer to the readme.vsd

_DEBUG = 1
#Parameters (not used)
#switch for the constrains, 1 measn enable
#Whether rank degenerated tetrahedra first
local_REMOVE_DEG_TETRAHEDRON = True
#keep negihbours of a  kepted tetrahedron
local_KEEP_DEG_TETRAHEDRON_NEIGHBOUR = False
#Constraint 0 is always enabled
#Constraint 5 should only be enabled when the orientations are corrected
#Constraint2 Building_2 0 others 1 201709
#Constraint3Ex  Building_2 1 others Rotterdamdata 0 201709
constraintsCtrl = {'Constraint0':1, 'Constraint1':0, 'Constraint2':0, 'Constraint3':0, 'Constraint5': 0, 'Constraint3Ex': 0}
#indicators is an ordered list of string of switches, indicates the sorting of heuristics, added 201709 for heuristic selection
## e.g.['dof','area','deg'] means sorted firstly by dof and then area and finally deg, the lenth of idicators shoul be equal of less than three
indicators = []#
#whether to seal concave shape, used together with Constraint3
#building 11 AC11 True Rotterdam building2 False
globalSealConcave = False

#Output
globalOutputCarve = True
globalOutputFreq = 1
globalOutputLog = False
globalOutputGlobalSTA = False


#heuristics
# volume is the volume of the candidate tetrahedron; 
# depth is the depth from a apex to the candidate face; 
# distanceToCenter is the distance from the candidate triangle to the center of the model；
# direction is the variation of the direction of the candidate triangle to the main directions
# area is the area of the entire tetrahedron
# level is the carving trace of the tetrahedra
switches = []
if globalOutputGlobalSTA:
    switches = [('dof',1), ('deg', 1), ('volume',1), ('flatness',1),('depth',1),  ('distanceToCenter',1), ('directions',1), ('area' ,1), ('level' ,1), ('curvature',1 )]
else:
    switches = [('dof',0), ('deg', 0), ('volume',0), ('flatness',0),('depth',0),  ('distanceToCenter',0), ('directions',0), ('area' ,0), ('level' ,0), ('curvature',0)]

globalHeuristic = collections.OrderedDict(switches)
#level(strangeOrder) + dof produce the best result 201709!!
globalInvHeuristic = False# whether to inverse the heuristics
strangeOrder = True #orignal order, for test 201709

#SUPPORT FUNCTIONS
#new global + local descriptors should be used when globalOutpuGlobalSTA is True
#indicators is an ordered list of string of switches, indicates the sorting of heuristics,
# e.g.['dof','area','deg'] means sorted firstly by dof and then area and finally deg, the lenth of idicators shoul be equal of less than three
def update_stack_ex():
    #check for the switches
    if not globalOutputGlobalSTA:
        return 
     #init
    sortedTetIDStack = []

    #update curvatures TODO: needs to update locally
    fmax_curvatures = []
    if globalHeuristic['curvature']:
        fmax_curvatures = ModelDataFuncs.cal_curvature_faces(ModelData.listShellFaceIDs)
    
    #building a list with all the dictTetrahedrons attached with TMP dictFaces and their volume
    tmpTetIDs = {}
    fCount = 0


    for fkey in ModelData.listShellFaceIDs:
        #all the facets of a fixed tet are already fix
        if ModelData.dictFaces[fkey].get_tag() == ClassFace.TMP:
            tetList = TetraFunc.find_tetids_by_faceid(fkey, 1)
            tetid = tetList[0]

             #update tetrahedra curvature
            if globalHeuristic['curvature']:
                if fmax_curvatures[fCount] < ModelData.dictTetrahedrons[tetid].get_curvature():
                    ModelData.dictTetrahedrons[tetid].set_curvature(fmax_curvatures[fCount])

            tetShellFaceidList = TetraFunc.get_shell_faceids_from_tetid(tetid)
            #ascending
            if  globalHeuristic['dof']:
                DoF = len(tetShellFaceidList)
            else:
                DoF = 0
            
            #tetFaceidList = TetraFunc.get_faceids_from_tetid(tetid) 160911 speed up
            tetFaceidList = TetraFunc.get_faceids_from_tetid_fast(tetid)

            #level ascending
            level = ModelData.dictTetrahedrons[tetid].get_level()

            #degenerated tetrahedron （shouldn't directly carve, because the tetrahedron may be blocked by constraints）
            degeneracy = 0
            volume = ModelData.dictTetrahedrons[tetid].get_volume()
            
            if  globalHeuristic['deg'] and local_REMOVE_DEG_TETRAHEDRON and volume < SimpleMath.DegTol :
                degeneracy = 1
            else:
                degeneracy = 0

            #heuristics
            if not tmpTetIDs.has_key(tetid):
                tmpTetIDs[tetid] = [tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag()]
                if globalHeuristic['dof']:
                    tmpTetIDs[tetid].append(DoF) #Dof
                if globalHeuristic['deg']:
                    tmpTetIDs[tetid].append(degeneracy) #Deg
                if globalHeuristic['volume']:
                    tmpTetIDs[tetid].append(volume) #volume
                if globalHeuristic['flatness']:
                    tmpTetIDs[tetid].append(ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())/ModelData.dictFaces[fkey].get_area())#flatness depth/area larger->sharper 
                if globalHeuristic['depth']:
                    tmpTetIDs[tetid].append(ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids()))#depth 
                if globalHeuristic['distanceToCenter']:
                    #face center to the model center cannot be used for concave shape
                    vids = ModelData.dictFaces[fkey].get_vids()
                    midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[0]], ModelData.dictVertices[vids[1]])
                    midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[2]], midPt)
                    midPt = SimpleMath.tuple_numproduct(1.0/3.0, midPt)
                    dist = SimpleMath.square_dist_point_to_point(midPt, [0.0, 0.0, 0.0])
                    if strangeOrder:
                        tmpTetIDs[tetid].append(1.0/dist)#distanceToCenter
                    else:
                        tmpTetIDs[tetid].append(dist)#distanceToCenter
                if globalHeuristic['directions']:
                    maxdev = 1#the maximum angle (minimum cos) of the corrent tetrahedron
                    for fid in tetShellFaceidList:
                        fnormal = ModelData.dictFaces[fid].get_normal()
                        fdev = 0 #the minimum angle (maximum cos) of the current boundary face
                        for pNormlTuple in ModelData.listPrincipleNormal:
                            pNorm = pNormlTuple[0]
                            angle = abs(SimpleMath.dot_product_3(fnormal, pNorm))
                            if  angle > fdev:
                                fdev = angle
                        if fdev < maxdev:
                            maxdev = fdev
                    if strangeOrder:
                        tmpTetIDs[tetid].append(maxdev)
                    else:
                        tmpTetIDs[tetid].append(1 - maxdev)
                if globalHeuristic['area']:
                    tmpTetIDs[tetid].append(ModelData.dictTetrahedrons[tetid].get_area())#volume area
                if globalHeuristic['level']:
                    if strangeOrder:
                        tmpTetIDs[tetid].append(level) #larger -level = smaller level
                    else:
                        tmpTetIDs[tetid].append(-1 * level) #larger -level = smaller level
                if globalHeuristic['curvature']:
                    #add curvature
                    if strangeOrder:
                        tmpTetIDs[tetid].append(-1 * ModelData.dictTetrahedrons[tetid].get_curvature())
                    else:
                        tmpTetIDs[tetid].append(ModelData.dictTetrahedrons[tetid].get_curvature())
            else:
                #update the exisiting information (DoF start from 3)
                if DoF != tmpTetIDs[tetid][globalHeuristic.keys().index('dof') + 3]:
                    tmpTetIDs[tetid][globalHeuristic.keys().index('dof') + 3] = DoF

                if degeneracy != tmpTetIDs[tetid][globalHeuristic.keys().index('deg') + 3]:
                    tmpTetIDs[tetid][globalHeuristic.keys().index('deg') + 3] = degeneracy

                volume = ModelData.dictTetrahedrons[tetid].get_volume()
                if volume != tmpTetIDs[tetid][globalHeuristic.keys().index('volume') + 3]:
                    tmpTetIDs[tetid][globalHeuristic.keys().index('volume') + 3] = volume

                flatness = ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())/ModelData.dictFaces[fkey].get_area()
                if flatness !=  tmpTetIDs[tetid][globalHeuristic.keys().index('flatness') + 3]:
                    tmpTetIDs[tetid][globalHeuristic.keys().index('flatness') + 3] = flatness

                depth = ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())
                if depth  != tmpTetIDs[tetid][globalHeuristic.keys().index('depth') + 3]:
                    tmpTetIDs[tetid][globalHeuristic.keys().index('depth') + 3] = depth

                area = ModelData.dictTetrahedrons[tetid].get_area()
                if area  != tmpTetIDs[tetid][globalHeuristic.keys().index('area') + 3]:
                    tmpTetIDs[tetid][globalHeuristic.keys().index('area') + 3] = area

                #face center to the model center
                vids = ModelData.dictFaces[fkey].get_vids()
                midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[0]], ModelData.dictVertices[vids[1]])
                midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[2]], midPt)
                midPt = SimpleMath.tuple_numproduct(1.0/3.0, midPt)
                if strangeOrder:
                    dist = 1.0 / SimpleMath.square_dist_point_to_point(midPt, [0.0, 0.0, 0.0])
                else:
                    dist = SimpleMath.square_dist_point_to_point(midPt, [0.0, 0.0, 0.0])
                if dist  != tmpTetIDs[tetid][globalHeuristic.keys().index('distanceToCenter') + 3]:
                    tmpTetIDs[tetid][globalHeuristic.keys().index('distanceToCenter') + 3] = dist

                #update directions
                maxdev = 1#the maximum angle (minimum cos) of the corrent tetrahedron
                for fid in tetShellFaceidList:
                    fnormal = ModelData.dictFaces[fid].get_normal()
                    fdev = 0 #the minimum angle (maximum cos) of the current boundary face
                    for pNormlTuple in ModelData.listPrincipleNormal:
                        pNorm = pNormlTuple[0]
                        angle = abs(SimpleMath.dot_product_3(fnormal, pNorm))
                        if  angle > fdev:
                            fdev = angle
                    if fdev < maxdev:
                        maxdev = fdev
                if maxdev  != tmpTetIDs[tetid][globalHeuristic.keys().index('directions') + 3]:
                    if strangeOrder:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('directions') + 3] = maxdev
                    else:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('directions') + 3] = 1-maxdev
                #
                if level != tmpTetIDs[tetid][globalHeuristic.keys().index('level') + 3]:
                    if strangeOrder:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('level') + 3] = level
                    else:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('level') + 3] = -1 * level
                #
                curvature = ModelData.dictTetrahedrons[tetid].get_curvature() 
                if curvature != tmpTetIDs[tetid][globalHeuristic.keys().index('curvature') + 3]:
                    if strangeOrder:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('curvature') + 3] = -1 * curvature#inverse the order
                    else:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('curvature') + 3] = curvature#inverse the order

           
        fCount = fCount + 1;

    sortedTetIDStack = []
    #add all the data
    for key in tmpTetIDs:
        sortedTetIDStack.append(([key]+tmpTetIDs[key]))
    #correction
    if globalInvHeuristic:
        indicators.reverse()

    for indicator in indicators:
        sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[globalHeuristic.keys().index(indicator) + 4], reverse = True)#larger value first
    
    sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[globalHeuristic.keys().index('deg') + 4], reverse = True)
    sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[3], reverse = True)#TMP tetrahedron first    
 

    if len(sortedTetIDStack) > 0 and _DEBUG:
        print "Current tetId:" + str(sortedTetIDStack[0][0])
        print "number of candidate tetrahedron: " + str(len(sortedTetIDStack))
    #str_out = ("number of candidate tetrahedron: {} ").format(len(sortedTetIDStack))
    #os.sys.stdout.write(str_out + "\r")
    #os.sys.stdout.flush()
   
    #if sortedTetIDStack[0][0] == 11:
    #    stop = 99
    return sortedTetIDStack

#Rebuild the sortedtetsidtack and the shellfaceidlist
#old dof+others
#INPUT OUTPUT is the stack
def update_stack():
    #init
    sortedTetIDStack = []

    #update curvatures TODO: needs to update locally
    fmax_curvatures = []
    if globalHeuristic['curvature']:
        fmax_curvatures = ModelDataFuncs.cal_curvature_faces(ModelData.listShellFaceIDs)
    
    #building a list with all the dictTetrahedrons attached with TMP dictFaces and their volume
    tmpTetIDs = {}
    fCount = 0


    for fkey in ModelData.listShellFaceIDs:
        #all the facets of a fixed tet are already fix
        if ModelData.dictFaces[fkey].get_tag() == ClassFace.TMP:
            tetList = TetraFunc.find_tetids_by_faceid(fkey, 1)
            tetid = tetList[0]

             #update tetrahedra curvature
            if globalHeuristic['curvature']:
                if fmax_curvatures[fCount] < ModelData.dictTetrahedrons[tetid].get_curvature():
                    ModelData.dictTetrahedrons[tetid].set_curvature(fmax_curvatures[fCount])

            ##start--test5 bad
            tetShellFaceidList = TetraFunc.get_shell_faceids_from_tetid(tetid)
            if  globalHeuristic['dof']:
                DoF = 4 - len(tetShellFaceidList)
            else:
                DoF = 0
            
            #tetFaceidList = TetraFunc.get_faceids_from_tetid(tetid) 160911 speed up
            tetFaceidList = TetraFunc.get_faceids_from_tetid_fast(tetid)
      

            #level ascending
            level = ModelData.dictTetrahedrons[tetid].get_level()

            #degenerated tetrahedron （shouldn't directly carve, because the tetrahedron may be blocked by constraints）
            degeneracy = 0
            volume = ModelData.dictTetrahedrons[tetid].get_volume()
            
            if  globalHeuristic['deg'] and local_REMOVE_DEG_TETRAHEDRON and volume < SimpleMath.DegTol :
                degeneracy = 1
            else:
                degeneracy = 0

            
            if globalOutputGlobalSTA:
                 #different configurations of heuristics
                 if not tmpTetIDs.has_key(tetid):
                    tmpTetIDs[tetid] = [tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy]
                    if globalHeuristic['volume']:
                        tmpTetIDs[tetid].append(ModelData.dictTetrahedrons[tetid].get_volume()) #volume
                    if globalHeuristic['flatness']:
                        tmpTetIDs[tetid].append(ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())/ModelData.dictFaces[fkey].get_area())#flatness depth/area larger->sharper 
                    if globalHeuristic['depth']:
                        tmpTetIDs[tetid].append(ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids()))#depth 
                    if globalHeuristic['distanceToCenter']:
                        #face center to the model center cannot be used for concave shape
                        vids = ModelData.dictFaces[fkey].get_vids()
                        midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[0]], ModelData.dictVertices[vids[1]])
                        midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[2]], midPt)
                        midPt = SimpleMath.tuple_numproduct(1.0/3.0, midPt)
                        dist = 1.0/SimpleMath.square_dist_point_to_point(midPt, [0.0, 0.0, 0.0])
                        tmpTetIDs[tetid].append(dist)#reciprocal distanceToCenter
                    if globalHeuristic['directions']:
                        maxdev = 1#the maximum angle (minimum cos) of the corrent tetrahedron
                        for fid in tetShellFaceidList:
                            fnormal = ModelData.dictFaces[fid].get_normal()
                            fdev = 0 #the minimum angle (maximum cos) of the current boundary face
                            for pNormlTuple in ModelData.listPrincipleNormal:
                                pNorm = pNormlTuple[0]
                                angle = abs(SimpleMath.dot_product_3(fnormal, pNorm))
                                if  angle > fdev:
                                    fdev = angle
                            if fdev < SimpleMath.NeighborAngle and fdev < maxdev:
                                maxdev = fdev
                        tmpTetIDs[tetid].append(maxdev)
                    if globalHeuristic['area']:
                        tmpTetIDs[tetid].append(ModelData.dictTetrahedrons[tetid].get_area())#volume area
                    if globalHeuristic['level']:
                        tmpTetIDs[tetid].append(level)
                    if globalHeuristic['curvature']:
                        #add curvature
                        tmpTetIDs[tetid].append(-1 * ModelData.dictTetrahedrons[tetid].get_curvature())#inverse the order
                 else:
                    #update the exisiting information (DoF start from 3)
                    print globalHeuristic.keys().index('dof') + 3
                    if DoF != tmpTetIDs[tetid][globalHeuristic.keys().index('dof') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('dof') + 3] = DoF

                    if degeneracy != tmpTetIDs[tetid][globalHeuristic.keys().index('deg') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('deg') + 3] = degeneracy

                    volume = ModelData.dictTetrahedrons[tetid].get_volume()
                    if volume != tmpTetIDs[tetid][globalHeuristic.keys().index('volume') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('volume') + 3] = volume

                    flatness = ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())/ModelData.dictFaces[fkey].get_area()
                    if flatness !=  tmpTetIDs[tetid][globalHeuristic.keys().index('flatness') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('flatness') + 3] = flatness

                    depth = ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())
                    if depth  != tmpTetIDs[tetid][globalHeuristic.keys().index('depth') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('depth') + 3] = depth

                    area = ModelData.dictTetrahedrons[tetid].get_area()
                    if area  != tmpTetIDs[tetid][globalHeuristic.keys().index('area') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('area') + 3] = area

                    #face center to the model center
                    vids = ModelData.dictFaces[fkey].get_vids()
                    midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[0]], ModelData.dictVertices[vids[1]])
                    midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[2]], midPt)
                    midPt = SimpleMath.tuple_numproduct(1.0/3.0, midPt)
                    dist = 1.0/SimpleMath.square_dist_point_to_point(midPt, [0.0, 0.0, 0.0])
                    if dist  != tmpTetIDs[tetid][globalHeuristic.keys().index('distanceToCenter') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('distanceToCenter') + 3] = dist

                    #update directions
                    maxdev = 1#the maximum angle (minimum cos) of the corrent tetrahedron
                    for fid in tetShellFaceidList:
                        fnormal = ModelData.dictFaces[fid].get_normal()
                        fdev = 0 #the minimum angle (maximum cos) of the current boundary face
                        for pNormlTuple in ModelData.listPrincipleNormal:
                            pNorm = pNormlTuple[0]
                            angle = abs(SimpleMath.dot_product_3(fnormal, pNorm))
                            if  angle > fdev:
                                fdev = angle
                        if fdev < SimpleMath.NeighborAngle and fdev < maxdev:
                            maxdev = fdev
                    if maxdev  != tmpTetIDs[tetid][globalHeuristic.keys().index('directions') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('directions') + 3] = maxdev
                    #
                    if level != tmpTetIDs[tetid][globalHeuristic.keys().index('level') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('level') + 3] = level
                    #
                    curvature = ModelData.dictTetrahedrons[tetid].get_curvature() 
                    if curvature != tmpTetIDs[tetid][globalHeuristic.keys().index('curvature') + 3]:
                        tmpTetIDs[tetid][globalHeuristic.keys().index('curvature') + 3] = -1 * curvature#inverse the order

            else:
                #different configurations of heuristics
                if not tmpTetIDs.has_key(tetid):
                    if globalHeuristic['volume']:
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, ModelData.dictTetrahedrons[tetid].get_volume()) #volume
                    elif globalHeuristic['flatness']:
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())/ModelData.dictFaces[fkey].get_area())#flatness depth/area larger->sharper 
                    elif globalHeuristic['depth']:
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids()))#depth 
                    elif globalHeuristic['area']:
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, ModelData.dictTetrahedrons[tetid].get_area())#volume area
                    elif globalHeuristic['distanceToCenter']:
                        #face center to the model center cannot be used for concave shape
                        vids = ModelData.dictFaces[fkey].get_vids()
                        midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[0]], ModelData.dictVertices[vids[1]])
                        midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[2]], midPt)
                        midPt = SimpleMath.tuple_numproduct(1.0/3.0, midPt)
                        dist = 1.0/SimpleMath.square_dist_point_to_point(midPt, [0.0, 0.0, 0.0])
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, dist)#reciprocal distanceToCenter
                    elif globalHeuristic['directions']:
                        maxdev = 1#the maximum angle (minimum cos) of the corrent tetrahedron
                        for fid in tetShellFaceidList:
                            fnormal = ModelData.dictFaces[fid].get_normal()
                            fdev = 0 #the minimum angle (maximum cos) of the current boundary face
                            for pNormlTuple in ModelData.listPrincipleNormal:
                                pNorm = pNormlTuple[0]
                                angle = abs(SimpleMath.dot_product_3(fnormal, pNorm))
                                if  angle > fdev:
                                    fdev = angle
                            if fdev < SimpleMath.NeighborAngle and fdev < maxdev:
                                maxdev = fdev
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, maxdev)
                    elif globalHeuristic['level']:
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, level)
                    elif globalHeuristic['curvature']:
                        #add -1 * curvature invers order 
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, -1 * ModelData.dictTetrahedrons[tetid].get_curvature())
                    else:
                        #nothing more than DoF
                        tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, 0)#simplest
                else:
                    #update the exisiting information
                    if globalHeuristic['volume']:
                        volume = ModelData.dictTetrahedrons[tetid].get_volume()
                        if DoF < tmpTetIDs[tetid][3] or degeneracy > tmpTetIDs[tetid][4] or volume > tmpTetIDs[tetid][5]:
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, volume) #volume
                    elif globalHeuristic['flatness']:
                        flatness = ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())/ModelData.dictFaces[fkey].get_area()
                        if DoF < tmpTetIDs[tetid][3] or degeneracy > tmpTetIDs[tetid][4] or flatness < tmpTetIDs[tetid][5]:
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, flatness)#flatness
                    elif globalHeuristic['depth']:
                        depth = ModelData.dictTetrahedrons[tetid].get_depth(ModelData.dictFaces[fkey].get_vids())
                        if DoF < tmpTetIDs[tetid][3] or degeneracy > tmpTetIDs[tetid][4] or depth < tmpTetIDs[tetid][5]:
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, depth)#depth
                    elif globalHeuristic['area']:
                        area = ModelData.dictTetrahedrons[tetid].get_area()
                        if DoF < tmpTetIDs[tetid][3] or degeneracy > tmpTetIDs[tetid][4] or area < tmpTetIDs[tetid][5]:
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, area)#area of the tetrahedron
                    elif globalHeuristic['distanceToCenter']:
                        #face center to the model center
                        vids = ModelData.dictFaces[fkey].get_vids()
                        midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[0]], ModelData.dictVertices[vids[1]])
                        midPt = SimpleMath.tuple_plus(ModelData.dictVertices[vids[2]], midPt)
                        midPt = SimpleMath.tuple_numproduct(1.0/3.0, midPt)
                        dist = 1.0/SimpleMath.square_dist_point_to_point(midPt, [0.0, 0.0, 0.0])
                        if DoF < tmpTetIDs[tetid][3] or degeneracy > tmpTetIDs[tetid][4] or dist > tmpTetIDs[tetid][5]: 
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, dist)#reciprocal distanceToCenter
                    elif  globalHeuristic['directions']:
                        #update directions
                        maxdev = 1#the maximum angle (minimum cos) of the corrent tetrahedron
                        for fid in tetShellFaceidList:
                            fnormal = ModelData.dictFaces[fid].get_normal()
                            fdev = 0 #the minimum angle (maximum cos) of the current boundary face
                            for pNormlTuple in ModelData.listPrincipleNormal:
                                pNorm = pNormlTuple[0]
                                angle = abs(SimpleMath.dot_product_3(fnormal, pNorm))
                                if  angle > fdev:
                                    fdev = angle
                            if fdev < SimpleMath.NeighborAngle and fdev < maxdev:
                                maxdev = fdev
                        if DoF != tmpTetIDs[tetid][3] or maxdev != tmpTetIDs[tetid][5]:
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, maxdev)
                    elif globalHeuristic['level']:
                        if DoF != tmpTetIDs[tetid][3] or level != tmpTetIDs[tetid][5]:
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, level)
                    elif globalHeuristic['curvature']:
                        if DoF != tmpTetIDs[tetid][3] or  -1 * ModelData.dictTetrahedrons[tetid].get_curvature() != tmpTetIDs[tetid][5]:
                            #add curvature inverse order
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, -1 * ModelData.dictTetrahedrons[tetid].get_curvature())
                    else:
                        #nothing more than DoF
                        if DoF != tmpTetIDs[tetid][3]:
                            tmpTetIDs[tetid] = (tetShellFaceidList, tetFaceidList, ModelData.dictTetrahedrons[tetid].get_tag(), DoF, degeneracy, 0)#simplest
        fCount = fCount + 1;
    
    if globalOutputGlobalSTA:
        #new
        for key in tmpTetIDs:
            sortedTetIDStack.append(([key]+tmpTetIDs[key]))
        sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[globalHeuristic.keys().index('area') + 4], reverse = True)# False means smaller ratio first (not for distance)
        sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[globalHeuristic.keys().index('deg') + 4], reverse = True)# degeneracy first (1 true, 0 false)
        sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[globalHeuristic.keys().index('dof') + 4], reverse = False)#smaller DoF first
        sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[3], reverse = True)#TMP tetrahedron first    
    else:
        #old
        #sort firstly by fix/tmp, secondly by DoF, thirdly by others
        if globalHeuristic['directions']:
            for key in tmpTetIDs:
                sortedTetIDStack.append((key, tmpTetIDs[key][0], tmpTetIDs[key][1], tmpTetIDs[key][2], tmpTetIDs[key][3], tmpTetIDs[key][4], tmpTetIDs[key][5]))
            #sort firstly by fix/tmp, secondly by level, thirdly by DoF, lastly by direction
            #sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[6], reverse = False)#Smaller normal angle (larger cos value) first
            sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[5], reverse = False)#smaller level first
            #sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[7], reverse = True)#larger volumed tet first
            sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[4], reverse = False)#smaller DoF firsrt effective
            sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[3], reverse = True)#TMP tetrahedron first
            pass
        else:
            for key in tmpTetIDs:
                sortedTetIDStack.append((key, tmpTetIDs[key][0], tmpTetIDs[key][1], tmpTetIDs[key][2], tmpTetIDs[key][3], tmpTetIDs[key][4], tmpTetIDs[key][5]))
            sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[6], reverse = True)# False means smaller ratio first
            sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[5], reverse = True)# degeneracy first (1 true, 0 false)
            sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[4], reverse = False)#smaller DoF first
            sortedTetIDStack = sorted(sortedTetIDStack, key=lambda tet: tet[3], reverse = True)#TMP tetrahedron first

    if len(sortedTetIDStack) > 0 and _DEBUG:
        print "Current tetId:" + str(sortedTetIDStack[0][0])
        print "number of candidate tetrahedron: " + str(len(sortedTetIDStack))
    #str_out = ("number of candidate tetrahedron: {} ").format(len(sortedTetIDStack))
    #os.sys.stdout.write(str_out + "\r")
    #os.sys.stdout.flush()
   
    #if sortedTetIDStack[0][0] == 11:
    #    stop = 99
    return sortedTetIDStack

#check the whether the edge recorded in vertexList is on the boundary or not (should be noted that on the boundary does not necessary means non-2-manifold)
#INPUT vertexList represent an edge with a list [v1, v2]
#RETURN True if the edge is on the boundary verse vice 
def is_edge_on_boundary(edge):
    for fid in ModelData.listShellFaceIDs:
        try:
            if edge[0] in ModelData.dictFaces[fid].get_vids() and edge[1] in ModelData.dictFaces[fid].get_vids():
                return True
        except:
            fewaf = 999

    return False

#check the whether the vertex is on the boundary or not (should be noted that on the boundary does not necessary means non-2-manifold)
#INPUT vid represent the id of the vertex
#RETURN True if the vertex is on the boundary verse vice 
def is_vertex_on_boundary(vid):
     for fid in ModelData.listShellFaceIDs:
        if vid in ModelData.dictFaces[fid].get_vids():
            return True
     return False
    
#convert/add the boundary dictFaces of a tet (curTetId) to FIX and KEEP
#INPUT:curTetId is the id of the tet, and faceIDsInCurTet is the known dictFaces of the tet
def keep_tetrahedron(curTetId, faceIDsInCurTet):
    if curTetId == 21:
        feaw = 99
    #use the tag of the tetrahedron
    if ModelData.dictTetrahedrons[curTetId].get_tag() == ClassFace.FIX:
        return
    #check whether all fixed faces are hidden inside of this tetrahedron 201707 failed
    if 0:
        num = 0
        num2 = 0
        for fid in faceIDsInCurTet:
            if  (ModelData.dictFaces[fid].get_tag() == ClassFace.FIX):
                 if (fid not in ModelData.listShellFaceIDs):
                    tetList = TetraFunc.find_tetids_by_faceid(fid)
                    if len(tetList) > 1:
                        if curTetId == tetList[0]:
                            if ModelData.dictTetrahedrons[tetList[1]].get_tag() == ClassFace.FIX:
                                carve_tetrahedron(curTetId, faceIDsInCurTet)
                                print ('keep prevented')
                                return
                                #f_logfile.write('keep prevented')
                        else:
                            if ModelData.dictTetrahedrons[tetList[0]].get_tag() == ClassFace.FIX:
                                carve_tetrahedron(curTetId, faceIDsInCurTet)
                                print ('keep prevented')
                                return
                                #f_logfile.write('keep prevented')
    #makes no sense 201709
    if 0: 
        #keep FLAT tetrahedron's none flat neighbour based on normal direction 20160210
        # the following algorithm is based on the fact that the tetrahedron is flat
        volume = ModelData.dictTetrahedrons[curTetId].get_volume()
        if  volume < SimpleMath.DegTol and local_KEEP_DEG_TETRAHEDRON_NEIGHBOUR:
            fid = -1
            for i in faceIDsInCurTet:
                if i in ModelData.listShellFaceIDs:
                    if ModelData.dictFaces[i].get_tag() == ClassFace.FIX:
                    #in case a flat tetrahedron should be kept cause of constraints
                        fid = i
                        break;
            if fid > 0 :
                #found the fixed triangle
                vertexList = ModelData.dictFaces[fid].get_vids()
                #find the opposite vertex
                oppVert = -1
                #the opposite edge list
                eList = []
                for v in ModelData.dictTetrahedrons[curTetId].get_vids():
                    if v not in ModelData.dictFaces[fid].get_vids():
                        oppVert = v
                        break
                #find the opposite triangles
                f01 = ClassFace.Class_face((vertexList[0], vertexList[1], vertexList[2]))
                f02 = ClassFace.Class_face((oppVert, vertexList[1], vertexList[2]))
                if SimpleMath.dot_product_3(f01.get_normal(), f02.get_normal()) > 0:#problematic
                    #found the opposite triangle
                    tetList = TetraFunc.find_tetids_by_face(f02)
                    for tetId in tetList:
                        if tetId != curTetId:
                            #keep the neighbouring tet 
                            keep_tetrahedron(tetId, TetraFunc.get_faceids_from_tetid_fast(tetId))

                f11 = ClassFace.Class_face((vertexList[1], vertexList[0], vertexList[2]))
                f12 = ClassFace.Class_face((oppVert, vertexList[0], vertexList[2]))
                if SimpleMath.dot_product_3(f11.get_normal(), f12.get_normal()) > 0:
                    #found the opposite triangle
                    tetList = TetraFunc.find_tetids_by_face(f12)
                    for tetId in tetList:
                        if tetId != curTetId:
                            #keep the neighbouring tet 
                            keep_tetrahedron(tetId, TetraFunc.get_faceids_from_tetid_fast(tetId))

                f21 = ClassFace.Class_face((vertexList[2], vertexList[0], vertexList[1]))
                f22 = ClassFace.Class_face((oppVert, vertexList[0], vertexList[1]))
                if SimpleMath.dot_product_3(f21.get_normal(), f22.get_normal()) > 0:
                    #found the opposite triangle
                    tetList = TetraFunc.find_tetids_by_face(f22)
                    for tetId in tetList:
                        if tetId != curTetId:
                            #keep the neighbouring tet 
                            keep_tetrahedron(tetId, TetraFunc.get_faceids_from_tetid_fast(tetId))

    #set the tag
    ModelData.dictTetrahedrons[curTetId].set_tag(ClassFace.FIX)
    #deal with all the known faces
    for j in faceIDsInCurTet:
        if  ModelData.dictFaces[j].get_tag() != ClassFace.FIX:
            if j == 65:
                fewafa = 999
            ModelData.dictFaces[j].set_tag(ClassFace.KEEP)
    #add the unkown faces and define them as KEEP (in order to seperate KEEP and FIX)
    if len(faceIDsInCurTet) < 4:
        vertexList = ModelData.dictTetrahedrons[curTetId].get_vids()
        faceList = []
        faceList.append((vertexList[0], vertexList[1], vertexList[2]))
        faceList.append((vertexList[0], vertexList[2], vertexList[3]))
        faceList.append((vertexList[0], vertexList[3], vertexList[1]))
        faceList.append((vertexList[1], vertexList[2], vertexList[3]))
        for f in faceList:
            isDefined = False
            for i in faceIDsInCurTet:
                if ModelData.dictFaces[i].is_equal_geometry(ClassFace.Class_face(f)):
                    isDefined = True
                    break
            if not isDefined :
                tetNormal = []
                for v in vertexList:
                    if v not in f:
                        #facing outwards
                        tetNormal = SimpleMath.tuple_minus(ModelData.dictVertices[f[0]], ModelData.dictVertices[v])
                        break
                #do not have to consider semantics at this moment
                fId = ModelDataFuncs.add_face(ClassFace.Class_face(ModelDataFuncs.create_orientated_vids(f, tetNormal), ClassFace.KEEP))
                if fId == 100:
                    fewafa = 999

#Carve the tetrahedron: delete all the TMP boundary face of the tetrahedron and add the unknown boundary ones as TMP
#INPUT: curTetId is the id of the tet and faceIDsInCurTet is a list of known dictFaces
#RETURN: 
def carve_tetrahedron(curTetId, faceIDsInCurTet):
    #remove the known TMP face of this tetrahedron and locally keep the adjacent FIX tetrahedron
    for i in faceIDsInCurTet:
        if ModelData.dictFaces[i].get_tag() == ClassFace.TMP:
            #on the shell
            ModelDataFuncs.pre_remove_face_by_faceids([i])
            #update the list of shell faces (TMP face must be on the shell) DO NOT DO THIS, SOLVED in REMOVE FACE function
            #ModelData.listShellFaceIDs.remove(i)
        else: #commnented 20170818 uncommented 20170831 for keep the shell fixed tetrahedron
            #20160210
            #deal with adjacent fixed tetrahedron
            if i not in ModelData.listShellFaceIDs:
                ModelData.listShellFaceIDs.append(i)
            if  ModelData.dictFaces[i].get_tag() == ClassFace.FIX:
                tetList = TetraFunc.find_tetids_by_faceid(i)
                for tetId in tetList:
                    if tetId != curTetId:
                        #keep the tet with fixed or keep shell face, #note the kept tetrahedron should not be flat #Added volume if 201709
                        volume = ModelData.dictTetrahedrons[curTetId].get_volume()
                        if  volume > SimpleMath.DegTol:
                            keep_tetrahedron(tetId, TetraFunc.get_faceids_from_tetid_fast(tetId))
        #elif ModelData.dictFaces[i].get_tag() == ClassFace.FIX or ModelData.dictFaces[i].get_tag() == ClassFace.KEEP:#added 201708
        #     ModelData.listShellFaceIDs.append(i)
    if len(faceIDsInCurTet) < 4:
        #add the undefined dictFaces as TMP dictFaces
        vertexList = ModelData.dictTetrahedrons[curTetId].get_vids()
        faceList = []
        faceList.append((vertexList[0], vertexList[1], vertexList[2]))
        faceList.append((vertexList[0], vertexList[2], vertexList[3]))
        faceList.append((vertexList[0], vertexList[3], vertexList[1]))
        faceList.append((vertexList[1], vertexList[2], vertexList[3]))
        if curTetId == 30 :
            fewaf = 99
        for f in faceList:
            isDefined = False
            for i in faceIDsInCurTet:
                if ModelData.dictFaces[i].is_equal_geometry(ClassFace.Class_face(f)):
                    isDefined = True
                    if i not in ModelData.listShellFaceIDs:
                        print 'this case exists'#20160210
                        ModelData.listShellFaceIDs.append(i)

                    #propagate the level value
                    TetIds = TetraFunc.find_tetids_by_faceid(i)
                    for tid in TetIds:
                        if ModelData.dictTetrahedrons[tid].get_level() < ModelData.dictTetrahedrons[curTetId].get_level():
                            ModelData.dictTetrahedrons[tid].set_level(ModelData.dictTetrahedrons[curTetId].get_level() + 1)
                    break
            if not isDefined :
                #add the tmp face and update the list of shell faces
                faceid = ModelDataFuncs.add_face(ClassFace.Class_face(f))
                if faceid == 42:
                    fewa = 22;
                ModelData.listShellFaceIDs.append(faceid)
                #propagate the level value
                TetIds = TetraFunc.find_tetids_by_faceid(faceid)
                for tid in TetIds:
                    if ModelData.dictTetrahedrons[tid].get_level() == 0:
                        ModelData.dictTetrahedrons[tid].set_level(ModelData.dictTetrahedrons[curTetId].get_level() + 1)

    #remove the tetrahedron
    ModelData.dictTetrahedrons.pop(curTetId)

#NO NEEDED Tetrahedra have fix facets on the shell are all kept, Constrain 0
#Why: it has been ensured by the datastructure
#the validity constraint Constraint0, check whether the FIX neighbor face is singular
#INPUT: curTetId is the id of the tet and faceIDsInCurTet is a list of know boundary dictFaces
#RETURN: True means not pass
def constraint_0(curTetId, faceIDsInCurTet):
    for i in faceIDsInCurTet:
        if ModelData.dictFaces[i].get_tag() == ClassFace.FIX:
            foundTets = TetraFunc.find_tetids_by_faceid(i)
            if len(foundTets) == 1:
                if foundTets[0] == curTetId:#verify
                    return True
                else:
                    print("Something goes wrong in constraint_0!")
                    raise Exception
            elif len(foundTets) != 2:
                print("Something goes wrong in constraint_0!")
                raise Exception
    return False

#the shape constraint Constraint5, check whether the tet is inside the input model (used when global_VALID_ORIENTATION is true)
#all the fix facets of the tetrahedron is used
#INPUT: curTetId is the id of the tet and faceIDsInCurTet is a list of know boundary dictFaces
#RETURN: True means inside, thus not pass
def constraint_5(curTetId, faceIDsInCurTet):
    bIsInterior = False
    for i in faceIDsInCurTet:
        if ModelData.dictFaces[i].get_tag() == ClassFace.FIX and i in ModelData.listShellFaceIDs:#20160210
            #normal check
            vIds = ModelData.dictFaces[i].get_vids()
            vectorNormal = SimpleMath.get_face_normal([ModelData.dictVertices[vIds[0]], ModelData.dictVertices[vIds[1]], ModelData.dictVertices[vIds[2]]])
            for v in ModelData.dictTetrahedrons[curTetId].get_vids():
                if v not in vIds:
                    #test whether the tetrahedron is in the interior
                    vectorTest = SimpleMath.tuple_minus(ModelData.dictVertices[v], ModelData.dictVertices[vIds[0]]);
                    if SimpleMath.dot_product_3(vectorNormal , vectorTest) < 0:
                        #find one inside
                        return True
    return bIsInterior

#recursively search in the circle of dictTetrahedrons around a given vertex, start from the given tetrahedron and the face (edge, vert); 
#end up with the boundary face or the fixed face
#INPUT: tet is the id of tetrahedron, edge is [vert1, vert2], vert is the id of vertex
#RETURN: True reach the bounday face, False blocked by a fixed face
#def circle_tetfid_by_vertex(tet, edge, vert, tetList):
#    if tet not in tetList:
#        tetList.append(tet)
#    #check current face
#    for f in ModelData.dictFaces:
#        if ModelData.dictFaces[f].is_equal_geometry(ClassFace.Class_face((edge[0], edge[1], vert))):
#            if ModelData.dictFaces[f].get_tag() in (ClassFace.FIX, ClassFace.KEEP):
#                #blocked
#                return False
#            elif ModelData.dictFaces[f].get_tag() == ClassFace.TMP:
#                #reached the boundary
#                return True
#    
#    #find the neighbouring face
#    for tid in ModelData.dictTetrahedrons:
#        if tid in tetList:
#            continue
#        if ModelData.dictTetrahedrons[tid].is_triangle_in_tet(ClassFace.Class_face((edge[0], edge[1], vert))):
#            for v in ModelData.dictTetrahedrons[tid].get_vids():
#                if v not in [edge[0], edge[1], vert]:
#                    if circle_tetfid_by_vertex(tid, [v, edge[0]], vert, tetList):
#                        return True
#                    elif circle_tetfid_by_vertex(tid, [v, edge[1]], vert, tetList):
#                        return True
#                    return False

#recursively search in the circle of dictTetrahedrons around a given edge, start from the given tetrahedron and the face (edge, vert); 
#end up with the boundary face or the fixed face
#INPUT: tet is the id of tetrahedron, edge is [vert1, vert2], vert is the id of vertex which indicates the direction
#OUTPUT: tetList is a list of ids of tetrahedron on the trace
#RETURN: True reach the bounday face, False blocked by a fixed face
def find_tetpath_by_edge(tet, edge, vert, tetList):
    if tet not in tetList:
        tetList.append(tet)
        #
        #check current face
        for f in ModelData.dictFaces:
            if ModelData.dictFaces[f].is_equal_geometry(ClassFace.Class_face((edge[0], edge[1], vert))):
                if ModelData.dictFaces[f].get_tag() in (ClassFace.FIX, ClassFace.KEEP):
                    #blocked
                    return False
                elif ModelData.dictFaces[f].get_tag() == ClassFace.TMP:
                    #reached the boundary
                    return True
            
        #find the neighbouring face
        adjTets = TetraFunc.find_tetids_by_face(ClassFace.Class_face((edge[0], edge[1], vert)))
        for tid in adjTets:
            if tid not in tetList:
                #found adj tet
                for v in ModelData.dictTetrahedrons[tid].get_vids():
                    if v not in [edge[0], edge[1], vert]:
                        return find_tetpath_by_edge(tid, edge, v, tetList)
    
    #for tid in ModelData.dictTetrahedrons:
    #    if tid in tetList:
    #        continue
    #    if ModelData.dictTetrahedrons[tid].is_triangle_in_tet(ClassFace.Class_face((edge[0], edge[1], vert))):
    #        for v in ModelData.dictTetrahedrons[tid].get_vids():
    #            if v not in [edge[0], edge[1], vert]:
    #                return circle_tetfid_by_edge(tid, edge, v, tetList)

#recursively search in the circle of dictTetrahedrons around a given vertex, start from the given tetrahedron and the face (edge, vert); 
#INPUT: tet is the id of tetrahedron, edge is [vert1, vert2], vert is the id of vertex, chkTetList is the tets on the carving path which should not be passed  2016.3 fixed
#OUTPUT: tetList all the id of the visited tetrahedrons
#RETURN:
def circle_tetfid_by_vertex(tet, edge, vert, tetList, chkTetList):
    if tet not in chkTetList:
        if tet not in tetList:
            tetList.append(tet)
        #find the neighbouring face
        adjTets = TetraFunc.find_tetids_by_face(ClassFace.Class_face((edge[0], edge[1], vert)))
        for tid in adjTets:
            if tid not in tetList:
                #found adj tet
                    for v in ModelData.dictTetrahedrons[tid].get_vids():
                        if v not in [edge[0], edge[1], vert]:
                            circle_tetfid_by_vertex(tid, [v, edge[0]], vert, tetList, chkTetList)
                            circle_tetfid_by_vertex(tid, [v, edge[1]], vert, tetList, chkTetList)

#check whether vid froms a singular vertex， the method is to first check the number of fixed tets around a vertex and seen whether they are all connected after carving tetids
#INPUT: vid is the id of the vertex to be checked, tetids are the ids of a set of tetrahedra that are virtually treated as not exist
#RETURN: True means is a singular False means is not a singular
def is_singular_vertex(vid, tetids):
    #find all the incident tetrahedra of the vid expect the tetids
    allTetids = TetraFunc.find_tetids_by_vertexid(vid)
    #have to check the number of fixed tetrhedra
    onefixedTet = -1
    numFix = 0
    for t in allTetids:
        if ModelData.dictTetrahedrons[t].get_tag() in (ClassFace.FIX, ClassFace.KEEP):
            onefixedTet = t
            numFix = numFix + 1
    if numFix < 2:
        return False
    #all the rest cases should be checked whether all the fixed tetrahedra are connected
    #circlate one of the fixed tetrahedron based on the faces adjacency and exclude the carving path tetids
    visitTetids = []#all the visited tetids
    carveTetids = tetids#tet ids that should be carved
    edgeVertexList = []
    for v in ModelData.dictTetrahedrons[onefixedTet].get_vids():
        if v != vid:
            edgeVertexList.append(v)
    circle_tetfid_by_vertex(onefixedTet, [edgeVertexList[0], edgeVertexList[1]], vid, visitTetids, carveTetids)
    circle_tetfid_by_vertex(onefixedTet, [edgeVertexList[1], edgeVertexList[2]], vid, visitTetids, carveTetids )
    circle_tetfid_by_vertex(onefixedTet, [edgeVertexList[0], edgeVertexList[2]], vid, visitTetids, carveTetids )
    
    numVisitedFix = 0
    for t in visitTetids:
        if ModelData.dictTetrahedrons[t].get_tag() in (ClassFace.FIX, ClassFace.KEEP):
            numVisitedFix = numVisitedFix + 1
    if numVisitedFix == numFix:
        return False
    else:
        return True

    ##check whether all the incident tetrahedra expect the tetids are visited
    #if len(allTetids) == len(visitTetids):
    #    return False
    #else:
    #    return True

#the validity constraint Constraint1, check whether the opposite edge is on the hull surface carving is valid
#INPUT: tet is the current tetrahedron, edge is a pairs that describe the ed【ge [vert1, vert2]
#RETURN: True False means keep, False False means pass, False True means postponed, the third return value is used to carving a bunch of tets if possible
def constraint_1(tet, edge):
    if is_edge_on_boundary(edge):
        #tetrahedra along two paths
        tetList = []
        #on the boundary then check the neighbors
        #search from non fixed side of the neighbor dictFaces
        bFoundPath = False
        for v in ModelData.dictTetrahedrons[tet].get_vids():
            if v not in edge:
                tetPath = []
                if find_tetpath_by_edge(tet, edge, v, tetPath):
                    #further check whether carving the path would resulting singular vertex
                    #!IMPORTANT! new_list = old_list will assign the reference, using new_list = old_list[:] will copy the list fast
                    #!Reference! http://stackoverflow.com/questions/2612802/how-to-clone-or-copy-a-list-in-python
                    if not (is_singular_vertex(edge[0], tetPath[:]) or is_singular_vertex(edge[1], tetPath[:])):
                        tetList.append(tetPath)
        if len(tetList) == 0:
            #No path found
            return True, False, []
        elif len(tetList) == 1:
            #found one path
            return False, True, tetList[0]
        else:
            #found two path then selected the shortest one
            if len(tetList[0]) > len(tetList[1]):
                return False, True, tetList[1]
            else:
                return False, True, tetList[0]
    return False, False, []


#Not used
#recursively search in the circle of dictTetrahedrons around a given vertex, start from the given tetrahedron and the face (edge, vert); 
#end up with the boundary face or the fixed face
#INPUT: tet is the id of tetrahedron, edge is [vert1, vert2], vert is the id of vertex
#RETURN: True reach the bounday face, False blocked by a fixed face
#def find_tetpath_by_vertex(tet, edge, vert, tetList):
#
#    if tet not in tetList:
#        tetList.append(tet)
#        #check current face
#        for f in ModelData.dictFaces:
#            if ModelData.dictFaces[f].is_equal_geometry(ClassFace.Class_face((edge[0], edge[1], vert))):
#                if ModelData.dictFaces[f].get_tag() in (ClassFace.FIX, ClassFace.KEEP):
#                    #blocked
#                    return False
#                elif ModelData.dictFaces[f].get_tag() == ClassFace.TMP:
#                    #reached the boundary
#                    return True
#                else:
#                    break
#    
#        #find the neighbouring face
#        adjTets = TetraFunc.find_tetids_by_face(ClassFace.Class_face((edge[0], edge[1], vert)))
#        for tid in adjTets:
#            if tid not in tetList:
#                #found adj tet
#                 for v in ModelData.dictTetrahedrons[tid].get_vids():
#                    if v not in [edge[0], edge[1], vert]:
#                        #find the shortest carving path using dijkstra
#                        #[:] means copying rather than referencing
#                        pathTet1 = tetList[:]
#                        pathTet2 = tetList[:]
#                        bPath1 = False
#                        bPath2 = False
#                        if find_tetpath_by_vertex(tid, [v, edge[0]], vert, pathTet1):
#                            bPath1 = True
#                        if find_tetpath_by_vertex(tid, [v, edge[1]], vert, pathTet2):
#                            bPath2 = True
#                        if bPath1 == True and bPath2 == True:
#                            if len(pathTet1) > len(pathTet2):
#                                for tet in pathTet2:
#                                    if tet not in tetList:
#                                        tetList.append(tet)
#                            else:
#                                for tet in pathTet1:
#                                    if tet not in tetList:
#                                        tetList.append(tet)
#                        elif bPath1 == True:
#                            for tet in pathTet1:
#                                    if tet not in tetList:
#                                        tetList.append(tet)
#                        elif bPath2 == True:
#                            for tet in pathTet2:
#                                    if tet not in tetList:
#                                        tetList.append(tet)
#                        else:
#                            return False
#                        return True

  
#recursively search the shortest path in the sphere of dictTetrahedrons around a given vertex; 
def find_tetpath_by_Vertex_dijkstra(curTet, oppVert, CostDict, CurrentPrevDict, goalTets):
    #
    edgeVertexList = []
    for v in ModelData.dictTetrahedrons[curTet].get_vids():
        if v != oppVert:
            edgeVertexList.append(v)

    #iterate 3 edges
    for i in range(-1, 2):
        bDefined = False
        for f in ModelData.dictFaces:
            if oppVert in ModelData.dictFaces[f].get_vids():#accelarated 201709
                if ModelData.dictFaces[f].is_equal_geometry(ClassFace.Class_face((edgeVertexList[i], edgeVertexList[i+1], oppVert))):
                    bDefined = True
                    if ModelData.dictFaces[f].get_tag() in (ClassFace.FIX, ClassFace.KEEP):
                        #blocked
                        #CostDict[curTet] = 999999
                        break
                    elif ModelData.dictFaces[f].get_tag() == ClassFace.TMP:
                        #reached the boundary
                        if curTet not in goalTets:
                            goalTets.append(curTet)
                        break
        if not bDefined:
            #not defined
            #find the neighbouring tet
            adjTets = TetraFunc.find_tetids_by_face(ClassFace.Class_face((edgeVertexList[i], edgeVertexList[i+1], oppVert)))
            for nexTid in adjTets:
                if nexTid != curTet and ModelData.dictTetrahedrons[nexTid].get_tag() not in (ClassFace.FIX, ClassFace.KEEP):#added the tetrahedron check 20170904 still problematic
                    #found adj tet
                    if CostDict[nexTid] > CostDict[curTet] + 1:
                        CostDict[nexTid] = CostDict[curTet] + 1
                        CurrentPrevDict[nexTid] = curTet
                        #recursion
                        find_tetpath_by_Vertex_dijkstra(nexTid, oppVert, CostDict, CurrentPrevDict, goalTets)
        

def sub_reconstruct_path(goal, CurrentPrevDict, path):
    if CurrentPrevDict.has_key(goal):
        path.append(sub_reconstruct_path(CurrentPrevDict[goal], CurrentPrevDict, path))
        return goal

#recustruct the path for Dijkstra algorithm
def reconstruct_path(CostDict, CurrentPrevDict, goalTets):
    tetPaths = []
    if len(goalTets) > 0:
        for item in goalTets:
            path = []
            path.append(sub_reconstruct_path(item, CurrentPrevDict, path))
            path.pop(0)
            tetPaths.append(path)

        #TODO sort by length
        orderTetPaths = sorted(tetPaths, key = len)
        return orderTetPaths[0]
    else:
        return []

#the validity constraint Constraint2, check whether the opposite vertex is on the hull surface and the carving is safe
#If a carvig path exists, it should be the shortest in steps (number of tetrahedra) why?
#INPUT: tet is the id of the current candidate tetrahedron, oppVert is the id of the vertex
#RETURN: True False means keep, False False means pass, False True means postponed, the third return value is used to carving a bunch of tets if possible
def constraint_2(tet, oppVert):
#check the vertex first, whether the vertex is on the boundary or not
    if is_vertex_on_boundary(oppVert):
        #find the shortest carving path using dijkstra(may cause singular vertices on the passerby vertices)
        IncidentTetraIds = TetraFunc.find_tetids_by_vertexid(oppVert)#all the incident tetrahedra of oppvertex
        if _DEBUG:
            print("The number of incident tetrahedra of the vert is: ", len(IncidentTetraIds))
        CostDict = dict() #record the cost from the start tet to the current tet
        for id in IncidentTetraIds:
            CostDict[id] = 99999999 #infinite number
        CostDict[tet] = 0 #the cost of current tet is 0
        CurrentPrevDict = dict()#record the previous of the current tet
        CurrentPrevDict[tet] = -1
        goalTets = []
        #tranverse the path
        find_tetpath_by_Vertex_dijkstra(tet, oppVert, CostDict, CurrentPrevDict, goalTets)
        #reconstruct the path
        tetPath = reconstruct_path(CostDict, CurrentPrevDict, goalTets)
        if len(tetPath) != 0:
            #found the path
            return False, True, tetPath
        else:
            #no path found
            return True, False, []

    return False, False, []


#Not used
#def constraint_2_old(tet, oppVert):
##check the vertex first, whether the vertex is on the boundary or not
#    if is_vertex_on_boundary(oppVert):
#        tetList = []
#        #on the boundary
#        bFoundPath = False
#        edgeVertexList = []
#        for v in ModelData.dictTetrahedrons[tet].get_vids():
#            if v != oppVert:
#                edgeVertexList.append(v)
#        #find the shortest carving path using dijkstra(may cause singular vertices on the passerby vertices)
#        tetPath = []
#        if find_tetpath_by_vertex(tet, [edgeVertexList[0], edgeVertexList[1]], oppVert, tetPath):
#            #if not (is_singular_vertex(oppVert, tetPath[:])):#may cause under estimation
#                tetList.append(tetPath)
#        tetPath = []
#        if find_tetpath_by_vertex(tet, [edgeVertexList[1], edgeVertexList[2]], oppVert, tetPath):
#            #if not (is_singular_vertex(oppVert, tetPath[:])):
#                tetList.append(tetPath)
#        tetPath = []
#        if find_tetpath_by_vertex(tet, [edgeVertexList[0], edgeVertexList[2]], oppVert, tetPath):
#            #if not (is_singular_vertex(oppVert, tetPath[:])):
#                tetList.append(tetPath)
#        #
#        if len(tetList) == 0:
#            #No path found
#            return True, False, []
#        elif len(tetList) == 1:
#            #found one path
#            return False, True, tetList[0]
#        else:
#            #found more then one paths then selected the shortest one
#            pathLen = []
#            for tets in tetList:
#                pathLen.append(len(tets))
#            pathLen.sort()
#            for tets in tetList:
#                if len(tets) == pathLen[0]:
#                    return False, True, tets
#
#    return False, False, []
#Get the neighbor shell face from a shell face from the shared edge
#INPUT edge is a two tuple of vertice ids representing a edge, fid is the id of the current face
#RETURN the id of the neighbor shell face
def get_neighbor_shellface(edge, fid):
    for f in ModelData.listShellFaceIDs:
        if edge[0] in ModelData.dictFaces[f].get_vids() and edge[1] in ModelData.dictFaces[f].get_vids() and fid != f:
            return f

#check the status of an edge: whether it is the open boundary or not
#e is a two tuple of (vId1, vId2), fIds are two shell faces that share the edge
#RETURN 1 means it is an open fixed boundary (hole) 2 means a closed fixed boundary (T-junction), 0 means not a fixed boundary
def is_edge_open_fix_boundary(e, fId1, fId2):
    #a bug fixed 201709 KEEP + FIX should not return code 2 but code 1, KEEP or FIX should return 1
    numFixCount = 0
    numKeepCount = 0
    if ModelData.dictFaces[fId1].get_tag()  == ClassFace.FIX:#FIX
        numFixCount += 1
    if ModelData.dictFaces[fId2].get_tag()  == ClassFace.FIX:#FIX
        numFixCount += 1                    
    if ModelData.dictFaces[fId1].get_tag()  == ClassFace.KEEP:#KEEP
        numKeepCount += 1                   
    if ModelData.dictFaces[fId2].get_tag()  == ClassFace.KEEP:#KEEP
        numKeepCount += 1
    if numFixCount < 2:
        for f in ModelData.dictFaces:
            if f not in (fId1, fId2) and e[0] in ModelData.dictFaces[f].get_vids() and e[1] in ModelData.dictFaces[f].get_vids() \
                and ModelData.dictFaces[f].get_tag() == ClassFace.FIX:#only fix, should not use KEEP since hidden faces canbe kept 20170903
                numFixCount += 1
                if numFixCount >= 2:
                    break
    if numFixCount == 2:
        return numFixCount
    elif numFixCount > 0 or numKeepCount > 0:
        return 1
    else:
        return 0


#Recursively search the boundary shell of a given shell face by checking the coplanarity and the type of face
#INPUT: fid is the id of the current face, fNormal is the normal of the current face, listUnbounded is a list of list of unbounded face known
#OUTPUT fVisited is a list of visited shell Faces; listSeedFace is a list of coplanar seed face that is not bounded
#RETURN: False means can not found the bounded face group by fix edges, other wise return nothing
def boundary_of_coplaner_neighbors(fid, fNormal, fVisited, listUnbounded, listSeedFace):
    vertexIds = ModelData.dictFaces[fid].get_vids()
    for i in range(0, 3):
        j = 0
        if i < 2:
            j = i + 1
        #test the adjacent face
        face = get_neighbor_shellface((vertexIds[i], vertexIds[j]), fid)
        if face == None:
            fea = 999
            for f in ModelData.dictFaces:
               if vertexIds[i] in ModelData.dictFaces[f].get_vids() and vertexIds[j] in  ModelData.dictFaces[f].get_vids():
                   feafe = 9281
        #test the edge
        code = is_edge_open_fix_boundary((vertexIds[i], vertexIds[j]), fid, face)
        if code == 1:
            #is a open fixed boundary then get one unvisited face as a seed #a bug was fixed to include KEEP face
            if ModelData.dictFaces[face].get_tag() not in [ClassFace.FIX, ClassFace.KEEP] and face not in fVisited:
                #modified to distance based 20170817
                if ModelDataFuncs.is_coplanar_byDist(face, fid):
                #if TetraFunc.get_dihedral_cos_angle(ModelData.dictFaces[face].get_vids(), ModelData.dictFaces[fid].get_vids()) > SimpleMath.NeighborAngle:
                    if face not in listSeedFace:
                        listSeedFace.append(face)
        elif code == 2:
            #is a close fixed boundary
            if not globalSealConcave:
                return False
        else:
            #not a boundary
            Normal = ModelData.dictFaces[face].get_normal()
            #newVertids = ModelData.dictFaces[face].get_vids()
            #Normal = SimpleMath.get_face_normal((ModelData.dictVertices[newVertids[0]], ModelData.dictVertices[newVertids[1]], ModelData.dictVertices[newVertids[2]]))
            #if (SimpleMath.vector_length_3(Normal) > SimpleMath.Tol and abs(SimpleMath.dot_product_3(fNormal, Normal)) > SimpleMath.NeighborAngle) or \
            #    SimpleMath.vector_length_3(Normal) < SimpleMath.Tol:

            #modified to distance based 20170817
            if (SimpleMath.vector_length_3(Normal) > SimpleMath.Tol and ModelDataFuncs.is_coplanar_byDist(face, fid)) or \
                SimpleMath.vector_length_3(Normal) < SimpleMath.Tol:
                if face not in fVisited:
                    fVisited.append(face)
                    
                    if SimpleMath.vector_length_3(Normal) < SimpleMath.Tol:
                        if not boundary_of_coplaner_neighbors(face, fNormal, fVisited, listUnbounded, listSeedFace):
                            return False
                    else:
                        #note: False should be not be modified to not
                        if False == boundary_of_coplaner_neighbors(face, Normal, fVisited, listUnbounded, listSeedFace):
                            return False
                else:
                    if face in listUnbounded:
                    #if in, test if it is connected to an unbounded face
                        return False
            else:
                if face not in fVisited:
                    fVisited.append(face)
                return False

#sort a list of list of faces by size
#can be problematic if multiple groups are adjacent
def sort_facesgroup_by_size(listFaceGroup):
    listSize = []
    for list in listFaceGroup:
        bbox = ModelDataFuncs.get_bbox_faces(list)
        listSize.append(SimpleMath.square_dist_point_to_point(bbox[0], bbox[1]), list)
    listSize.sort()
    #
    listFaceGroup = []
    for list in listSize:
        listFaceGroup.append(list[1])
    return listFaceGroup

#the shape constraint Constraint3, extract the coplaner facets and tag facets based on multi-rings
#INPUT: fid is id of the shell face
#RETURN: True means have bounded coplanar faces, and those faces are also returned
def constraint_3(fid):
    #keep the current faceid, used in the last check
    curFaceID = fid
    #Get the normal of vertexList
    vertexList = ModelData.dictFaces[fid].get_vids()
    curNormal = SimpleMath.get_face_normal((ModelData.dictVertices[vertexList[0]], ModelData.dictVertices[vertexList[1]], ModelData.dictVertices[vertexList[2]]))
    if SimpleMath.vector_length_3(curNormal) > SimpleMath.Tol:
        #the list of lists of bounded faces
        listBoundedFaceGroup = []
        #all the visited faces
        listAllVisitedFids = []
        #the seed faces
        listSeedFace = []
        #the previously visited faces
        listLastVisitedFace = []
        #the Unbounded faces
        listUnboundedFaces = []
        while (fid >= 0):
            listAllVisitedFids.append(fid)
            #note: False should be not be modified to not
            if False == boundary_of_coplaner_neighbors(fid, curNormal, listAllVisitedFids, listUnboundedFaces, listSeedFace):
                #extracted the unbounded faces
                for f in listAllVisitedFids:
                    if f not in listLastVisitedFace:
                        listUnboundedFaces.append(f)
                #
                for f in listAllVisitedFids:
                    if f not in listLastVisitedFace:
                        listLastVisitedFace.append(f)
            else:
                #extracted the bounded faces
                fGrouped = []
                for f in listAllVisitedFids:
                    if f not in listLastVisitedFace:
                        fGrouped.append(f)
                listBoundedFaceGroup.append(fGrouped)
                #
                for f in listAllVisitedFids:
                    if f not in listLastVisitedFace:
                        listLastVisitedFace.append(f)
            #
            for f in listSeedFace:
                if f in listLastVisitedFace:
                    listSeedFace.remove(f)
            #
            if len(listSeedFace) > 0:
                fid = listSeedFace.pop(0)
            else:
                fid = -1
            #check the outer neigbour faces
            if fid != -1:
                vertexList = ModelData.dictFaces[fid].get_vids()
                curNormal = SimpleMath.get_face_normal((ModelData.dictVertices[vertexList[0]], ModelData.dictVertices[vertexList[1]], ModelData.dictVertices[vertexList[2]]))
             
        # a bug fixed 20170904, BoundedFace group may be not belong to the current Tetrahedron
        bBound = False
        for fg in listBoundedFaceGroup:
            if curFaceID in fg:
                bBound = True
                break
        if bBound:
            if len(listBoundedFaceGroup) > 1:
                #TODO: find the nesting order of groups
                #now keep them all
                print ('Warning: Merging coplanar face groups\n')
                listKeepFace = []
                for iGroup in listBoundedFaceGroup:
                    listKeepFace += iGroup
                #reporder the group by nesting order
                #listFaceGroup = sort_facesgroup_by_size(listFaceGroup)
                ##extact the faces to be kept
                #listKeepFace = []
                #if len(listFaceGroup) % 2 == 0:
                #    #the odd groups should be kept
                #    listFaceGroup = listFaceGroup[1::2]
                #    for iGroup in listFaceGroup:
                #        listKeepFace += listFaceGroup[iGroup]
                #else:
                #    #the even groups should be kept
                #    listFaceGroup = listFaceGroup[0::2]
                #    for iGroup in listFaceGroup:
                #        listKeepFace += listFaceGroup[iGroup]
                #keep all the tetrahedra
                return bBound, listKeepFace, listUnboundedFaces
            elif len(listBoundedFaceGroup) == 1:
                #keep all the tetrahedra
                return bBound, listBoundedFaceGroup[0], listUnboundedFaces
        else:
            return bBound, [], listUnboundedFaces

    else:
        print ('Degeneracy!')
        return False, [], []



#carving the dictTetrahedrons recorded in the ModelData
def heuristic_tet_carving():
    print("----Statistic all the face normals----")
    dictPrincipleNormal = dict()
    for f in ModelData.dictFaces:
        normal = ModelData.dictFaces[f].get_normal()
        nnormal = tuple(SimpleMath.tuple_numproduct(-1, normal))#invert the normal
        if dictPrincipleNormal.has_key(normal) or dictPrincipleNormal.has_key(nnormal):
            if dictPrincipleNormal.has_key(normal):
                dictPrincipleNormal[normal] += 1
            if dictPrincipleNormal.has_key(nnormal):
                dictPrincipleNormal[nnormal] += 1
        else:
            #test the angle with TOL
            findCopplanar = False
            for key in dictPrincipleNormal:
                if abs(SimpleMath.dot_product_3(normal, key)) > SimpleMath.NeighborAngle:
                    # approx. coplaner
                    dictPrincipleNormal[key] += 1
                    findCopplanar = True
                    break
            if not findCopplanar:
                dictPrincipleNormal[normal] = 1
    ModelData.listPrincipleNormal = sorted(dictPrincipleNormal.items(), key = operator.itemgetter(1), reverse = True)
    ModelData.listPrincipleNormal = ModelData.listPrincipleNormal[0:3]#select the first x directions

    print("----Heuristic shrinking-wrapping----")
    #keep all the tetrahedra that have fix facets on the shell note the flat tetrahedra
    #bdebug = -9999
    for fId in ModelData.listShellFaceIDs:
        tetId = TetraFunc.find_tetids_by_faceid(fId, 1)
        #initate the level values of candidate tetrahedra
        ModelData.dictTetrahedrons[tetId[0]].set_level(1)
        #note the kept tetrahedron should not be flat
        if ModelData.dictFaces[fId].get_tag() == ClassFace.FIX:
            #tiny faces may errouneously keep a tetrahedron
            keep_tetrahedron(tetId[0], TetraFunc.get_faceids_from_tetid_fast(tetId[0]))
            #ModelDataFuncs.writer_obj(ModelData.strInputFileName + '\\' + str(bdebug) + "_CARVE_.obj")
            #bdebug = bdebug + 1
            #if bdebug == -9988:
            #    fewwe = 9999

    #count
    numCount = 1

    if globalOutputLog:
        #write the sequence to a file
        f_logfile = file("log.txt", 'w')
    if globalOutputGlobalSTA:
        f_stafile = file("sta.txt", 'w')

    #initiate Stack and lists
    if not globalOutputGlobalSTA:
       sortedTetIDStack = update_stack()
    else:
       sortedTetIDStack = update_stack_ex()
    


    #heruistic carving
    while len(sortedTetIDStack) > 0:
        
        #output all the statistics
        if globalOutputGlobalSTA:
            f_stafile.write(str(len(sortedTetIDStack)))
            f_stafile.write(str(len(ModelData.dictTetrahedrons)) + "\n")
            for item in sortedTetIDStack:
                f_stafile.write(str(item))

        #pop the first not fix element of stack if possible
        curTet = sortedTetIDStack.pop(0)
        curTetId = curTet[0]
        #print str(curTetId) + '\n'
        print str(curTet[6]) + '\n'
        if globalOutputLog:
            f_logfile.write("\n")
            f_logfile.write("\n")
            f_logfile.write(str(len(ModelData.dictTetrahedrons)) + "\n")
            f_logfile.write('TetId: ' + str(curTet[0]) +' Tag: ' + str(curTet[3]) +' Dof: ' + str(curTet[4]) + ' OTHER: ' + str(curTet[6]) + '\n')

        #fetch all the shellFaces (indices) from a given Tet
        shellFaceIDsInCurTet = curTet[1]
        #fetch all the dictFaces (indices) from a given Tet
        faceIDsInCurTet = curTet[2]

        #classify the tetrahedron
        numTMP = len(shellFaceIDsInCurTet)#equal to the no. of faces on the shell
        numFIX = 0
        for fid in faceIDsInCurTet:
            if ModelData.dictFaces[fid].get_tag() == ClassFace.FIX:
                numFIX += 1
        numKEEP = len(faceIDsInCurTet) - numTMP - numFIX#keep face is not constrainted as fixed ones
        numPRESERV = numFIX + numKEEP
        #test by a set of constraints
        bStop = False
        bPostponed = False
        carveTetList = [] #for infinite tetehedra
        keepFaceList = [] #for coplanar bounded facets
        unboundFaceList = [] #for coplanar unbouned facets

        # new code
        #if numFIX == 0 and numTMP == 1:
        #    #constraint3
        #    if constraintsCtrl['Constraint3'] and not bStop:
        #        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[0])
        #elif numFIX == 1 and numTMP == 3:
        #    #constraint5
        #    if constraintsCtrl['Constraint5'] and not bStop:
        #            bStop = constraint_5(curTetId, faceIDsInCurTet)
        #    #check all faces with constraint 3 not needed in theory (flat tetrahedra)
        #    if constraintsCtrl['Constraint3'] and not bStop:
        #        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[0])
        #    if constraintsCtrl['Constraint3'] and not bStop:
        #        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[1])
        #    if constraintsCtrl['Constraint3'] and not bStop:
        #        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[2])
        #elif numFIX in (1, 2) and numTMP == 2:
        #    #c1 5
        #    if constraintsCtrl['Constraint5'] and not bStop:
        #            bStop = constraint_5(curTetId, faceIDsInCurTet)

        #    if constraintsCtrl['Constraint1'] and not bStop:
        #        #extract the opposite edge
        #        eList = []
        #        for i in shellFaceIDsInCurTet:
        #            for j in range(0, 3):
        #                if ModelData.dictFaces[i].get_vids()[j] not in eList:
        #                    eList.append(ModelData.dictFaces[i].get_vids()[j])
        #                else:
        #                    eList.remove(ModelData.dictFaces[i].get_vids()[j])
        #    
        #        if not bStop:
        #            bStop, bPostponed, carveTetList = constraint_1(curTetId, eList)
        #    
        #    #check all faces with constraint 3 not needed in theory (flat tetrahedra)
        #    if constraintsCtrl['Constraint3'] and not bStop:
        #        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[0])
        #    if constraintsCtrl['Constraint3'] and not bStop:
        #        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[1])
        #elif numFIX in (1, 2, 3) and numTMP == 1:
        #    #c1 2 3 5
        #    #constraint5
        #    if constraintsCtrl['Constraint5'] and not bStop:
        #        bStop = constraint_5(curTetId, faceIDsInCurTet)
        #   
        #    #constraint3
        #    if constraintsCtrl['Constraint3'] and not bStop:
        #        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[0])

        #    if (constraintsCtrl['Constraint2'] or constraintsCtrl['Constraint1']) and not bStop:
        #        #extract the candidate face, the opposite edge list (three) the and opposite vert
        #        tmpFace = shellFaceIDsInCurTet[0]
        #        #the opposite vertex
        #        oppVert = -1
        #        #the opposite edge list
        #        eList = []
        #        for v in ModelData.dictTetrahedrons[curTetId].get_vids():
        #            if v not in ModelData.dictFaces[tmpFace].get_vids():
        #                oppVert = v
        #                if numFIX == 1:
        #                    #only two edges
        #                    fixFace = list(set(faceIDsInCurTet) - set(shellFaceIDsInCurTet))
        #                    for v_1 in ModelData.dictFaces[fixFace[0]].get_vids():
        #                        if v_1 != oppVert:
        #                            eList.append((v, v_1))
        #                else:
        #                    #three edges
        #                    for n in ModelData.dictFaces[tmpFace].get_vids():
        #                        eList.append((v, n))
        #                break
        #        #check with constraints 1 2
        #        #2
        #        if constraintsCtrl['Constraint2'] and not bStop:
        #            bStop, bPostponed, carveTetList = constraint_2(curTetId, oppVert)
        #        #1
        #        if numFIX == 1:
        #            #two edges
        #            if constraintsCtrl['Constraint1'] and not bStop:
        #                bStop, bPostponed, carveTetList = constraint_1(curTetId, eList[0])
        #            if constraintsCtrl['Constraint1'] and not bStop:
        #                bStop, bPostponed, carveTetList = constraint_1(curTetId, eList[1])
        #        else:
        #            #three edges
        #            if constraintsCtrl['Constraint1'] and not bStop:
        #                bStop, bPostponed, carveTetList = constraint_1(curTetId, eList[0])
        #            if constraintsCtrl['Constraint1'] and not bStop:
        #                bStop, bPostponed, carveTetList = constraint_1(curTetId, eList[1])
        #            if constraintsCtrl['Constraint1'] and not bStop:
        #                bStop, bPostponed, carveTetList = constraint_1(curTetId, eList[2])
        #elif numFIX == 0:
        #    #check all faces with constraint 3 not needed in theory (flat tetrahedra)
        #    if constraintsCtrl['Constraint3'] and not bStop:
        #        for fID in shellFaceIDsInCurTet:
        #            bStop, keepFaceList, unboundFaceList = constraint_3(fID)
        
        if numTMP ==4:
            print ('Isolated tetrahedron')
        elif numTMP == 3:
            if _DEBUG:
                print "numbTMP==3"
            #check with constraints 5
            if numFIX == 1:
                if constraintsCtrl['Constraint5'] and not bStop and not bPostponed:
                    bStop = constraint_5(curTetId, faceIDsInCurTet)
            elif numFIX == 0:
                #check all faces with constraint 3 not needed in theory
                if constraintsCtrl['Constraint3Ex']:
                    if constraintsCtrl['Constraint3'] and not bStop:
                        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[0])
                    if constraintsCtrl['Constraint3'] and not bStop:
                        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[1])
                    if constraintsCtrl['Constraint3'] and not bStop:
                        bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[2])
        elif numTMP == 2:
            if _DEBUG:
                print "numbTMP==2"
            if constraintsCtrl['Constraint1']:
                #extract the opposite edge
                eList = []
                for i in shellFaceIDsInCurTet:
                    for j in range(0, 3):
                        if ModelData.dictFaces[i].get_vids()[j] not in eList:
                            eList.append(ModelData.dictFaces[i].get_vids()[j])
                        else:
                            eList.remove(ModelData.dictFaces[i].get_vids()[j])
                
                #1
                if constraintsCtrl['Constraint1'] and not bStop and not bPostponed:
                    bStop, bPostponed, carveTetList = constraint_1(curTetId, eList)

            #5
            if numFIX != 0:
                #if constraintsCtrl['Constraint5'] and not bStop and not bPostponed:
                if constraintsCtrl['Constraint5'] and not bStop:
                    bStop = constraint_5(curTetId, faceIDsInCurTet)
                
            #check with constraint 3 (first check the dihedral angle)
            if constraintsCtrl['Constraint3'] and not bStop and not bPostponed and \
                SimpleMath.dot_product_3(ModelData.dictFaces[shellFaceIDsInCurTet[0]].get_normal(), ModelData.dictFaces[shellFaceIDsInCurTet[1]].get_normal())\
                > SimpleMath.NeighborAngle:
                if ModelDataFuncs.is_coplanar_byDist(shellFaceIDsInCurTet[0], shellFaceIDsInCurTet[1]):
                    print ('true flat tetrahedron!')

                #abs(TetraFunc.get_dihedral_cos_angle(ModelData.dictFaces[shellFaceIDsInCurTet[0]].get_vids(), \
                #ModelData.dictFaces[shellFaceIDsInCurTet[1]].get_vids())) > SimpleMath.NeighborAngle:
                    print ('Flat tetrahedron!')
            #check both faces with constraint 3 not needed in theory
            if constraintsCtrl['Constraint3Ex']:
                if constraintsCtrl['Constraint3'] and not bStop:
                    bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[0])
                if constraintsCtrl['Constraint3'] and not bStop:
                    bStop, keepFaceList, unboundFaceList = constraint_3(shellFaceIDsInCurTet[1])

        elif numTMP == 1:
            if _DEBUG:
                print "numbTMP==1"
             #extract the candidate face, the opposite edge list (three) the and opposite vert
            tmpFace = shellFaceIDsInCurTet[0]
            #the opposite vertex
            oppVert = -1
            #the opposite edge list
            eList = []
            for v in ModelData.dictTetrahedrons[curTetId].get_vids():
                if v not in ModelData.dictFaces[tmpFace].get_vids():
                    oppVert = v
                    for n in ModelData.dictFaces[tmpFace].get_vids():
                        eList.append((v, n))
                    break

            if constraintsCtrl['Constraint2'] or constraintsCtrl['Constraint1']:
                #check with constraints 1 2 3 5
                #2
                if constraintsCtrl['Constraint2'] and not bStop and not bPostponed:
                    bStop, bPostponed, carveTetList = constraint_2(curTetId, oppVert)
                #1
                if constraintsCtrl['Constraint1'] and not bStop and not bPostponed:
                    bStop, bPostponed, carveTetList = constraint_1(curTetId, eList[0])
                if constraintsCtrl['Constraint1'] and not bStop and not bPostponed:
                    bStop, bPostponed, carveTetList = constraint_1(curTetId, eList[1])
                if constraintsCtrl['Constraint1'] and not bStop and not bPostponed:
                    bStop, bPostponed, carveTetList = constraint_1(curTetId, eList[2])
              
            #Constraint2 is problematic somehow todo 20170904
            if numFIX != 0 and constraintsCtrl['Constraint5'] and not bStop:
            #if numFIX != 0 and constraintsCtrl['Constraint5'] and not bStop and not bPostponed:
               #5
                bStop = constraint_5(curTetId, faceIDsInCurTet)   
               
            #3
            #if numFIX != 3 and constraintsCtrl['Constraint3'] and not bStop and not bPostponed:
            if numFIX != 3 and constraintsCtrl['Constraint3'] and not bStop:
                bStop, keepFaceListt, unboundFaceList = constraint_3(tmpFace)
        else:
            print("Isolated Tetrahedron!", numTMP, numFIX)
            #raise Exception
        
            #added 20170818
        #if curTet[5] == 1:
        #    bStop = False
        #    #degenercy
        #    if (numTMP >= 3 and numFIX == 1) or\
        #       (numTMP == 2 and numFIX == 2) or\
        #       (numTMP == 1 and numFIX == 3):
        #        if bStop == True:
        #            bStop = False
        #            print("flat tetrahedron forcely caved ")
   
        #manipulate the tetrahedron
        numTet = len(ModelData.dictTetrahedrons)
        if bStop:
            #keep
            if len(keepFaceList) != 0:
                #keep a bunch of "coplanar" tetrehedra
                for faceId in keepFaceList:
                    tetId = TetraFunc.find_tetids_by_faceid(faceId, 1)
                    if tetId != []:
                        keep_tetrahedron(tetId[0], TetraFunc.get_faceids_from_tetid_fast(tetId[0]))
                #carve a bunch of "coplanar" unbounded tetrehedra
                if len(unboundFaceList) != 0:
                    for faceId in unboundFaceList:
                        tetId = TetraFunc.find_tetids_by_faceid(faceId, 1)
                        if tetId != []:
                            carve_tetrahedron(tetId[0], TetraFunc.get_faceids_from_tetid_fast(tetId[0]))
            else:
                #keep
                keep_tetrahedron(curTetId, faceIDsInCurTet)
        else:
            #carve or postpone
            if not bPostponed:
                #Carve
                carve_tetrahedron(curTetId, faceIDsInCurTet)
                #in case other keptable face are detected
                if len(keepFaceList) != 0:
                    #keep a bunch of "coplanar" tetrehedra
                    for faceId in keepFaceList:
                        tetId = TetraFunc.find_tetids_by_faceid(faceId, 1)
                        keep_tetrahedron(tetId[0], TetraFunc.get_faceids_from_tetid_fast(tetId[0]))
            else:
                #postpone (modified)
                if ModelData.dictTetrahedrons[curTetId].get_tag() == ClassFace.DEL:#(modified)
                    #carve_tetrahedron(curTetId, TetraFunc.get_faceids_from_tetid(curTetId))
                    #all the tetrehedra are infinite (DEL)
                    for tetId in carveTetList:
                        #carve a bunch of tetrahedra
                        carve_tetrahedron(tetId, TetraFunc.get_faceids_from_tetid_fast(tetId))
                else:#(modified)
                    #postphone the tetrahedron
                    ModelData.dictTetrahedrons[curTetId].set_tag(ClassFace.DEL)#(modified)

        #Update the dictFaces
        ModelDataFuncs.remove_faces()
        #Update the stack and lists
        if not globalOutputGlobalSTA:
            sortedTetIDStack = update_stack()
        else:
            sortedTetIDStack = update_stack_ex()

        #Output intermediate results
        #if not bStop:
        numCount += 1
        if numCount == 250:
              stoppp= True
        #if globalOutputCarve and numTet > len(ModelData.dictTetrahedrons) and not bStop and numCount % globalOutputFreq == 0: #write out all the carved cases
        if globalOutputCarve and numCount % globalOutputFreq == 0:#write out all steps for debuging
            if not os.path.exists(ModelData.strInputFileName + "\\"):
                os.makedirs(ModelData.strInputFileName + "\\")
            ModelDataFuncs.writer_obj(ModelData.strInputFileName + '\\' + str(numCount) + "_CARVE_.obj")
    if globalOutputLog:
        #end the log file      
        f_logfile.close()


        