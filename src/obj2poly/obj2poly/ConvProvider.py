import os
from os import sys
import cleanpoly
from ctypes import *
import inspect

class ConvProvider:
    def convert (self, FilePath1, FilePath2, bTessellation = False):
        
        fileName1, fileExt1 = os.path.splitext(FilePath1)
        fileName2, fileExt2 = os.path.splitext(FilePath2)
        #
        self.inputFile = FilePath1
        self.outputFile = FilePath2
        # data storage
        self.listVertices = []
        self.listFaces = []
        # semantics storage (only avaliable for poly)
        self.listFaceSemantics = []
        self.strModelID = ''
        self.isSolid = False
        #tessellation
        self.bTessellation = bTessellation
        #
        if fileExt1 == fileExt2 and bTessellation == False:
            #prevent from tessellating
            print("the same input and output")
            return
        elif fileExt1 == '.poly' and fileExt2 == '.poly':
            #conversion considering the semantics
            self.__read_semantic_poly()
            self.__write_semantic_poly()
        else:
            # data IO
            if fileExt1 == '.obj':
                self.__read_obj()
            else:
                self.__read_poly()
            if fileExt2 == '.obj':
                self.__write_obj()
            else:
                self.__write_poly()

#private members
    #read OBJ file and tessellate ()
    def __read_obj(self):
        try:
            fileObj = file(self.inputFile, 'r')
        except:
            print ("Invalide file: " + self.inputFile)
            return False
        #read vertics and dictFaces
        for line in fileObj:
            if line.startswith('v') and line[1] == ' ':
                line = line[1:-1].strip()
                self.listVertices.append(map(float, line.split(' ')))
            elif line.startswith('f') and line[1] == ' ':
                indexList = []
                #to filter out the /
                for index in line[1:-1].strip().split(' '):
                    indexList.append(index.split('/')[0])
                #tesselation for polygon (more than 3 dictVertices)
                if self.bTessellation and len(indexList) > 3:
                    #workaround
                    curDirBefore = os.getcwd() 
                    path = os.path.dirname(os.path.realpath(__file__))
                    if sizeof(c_voidp) == 4:
                        path = os.path.join(path, 'x32')
                        os.chdir(path)
                        Tessellator = CDLL('tesselatorInterface.dll')
                    elif sizeof(c_voidp) == 8:
                        #workaround 
                        path = os.path.join(path, 'x64')
                        os.chdir(path)
                        Tessellator = CDLL('tesselatorInterface.dll')
                    os.chdir(curDirBefore)
                    #add rings
                    ring_vert_num = len(indexList)
                    #ExtRingCoords = ((c_double * 3) * ring_vert_num)()
                    ExtRingCoords = (POINTER(c_double) * ring_vert_num)()
                    for j in range(0, ring_vert_num):
                        ExtRingCoords[j] = (c_double * 3)()
                        ExtRingCoords[j][0] = self.listVertices[int(indexList[j])-1][0]
                        ExtRingCoords[j][1] = self.listVertices[int(indexList[j])-1][1]
                        ExtRingCoords[j][2] = self.listVertices[int(indexList[j])-1][2]
                    Tessellator.AddRing(byref(ExtRingCoords), ring_vert_num, c_bool(1))
                    #compute
                    numOutputVertices = c_int(0)
                    numOutputIndices = c_int(0)
                    if Tessellator.Tessellation(byref(numOutputVertices), byref(numOutputIndices)) == c_bool(0):
                        print "Tesselation failed"
                    #output
                    coordsOutput = (POINTER(c_double) * numOutputVertices.value)()
                    for i in range(0, numOutputVertices.value):
                        coordsOutput[i] = (c_double * 3)()
                    indicesOutput = (POINTER(c_int) * numOutputIndices.value)()
                    for i in range(0, numOutputIndices.value):
                        indicesOutput[i] = (c_int * 3)()
                    #coordsOutput = (c_double * 3 * numOutputVertices.value)()
                    #indicesOutput = (c_int * 3 * numOutputIndices.value)()
                    Tessellator.Output(byref(coordsOutput), byref(indicesOutput))
                    #convert indices
                    if ring_vert_num < numOutputVertices.value:
                        print ('intersection existed')
                    elif ring_vert_num > numOutputVertices.value:
                        print ('duplicated dictVertices existed')
                    outputCoordsIndice = [] #the indices of the outputVerts
                    for j in range (0, numOutputVertices.value):
                        vert = coordsOutput[j]
                        vert = [coordsOutput[j][0], coordsOutput[j][1], coordsOutput[j][2]]
                        try:
                            k = self.listVertices.index(vert)
                        except ValueError:
                            k = len(self.listVertices)
                            self.listVertices.append(vert)
                            print ('Vertex '+ str(k) + ' added')
                        outputCoordsIndice.append(k)
                    #Add to listFaces
                    for j in range (0, numOutputIndices.value):
                        self.listFaces.append([outputCoordsIndice[indicesOutput[j][0]],outputCoordsIndice[indicesOutput[j][1]],outputCoordsIndice[indicesOutput[j][2]]])
                else:
                    #index - 1
                    indexList = [int(i)-1 for i in indexList]
                    self.listFaces.append(indexList)

        #check the content
        if self.listVertices.count == 0 or self.listFaces.count == 0:
            print "Invalid Obj file!\n"
        fileObj.close()
    #end __read_obj
    
    #read OBJ file and try to tessellate
    def __read_poly(self):
        #first clean the poly file (code from Hugo Ledoux)
        try:
            cleanpoly.CleanPoly(self.inputFile, self.inputFile + "mid")
        except:
            print ("Cleanpoly failed")
        #then
        try:
            filePoly = file(self.inputFile + "mid" , 'r')
        except:
            print ("Invalide file:" + "..\Output.polymid")
            sys.exit()
        #read
        line_list = []

        #dictVertices
        f_line = filePoly.readline()
        while f_line.startswith('#'):
            f_line = filePoly.readline()

        f_line = f_line[:-1].strip()
        line_list = f_line.split(' ')
        vert_no = int(line_list[0])
        for i in range (0, vert_no):
            line_list = []
            f_line = filePoly.readline()
            f_line = f_line[:-1].strip()
            line_list.append(map(float, f_line.split(' ')[-3:]))
            self.listVertices.append(line_list[0])

        #dictFaces
        f_line = filePoly.readline()
        line_list = []
        f_line = f_line[:-1].strip()
        line_list.append(map(int, f_line.split(' ')))
        face_no = int(line_list[0][0])
        for i in range (0, face_no):
            line_list = []
            f_line = filePoly.readline()
            f_line = f_line[:-1].strip()
            line_list = f_line.split(' ')
            ring_no = int(line_list[0][0])
            #extior ring
            line_list = []
            f_line = filePoly.readline()
            f_line = f_line[:-1].strip()
            line_list.append(map(int, f_line.split(' ')))
            #if contain holes then do triangulation
            #read rings
            if ring_no > 1:
                nTotalVerts = line_list[0][0]
                for j in range (1, ring_no):
                    #interior ring
                    f_line = filePoly.readline()
                    f_line = f_line[:-1].strip()
                    line_list.append(map(int, f_line.split(' ')))
                    nTotalVerts = nTotalVerts + line_list[j][0]
                    #hole skipped
                    f_line = filePoly.readline()
                #workaround
                curDirBefore = os.getcwd()
                path = os.path.dirname(os.path.realpath(__file__))
                if sizeof(c_voidp) == 4:
                    path = os.path.join(path, 'x32')
                    os.chdir(path)
                    Tessellator = CDLL('tesselatorInterface.dll')
                elif sizeof(c_voidp) == 8:
                    #workaround 
                    path = os.path.join(path, 'x64')
                    os.chdir(path)
                    Tessellator = CDLL('tesselatorInterface.dll')
                os.chdir(curDirBefore)
                #add rings
                #ExtRingCoords = (c_double * 3 * line_list[0][0] )()
                ExtRingCoords = (POINTER(c_double) * line_list[0][0])()
                for j in range(0, line_list[0][0]):
                    ExtRingCoords[j] = (c_double * 3)()
                    ExtRingCoords[j][0] = self.listVertices[line_list[0][j+1]][0]
                    ExtRingCoords[j][1] = self.listVertices[line_list[0][j+1]][1]
                    ExtRingCoords[j][2] = self.listVertices[line_list[0][j+1]][2]
                Tessellator.AddRing(byref(ExtRingCoords), line_list[0][0], c_bool(1))

                for j in range (0, ring_no-1):
                    #IntRingCoords = ((c_double * 3) * line_list[j+1][0])()
                    IntRingCoords = (POINTER(c_double) * line_list[j+1][0])()
                    for k in range (0, line_list[j+1][0]):
                        IntRingCoords[k] = (c_double * 3)()
                        IntRingCoords[k][0] = self.listVertices[line_list[j+1][k+1]][0]
                        IntRingCoords[k][1] = self.listVertices[line_list[j+1][k+1]][1]
                        IntRingCoords[k][2] = self.listVertices[line_list[j+1][k+1]][2]
                    Tessellator.AddRing(byref(IntRingCoords), line_list[j+1][0], c_bool(0))
                 
                #compute
                numOutputVertices = c_int(0)
                numOutputIndices = c_int(0)
                if Tessellator.Tessellation(byref(numOutputVertices), byref(numOutputIndices)) == c_bool(0):
                    print "Tesselation failed"
                #output
                #coordsOutput = (c_double * 3 * numOutputVertices.value)()
                #indicesOutput = (c_int * 3 * numOutputIndices.value)()
                coordsOutput = (POINTER(c_double) * numOutputVertices.value)()
                for i in range(0, numOutputVertices.value):
                    coordsOutput[i] = (c_double * 3)()
                indicesOutput = (POINTER(c_int) * numOutputIndices.value)()
                for i in range(0, numOutputIndices.value):
                    indicesOutput[i] = (c_int * 3)()
                Tessellator.Output(byref(coordsOutput), byref(indicesOutput))
                #convert indices
                if nTotalVerts < numOutputVertices.value:
                    print ('intersection existed')
                elif nTotalVerts > numOutputVertices.value:
                    print ('duplicated dictVertices existed')
                outputCoordsIndice = [] #the indices of the outputVerts
                for j in range (0, numOutputVertices.value):
                    vert = [coordsOutput[j][0], coordsOutput[j][1], coordsOutput[j][2]]
                    try:
                        k = self.listVertices.index(vert)
                    except ValueError:
                        k = len(self.listVertices)
                        self.listVertices.append(vert)
                        print ('Vertex '+ str(k) + ' added')
                    outputCoordsIndice.append(k)
                #Add to listFaces
                for j in range (0, numOutputIndices.value):
                    self.listFaces.append([outputCoordsIndice[indicesOutput[j][0]],outputCoordsIndice[indicesOutput[j][1]],outputCoordsIndice[indicesOutput[j][2]]])
            elif self.bTessellation == True and line_list[0][0] > 3:
                #workaround
                curDirBefore = os.getcwd()
                path = os.path.dirname(os.path.realpath(__file__))
                if sizeof(c_voidp) == 4:
                    path = os.path.join(path, 'x32')
                    os.chdir(path)
                    Tessellator = CDLL('tesselatorInterface.dll')
                elif sizeof(c_voidp) == 8:
                    #workaround 
                    path = os.path.join(path, 'x64')
                    os.chdir(path)
                    Tessellator = CDLL('tesselatorInterface.dll')
                os.chdir(curDirBefore)
                #add rinsg
                ExtRingCoords = (POINTER(c_double) * line_list[0][0])()
                for j in range(0, line_list[0][0]):
                    ExtRingCoords[j] = (c_double * 3)()
                    ExtRingCoords[j][0] = self.listVertices[line_list[0][j+1]][0]
                    ExtRingCoords[j][1] = self.listVertices[line_list[0][j+1]][1]
                    ExtRingCoords[j][2] = self.listVertices[line_list[0][j+1]][2]
                Tessellator.AddRing(byref(ExtRingCoords), c_int(int(line_list[0][0])), c_bool(1))
                #compute
                numOutputVertices = c_int(0)
                numOutputIndices = c_int(0)
                if Tessellator.Tessellation(byref(numOutputVertices), byref(numOutputIndices)) == c_bool(0):
                    print "Tesselation failed"
                #output
                coordsOutput = (POINTER(c_double) * numOutputVertices.value)()
                for i in range(0, numOutputVertices.value):
                    coordsOutput[i] = (c_double * 3)()
                indicesOutput = (POINTER(c_int) * numOutputIndices.value)()
                for i in range(0, numOutputIndices.value):
                    indicesOutput[i] = (c_int * 3)()
                Tessellator.Output(byref(coordsOutput), byref(indicesOutput))
                #convert indices
                if line_list[0][0] < numOutputVertices.value:
                    print ('intersection existed')
                elif line_list[0][0] > numOutputVertices.value:
                    print ('duplicated dictVertices existed')
                outputCoordsIndice = [] #the indices of the outputVerts
                for j in range (0, numOutputVertices.value):
                    vert = [coordsOutput[j][0], coordsOutput[j][1], coordsOutput[j][2]]
                    try:
                        k = self.listVertices.index(vert)
                    except ValueError:
                        k = len(self.listVertices)
                        self.listVertices.append(vert)
                        print ('Vertex '+ str(k) + ' added')
                    outputCoordsIndice.append(k)
                #Add to listFaces
                for j in range (0, numOutputIndices.value):
                    self.listFaces.append([outputCoordsIndice[indicesOutput[j][0]],outputCoordsIndice[indicesOutput[j][1]],outputCoordsIndice[indicesOutput[j][2]]])
            else:
                self.listFaces.append(line_list[0][1:])

        #check the content
        if self.listVertices.count == 0 or self.listFaces.count == 0:
            print "Invalid Poly file!\n"
            sys.exit()
        filePoly.close()
        os.remove(self.inputFile + "mid")
    #end __read_poly


    def __write_obj(self):
        try:
            fileObj = file(self.outputFile, 'w')
        except:
            print ("Invalide file:" + self.outputFile)
            sys.exit()
        
        fileObj.write("# Created by obj2poly from "+ str(self.inputFile) + '\n')
        fileObj.write("# Object\n")

        #dictVertices
        for vert in self.listVertices:
            fileObj.write("v ")
            fileObj.write(str(vert).replace(',', '')[1:-1] + '\n')
        fileObj.write("# ")
        fileObj.write(str(len(self.listVertices)) + ' ')
        fileObj.write("dictVertices\n")

        #dictFaces
        for face in self.listFaces:
            #index + 1
            face = [i + 1 for i in face]
            fileObj.write("f ")
            fileObj.write(str(face).replace(',', '')[1:-1] + '\n')
        fileObj.write("# ")
        fileObj.write(str(len(self.listFaces)) + ' ')
        fileObj.write("dictFaces\n")
        fileObj.close()
    #end __write_obj


    def __write_poly(self):
        try:
            filePoly = file(self.outputFile, 'w')
        except:
            print ("Invalide file:" + self.outputFile)
            sys.exit()
        filePoly.write(str(len(self.listVertices)) + ' 3'+ ' 0' + ' 0'+'\n')
        for i in range(0, len(self.listVertices)):
            filePoly.write(str(i) +' '+ str(self.listVertices[i]).replace(',', '')[1:-1] + '\n')

        #write dictFaces
        filePoly.write(str(len(self.listFaces)) + ' 0' + '\n')
        for i in range(0, len(self.listFaces)):
            filePoly.write("1 0\n")
            filePoly.write(str(len(self.listFaces[i])) + ' ')
            for j in range (0, len(self.listFaces[i])):
                filePoly.write(str(self.listFaces[i][j]) + ' ')
            filePoly.write('\n')
        filePoly.write('0\n')
        filePoly.write('0\n')
        filePoly.close()
    #end __write_poly

    def __read_semantic_poly(self):
        fin = file(self.inputFile, 'r')
        #read the first line and try to extract semantics
        strFirstLine = fin.readline().split()
        if strFirstLine[0] == '#':
            #read the building id
            self.strModelID = strFirstLine[1]
            #whether the geometry is a solid:1 or a multisurface:0
            self.isSolid = int(fin.readline().split()[1])
            #the point information
            strFirstLine = int(fin.readline().split()[0])
        else:
            #no semanics
            self.strModelID = '-1'
            #we assume it is a solid
            self.isSolid = 1
            #the point information
            strFirstLine = int(strFirstLine[0])
        #read all the points
        for i in range(strFirstLine):
            self.listVertices.append(map(float, fin.readline().split()[1:4]))

        #read each face
        nof = int(fin.readline().split()[0])
        for i in range(nof):
            #read surface semantics
            strPolygonInfo = fin.readline().split()
            numRings = int(strPolygonInfo[0])
            strPolygonId = '' 
            strPolygonType = ''
            if len(strPolygonInfo) >= 4:
                strPolygonId = strPolygonInfo[3]
            if len(strPolygonInfo) >= 6:
                strPolygonType = strPolygonInfo[5]
            #read surface geometry
            oRing = map(int, fin.readline().split())
            oRing.pop(0)
            iRings = []
            if numRings > 1:
                for j in range (1, numRings):
                    iRing = map(int, fin.readline().split())
                    iRing.pop(0)
                    iRings.append(iRing)
                for j in range (1, numRings):
                    fin.readline()
            #do tesselation for polygons
            if len(oRing) > 3 or numRings > 1:
                curDirBefore = os.getcwd()
                path = os.path.dirname(os.path.realpath(__file__))
                if sizeof(c_voidp) == 4:
                    path = os.path.join(path, 'x32')
                    os.chdir(path)
                    Tessellator = CDLL('tesselatorInterface.dll')
                elif sizeof(c_voidp) == 8:
                    #workaround 
                    path = os.path.join(path, 'x64')
                    os.chdir(path)
                    Tessellator = CDLL('tesselatorInterface.dll')
                os.chdir(curDirBefore)
                #add rings
                ExtRingCoords = (POINTER(c_double) * len(oRing))()
                for j in range(len(oRing)):
                    ExtRingCoords[j] = (c_double * 3)()
                    ExtRingCoords[j][0] = self.listVertices[oRing[j]][0]
                    ExtRingCoords[j][1] = self.listVertices[oRing[j]][1]
                    ExtRingCoords[j][2] = self.listVertices[oRing[j]][2]
                Tessellator.AddRing(byref(ExtRingCoords), len(oRing), c_bool(1))

                for j in range (0, numRings-1):
                    IntRingCoords = (POINTER(c_double) * len(iRings[j]))()
                    for k in range (0, len(iRings[j])):
                        IntRingCoords[k] = (c_double * 3)()
                        IntRingCoords[k][0] = self.listVertices[iRings[j][k]][0]
                        IntRingCoords[k][1] = self.listVertices[iRings[j][k]][1]
                        IntRingCoords[k][2] = self.listVertices[iRings[j][k]][2]
                    Tessellator.AddRing(byref(IntRingCoords), len(iRings[j]), c_bool(0))
                 
                #compute
                numOutputVertices = c_int(0)
                numOutputIndices = c_int(0)
                if Tessellator.Tessellation(byref(numOutputVertices), byref(numOutputIndices)) == c_bool(0):
                    print "Tesselation failed"
                #get output
                coordsOutput = (POINTER(c_double) * numOutputVertices.value)()
                for i in range(0, numOutputVertices.value):
                    coordsOutput[i] = (c_double * 3)()
                indicesOutput = (POINTER(c_int) * numOutputIndices.value)()
                for i in range(0, numOutputIndices.value):
                    indicesOutput[i] = (c_int * 3)()
                Tessellator.Output(byref(coordsOutput), byref(indicesOutput))
                #convert indices
                outputCoordsIndice = [] #the indices of the outputVerts
                for j in range (0, numOutputVertices.value):
                    vert = [coordsOutput[j][0], coordsOutput[j][1], coordsOutput[j][2]]
                    try:
                        k = self.listVertices.index(vert)
                    except ValueError:
                        k = len(self.listVertices)
                        self.listVertices.append(vert)
                        print ('Vertex '+ str(k) + ' added')
                    outputCoordsIndice.append(k)
                #Add to listFaces
                for j in range (0, numOutputIndices.value):
                    self.listFaces.append([outputCoordsIndice[indicesOutput[j][0]],outputCoordsIndice[indicesOutput[j][1]],outputCoordsIndice[indicesOutput[j][2]]])
                    self.listFaceSemantics.append((strPolygonId, strPolygonType))
            else:
                #add rings and its semantics
                self.listFaces.append(oRing)
                self.listFaceSemantics.append((strPolygonId, strPolygonType))
    #end __read_semantic_poly

    def __write_semantic_poly(self):
        try:
            filePoly = file(self.outputFile, 'w')
        except:
            print ("Invalide file:" + self.outputFile)
            sys.exit()
        #model information
        filePoly.write('# ' + self.strModelID + '\n')
        filePoly.write('# ' + str(self.isSolid) + '\n')
        #dictVertices
        filePoly.write(str(len(self.listVertices)) + ' 3'+ ' 0' + ' 0'+'\n')
        for i in range(0, len(self.listVertices)):
            filePoly.write(str(i) +' '+ str(self.listVertices[i]).replace(',', '')[1:-1] + '\n')

        #write dictFaces
        filePoly.write(str(len(self.listFaces)) + ' 0' + '\n')
        for i in range(0, len(self.listFaces)):
            filePoly.write('1 0' + ' # ' + self.listFaceSemantics[i][0] + ' # '+ self.listFaceSemantics[i][1] + '\n')
            filePoly.write(str(len(self.listFaces[i])) + ' ')
            for j in range (0, len(self.listFaces[i])):
                filePoly.write(str(self.listFaces[i][j]) + ' ')
            filePoly.write('\n')
        filePoly.write('0\n')
        filePoly.write('0\n')
        filePoly.close()
    #end __write_semantic_poly