import os, sys, types
import ModelData, ModelDataFuncs, DecomposeFunc, TetraFunc, CarveFunc

#sys.path.append("..\\..\\obj2poly\obj2poly/")
sys.path.append("D:\\JohnGitHub\\mySVN\\obj2poly\\obj2poly\\")
from ConvProvider import ConvProvider

MIDFILEPATH = "tmpRepairShrink.obj"

#start the repair procedure
#isSemantic is equal to True means the semantics should be handled
#debugControl is used to debug
def do_the_work(inputFilePath, isSemantic, debugControl):

    #Init mid files
    if os.path.exists(MIDFILEPATH):
        os.remove(MIDFILEPATH)

    #Init datastructure
    ModelDataFuncs.Init()
    ModelData.strInputFileName, ext = os.path.splitext(inputFilePath)

    #read file
    print ("----Processing file----")
    print (inputFilePath)
    if isSemantic == True:
        if os.path.splitext(inputFilePath)[1] == '.obj':
            print('WARNING: obj format does not contain semantics')
            print('Semantics will be deduced')
            print ("Check and tessellate the file...")
            #MyCov = ConvProvider()
            #MyCov.convert(inputFilePath, MIDFILEPATH, True)
            ##read a tesselated objfile    
            #if ModelDataFuncs.reader_obj(MIDFILEPATH) == False:
            #    raise Exception
            if ModelDataFuncs.reader_obj(inputFilePath) == False:
                raise Exception
        else:
            #poly with semantics
            try:
                if not ModelDataFuncs.reader_poly_with_semantics(inputFilePath):
                    return
            except:
                raise ImportError
    else:
        #preprocess (convert and tessellation)
        print ("Check and tessellate the file...")
        MyCov = ConvProvider()
        MyCov.convert(inputFilePath, MIDFILEPATH, True)
        #read a tesselated objfile    
        if ModelDataFuncs.reader_obj(MIDFILEPATH) == False:
            raise Exception
    #invert the normal of the input model
    if ModelData.global_INVERT_NORMAL:
        ModelDataFuncs.invert_poly_normal()
    #only for debug
    #tmp = ModelData.centerVertex
    #ModelData.centerVertex = (0.0, 0.0, 0.0)
    #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_CLS.obj")
    #ModelData.centerVertex = tmp
    #


    if int(debugControl) == 1:
        print("Mode 1 start...\n")
        #Decomposit all the triangles%
        DecomposeFunc.model_decompositionEx() 

        #Merge all the coplaner dictFaces
        #coplaner_face_merge()
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_DEC.obj")

    elif int(debugControl) == 2:
        print("Mode 2 start...\n")
        #Constrained Tetrahedralization
        if False == TetraFunc.CDT():
            print("Constrained Delauney Tetrahedralization FAILED!")
            return

        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_CDT.obj")

        #Heuristic carving
        CarveFunc.heuristic_tet_carving()
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_CARVE.obj")

        #Reconstruct the mesh from tetrahedron
        TetraFunc.extract_mesh_from_tet(isSemantic)
        #Output
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT.obj")
        if isSemantic:
            ModelDataFuncs.writer_poly_with_semantics(ModelData.strInputFileName + "_OUTPUT.poly")
    elif int(debugControl) == 3:
        print("Mode 3 start...\n")
        #only deduce the semantics
        TetraFunc.deduce_semantics_of_poly(isSemantic)
        ModelDataFuncs.writer_poly_with_semantics(ModelData.strInputFileName + "_OUTPUT.poly")
    elif int(debugControl) == 4:
        print("Mode 4 comparison mode start...\n")

        #Constrained Tetrahedralization
        if False == TetraFunc.CDT():
            print("Constrained Delauney Tetrahedralization FAILED!")
            return
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_CDT.obj")

        #####copy datacopy
        ModelDataFuncs.preserveModelData()


        #switches = [('dof',0), ('deg', 0), ('volume',0), ('flatness',0),('depth',0),  ('distanceToCenter',1), ('directions',0), ('area' ,0), ('level' ,0), ('curvature',0)]
        print CarveFunc.globalHeuristic
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_none.obj")

        #different combinations
        #dof
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['dof'] = 1
        print CarveFunc.globalHeuristic
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof.obj")
        #dof+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        print CarveFunc.globalHeuristic
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_deg.obj")
        CarveFunc.globalHeuristic['deg'] = 0
        #dof+volume
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['volume'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_vol.obj")
        #dof+volume+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_vol_deg.obj")
        CarveFunc.globalHeuristic['volume'] = 0
        CarveFunc.globalHeuristic['deg'] = 0
        #dof+flatness
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['flatness'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_flat.obj")
        #dof+flatness+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_flat_deg.obj")
        CarveFunc.globalHeuristic['flatness'] = 0
        CarveFunc.globalHeuristic['deg'] = 0
        #dof+depth
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['depth'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_depth.obj")
        #dof+depth+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_depth_deg.obj")
        CarveFunc.globalHeuristic['depth'] = 0
        CarveFunc.globalHeuristic['deg'] = 0
        #dof+distant
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['distanceToCenter'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_dist.obj")
        #dof+distant+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_dist_deg.obj")
        CarveFunc.globalHeuristic['distanceToCenter'] = 0
        CarveFunc.globalHeuristic['deg'] = 0
        #dof+direction
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['direction'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_direction.obj")
        #dof+direction+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_direction_deg.obj")
        CarveFunc.globalHeuristic['direction'] = 0
        CarveFunc.globalHeuristic['deg'] = 0
        #dof+area
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['area'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_area.obj")
        #dof+area+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_area_deg.obj")
        CarveFunc.globalHeuristic['area'] = 0
        CarveFunc.globalHeuristic['deg'] = 0
        #dof+level
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['level'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_level.obj")
        #dof+level+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_level_deg.obj")
        CarveFunc.globalHeuristic['level'] = 0
        CarveFunc.globalHeuristic['deg'] = 0
        #dof+curvature
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['curvature'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_curve.obj")
        #dof+curvature+deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_curve_deg.obj")
        CarveFunc.globalHeuristic['curvature'] = 0
        CarveFunc.globalHeuristic['deg'] = 0
       
        CarveFunc.globalHeuristic['dof'] = 0
        #deg
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['deg'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_deg.obj")
        CarveFunc.globalHeuristic['deg'] = 0
        #vloume
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['volume'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_vol.obj")
        CarveFunc.globalHeuristic['volume'] = 0
        #flatness
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['flatness'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_flat.obj")
        CarveFunc.globalHeuristic['flatness'] = 0
        #depth
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['depth'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_depth.obj")
        CarveFunc.globalHeuristic['depth'] = 0
        #distant
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['distanceToCenter'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist.obj")
        CarveFunc.globalHeuristic['distanceToCenter'] = 0
        #direction
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['direction'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_direction.obj")
        CarveFunc.globalHeuristic['direction'] = 0
        #area
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['area'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_area.obj")
        CarveFunc.globalHeuristic['area'] = 0
        #level
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['level'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level.obj")
        CarveFunc.globalHeuristic['level'] = 0
        #curvature
        ModelDataFuncs. restoreModelData()
        CarveFunc.globalHeuristic['curvature'] = 1
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_curve.obj")
        CarveFunc.globalHeuristic['curvature'] = 0

    elif int(debugControl) == 5:
        print("Mode 5 new comparison mode start...\n")
        
        #Constrained Tetrahedralization
        if False == TetraFunc.CDT():
            print("Constrained Delauney Tetrahedralization FAILED!")
            return
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_CDT.obj")

        #####copy datacopy
        ModelDataFuncs.preserveModelData()
        CarveFunc.globalOutputGlobalSTA = True

        #switches = [('dof',0), ('deg', 0), ('volume',0), ('flatness',0),('depth',0),  ('distanceToCenter',1), ('directions',0), ('area' ,0), ('level' ,0), ('curvature',0)]

        #already generated in mode 4 thus commented

        #None
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_none.obj")
        ##dof
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['dof']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof.obj")
        # #deg
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['deg']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_deg.obj")
        ##vloume
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['vol']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_vol.obj")
        ##flatness
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['flatness']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_flat.obj")
        ##depth
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['depth']     
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_depth.obj")
        ##distant
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['distanceToCenter']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist.obj")
        #        #direction
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['direction']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_direction.obj")
        ##area
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['area']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_area.obj")
        ##level
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['level']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level.obj")
        ##curvature
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.indicators = ['curvature']
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_curve.obj")
        #different combinations including some results from mode 4
        #
        #combinations
        CarveFunc.indicators = [ 'level', 'volume']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_vol.obj")

        CarveFunc.indicators = [ 'level', 'area']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_area.obj")

        CarveFunc.indicators = [ 'level', 'flatness']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_flat.obj")
        CarveFunc.indicators = [ 'level', 'depth']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_depth.obj")
        CarveFunc.indicators = [ 'level', 'curvature']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_curve.obj")
        CarveFunc.indicators = [ 'level', 'dof']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_dof.obj")

        CarveFunc.indicators = [ 'directions', 'volume']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_vol.obj")
        CarveFunc.indicators = [ 'directions', 'area']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_area.obj")
        CarveFunc.indicators = [ 'directions', 'flatness']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_flat.obj")
        CarveFunc.indicators = [ 'directions', 'depth']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_depth.obj")
        CarveFunc.indicators = [ 'directions', 'curvature']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_curve.obj")
        CarveFunc.indicators = [ 'directions', 'dof']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_dof.obj")

        CarveFunc.indicators = [ 'distanceToCenter', 'volume']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_vol.obj")
        CarveFunc.indicators = [ 'distanceToCenter', 'area']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_area.obj")
        CarveFunc.indicators = [ 'distanceToCenter', 'flatness']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_flat.obj")
        CarveFunc.indicators = [ 'distanceToCenter', 'depth']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_depth.obj")
        CarveFunc.indicators = [ 'distanceToCenter', 'curvature']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_curve.obj")
        CarveFunc.indicators = [ 'distanceToCenter', 'dof']
        ModelDataFuncs. restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_dof.obj")

        ##complex comninations
        #CarveFunc.indicators = ['dof', 'level', 'volume']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_level_vol.obj")

        #CarveFunc.indicators = ['dof', 'level', 'area']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_level_area.obj")

        #CarveFunc.indicators = ['dof', 'level', 'flatness']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_level_flat.obj")
        #CarveFunc.indicators = ['dof', 'level', 'depth']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_level_depth.obj")
        #CarveFunc.indicators = ['dof', 'level', 'curvature']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_level_curve.obj")

        #CarveFunc.indicators = ['dof', 'directions', 'volume']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_directions_vol.obj")
        #CarveFunc.indicators = ['dof', 'directions', 'area']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_directions_area.obj")
        #CarveFunc.indicators = ['dof', 'directions', 'flatness']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_directions_flat.obj")
        #CarveFunc.indicators = ['dof', 'directions', 'depth']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_directions_depth.obj")
        #CarveFunc.indicators = ['dof', 'directions', 'curvature']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_directions_curve.obj")

        #CarveFunc.indicators = ['dof', 'distanceToCenter', 'volume']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_dist_vol.obj")
        #CarveFunc.indicators = ['dof', 'distanceToCenter', 'area']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_dist_area.obj")
        #CarveFunc.indicators = ['dof', 'distanceToCenter', 'flatness']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_dist_flat.obj")
        #CarveFunc.indicators = ['dof', 'distanceToCenter', 'depth']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_dist_depth.obj")
        #CarveFunc.indicators = ['dof', 'distanceToCenter', 'curvature']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dof_dist_curve.obj")

        #CarveFunc.indicators = ['level', 'volume',  'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_vol_dof.obj")
        #CarveFunc.indicators = ['level', 'area' , 'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_area_dof.obj")
        #CarveFunc.indicators = ['level', 'flatness', 'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_flat_dof.obj")
        #CarveFunc.indicators = ['level', 'depth', 'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_depth_dof.obj")
        #CarveFunc.indicators = ['level', 'curvature', 'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_curve_dof.obj")
                                                                    
        #CarveFunc.indicators = ['directions', 'volume','dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_vol_dof.obj")
        #CarveFunc.indicators = ['directions', 'area', 'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_area_dof.obj")
        #CarveFunc.indicators = ['directions', 'flatness','dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_flat_dof.obj")
        #CarveFunc.indicators = ['directions', 'depth', 'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_depth_dof.obj")
        #CarveFunc.indicators = ['directions', 'curvature', 'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_curve_dof.obj")
                                                                    
        #CarveFunc.indicators = ['distanceToCenter', 'volume', 'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_vol_dof.obj")
        #CarveFunc.indicators = ['distanceToCenter', 'area',  'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_area_dof.obj")
        #CarveFunc.indicators = ['distanceToCenter', 'flatness','dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_flat_dof.obj")
        #CarveFunc.indicators = ['distanceToCenter', 'depth',  'dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_depth_dof.obj")
        #CarveFunc.indicators = ['distanceToCenter', 'curvature','dof']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_curve_dof.obj")

        #CarveFunc.indicators = ['level', 'volume']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_volume.obj")
        #CarveFunc.indicators = ['level', 'area' ]
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_area.obj")
        #CarveFunc.indicators = ['level', 'flatness']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_flat.obj")
        #CarveFunc.indicators = ['level', 'depth']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_depth.obj")
        #CarveFunc.indicators = ['level', 'curvature']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level_curve.obj")
                                                                    
        #CarveFunc.indicators = ['directions', 'volume']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_volume.obj")
        #CarveFunc.indicators = ['directions', 'area']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_area.obj")
        #CarveFunc.indicators = ['directions', 'flatness']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_flat.obj")
        #CarveFunc.indicators = ['directions', 'depth']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_depth.obj")
        #CarveFunc.indicators = ['directions', 'curvature']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_directions_curve.obj")
                                                                    
        #CarveFunc.indicators = ['distanceToCenter', 'volume']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_volume.obj")
        #CarveFunc.indicators = ['distanceToCenter', 'area']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_area.obj")
        #CarveFunc.indicators = ['distanceToCenter', 'flatness']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_flat.obj")
        #CarveFunc.indicators = ['distanceToCenter', 'depth']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_depth.obj")
        #CarveFunc.indicators = ['distanceToCenter', 'curvature']
        #ModelDataFuncs. restoreModelData()
        #CarveFunc.heuristic_tet_carving()
        #TetraFunc.extract_mesh_from_tet(isSemantic)
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist_curve.obj")
    elif int(debugControl) == 6:
        print("Mode 6 verify mode start...\n")
         #Constrained Tetrahedralization
        if False == TetraFunc.CDT():
            print("Constrained Delauney Tetrahedralization FAILED!")
            return
        #ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_CDT.obj")

        #####copy datacopy
        ModelDataFuncs.preserveModelData()
        CarveFunc.globalOutputGlobalSTA = True
        CarveFunc.indicators = [ 'level']
        ModelDataFuncs.restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_level.obj")

         #####copy datacopy
        CarveFunc.globalOutputGlobalSTA = True
        CarveFunc.indicators = [ 'distanceToCenter']
        ModelDataFuncs.restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_dist.obj")

         #####copy datacopy
        CarveFunc.globalOutputGlobalSTA = True
        CarveFunc.indicators = [ 'directions']
        ModelDataFuncs.restoreModelData()
        CarveFunc.heuristic_tet_carving()
        TetraFunc.extract_mesh_from_tet(isSemantic)
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_OUTPUT_direction.obj")

    elif int(debugControl) == 7 and isSemantic:
        print("Mode7 deduce semantic mode start...\n")
         #Constrained Tetrahedralization
        TetraFunc.deduce_semantics_of_poly(isSemantic)
        ModelDataFuncs.writer_poly_with_semantics(ModelData.strInputFileName + "_OUTPUT.poly")

    else:
        print("Full start...\n")
        #Decomposit all the triangles
        DecomposeFunc.model_decompositionEx() 

        #Merge all the coplaner dictFaces
        #coplaner_face_merge()
        ModelDataFuncs.writer_obj(ModelData.strInputFileName +"_DEC.obj")

        #Constrained Tetrahedralization
        if False == TetraFunc.CDT():
            print("Constrained Delauney Tetrahedralization FAILED!")
            return
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_CDT.obj")

        #Heuristic carving
        CarveFunc.heuristic_tet_carving()
        ModelDataFuncs.writer_obj(ModelData.strInputFileName+"_CARVE.obj")

        #Reconstruct the mesh from tetrahedron
        TetraFunc.extract_mesh_from_tet(isSemantic)
        #Output
        ModelDataFuncs.writer_obj(ModelData.strInputFileName + "_OUTPUT.obj")
        if isSemantic:
            ModelDataFuncs.writer_poly_with_semantics(ModelData.strInputFileName + "_OUTPUT.poly")

    #Move the results to another folder
        #filepath, filename=os.path.split(sys.argv[1])
        #filepath = os.path.join(filepath, "res_tr1_with_tiny")
        #filepath = "C:\\Users\\John\\Desktop\\rotterdam\\3-28-Witte_Dorp\\obj\\res_tr1_del_tiny\\"
        #if not os.path.exists(filepath):
        #    os.mkdir(filepath)
        #os.rename(inputFilePath, filepath + inputFilePath)
        #os.rename(inputFilePath + "_OUTPUT.obj", filepath + inputFilePath + "_OUTPUT.obj")
        #os.rename(inputFilePath + "_DEC.obj", filepath + inputFilePath + "_DEC.obj")

def Main():

    if len(sys.argv) < 2:
        print (
        '''Usage of RepairShrink:
           Python RepairShrink.py MODELFILEPATH(.obj|.poly) (-s) debugControl
           Note: obj format does not support semantics while poly format support basic semantics of CityGML''')
        sys.exit()
    
    if os.path.isdir(sys.argv[1]):
        os.chdir(sys.argv[1])
        dFiles = []
        for f in os.listdir('.'):
            fileName, fileExt = os.path.splitext(f)
            if fileExt == '.poly':
				dFiles.append(f)
            #elif fileExt == '.obj':
                #dFiles.append(f)
        if len(dFiles) == 0:
            print ('Emptry folder!')
            sys.exit()
        for fName in dFiles:
            try:
                if len(sys.argv) == 4:
                    if sys.argv[2] == '-s':
                        do_the_work(fName, True, sys.argv[3])
                    else:
                        do_the_work(fName, False, sys.argv[3])
                elif len(sys.argv) == 3:
                    do_the_work(fName, False, sys.argv[2])
                elif len(sys.argv) == 2:
                    do_the_work(fName, False, 0)

            except ValueError:
                print("{} has a problem").format(fName)
    else:
        fileName, fileExt = os.path.splitext(sys.argv[1])
        if fileExt not in ('.obj', '.poly'):
            print ("The input parameter 1 should be a OBJ or POLY file or a folder of a set of model files")
            sys.exit()
        else:
            if len(sys.argv) == 4:
                if sys.argv[2] == '-s':
                    do_the_work(sys.argv[1], True, sys.argv[3])
                else:
                    do_the_work(sys.argv[1], False, sys.argv[3])
            elif len(sys.argv) == 3:
                do_the_work(sys.argv[1], False, sys.argv[2])
            elif len(sys.argv) == 2:
                do_the_work(sys.argv[1], False, 0)


if __name__ == '__main__':
    Main()