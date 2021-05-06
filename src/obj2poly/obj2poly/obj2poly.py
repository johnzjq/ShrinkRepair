#Convertion between Obj and Poly format (only geometric part)
#Support Obj->Poly and its inverse
#Usage "obj2poly FILEPATH1 FILEPATH2" where FILE1 is converted to FILE2

import sys
import os
from ConvProvider import ConvProvider

def main():
	#handel the arguments and make the conversion decision
    if len(sys.argv) < 3:
        if len(sys.argv) == 2 and sys.argv[1].startswith('--') and sys.argv[1][2:] == 'help':
                #help part
                print """
    Convertion between Obj and Poly format and tesselation (only geometric part) holes in polyfiles are always tessellated
    Support Obj<->Poly and its tesselation, and Obj->Tesselated Obj and Poly->Tesselated Poly, the format is detected by the suffix
    Usage: "obj2poly FILEPATH1 FILEPATH2 bFlag" where FILE1 is converted to FILE2 and bFlag == True means tessellation of all the polygons
                """
        else:
            print "TWO FILEPATHS REQUIRED. Plz see details by obj2poly --help"
            sys.exit()

    elif len(sys.argv) in (3, 4):
        fileName1, fileExt1 = os.path.splitext(sys.argv[1])
        fileName2, fileExt2 = os.path.splitext(sys.argv[2])
        if fileExt1 in ('.obj', '.poly') and fileExt2 in ('.obj', '.poly'):
            #generic conversion
            MyCov = ConvProvider()
            if len(sys.argv) == 3 or (len(sys.argv) == 4 and (sys.argv[3] == 'False' or sys.argv[3] == 'false')):
                # standardised convertion without tessellation
                if MyCov.convert(sys.argv[1], sys.argv[2]) == False:
                    print ("Conversion failed")
                    sys.exit()
            elif len(sys.argv) == 4 and (sys.argv[3] == 'True' or sys.argv[3] == 'true'):
                 # convertion with tessellation
                 if MyCov.convert(sys.argv[1], sys.argv[2], True) == False:
                     print ("Conversion failed")
                     sys.exit()
            print ("Successed!")
        else:
            print ("Invalide file extension or bFlag value. Support conversion between obj and poly and its tessellation. Plz see details by obj2poly --help")
    else:
        print ("TWO FILEPATHS REQUIRED. Plz see details by obj2poly --help")
        sys.exit()
		
if __name__ == '__main__':
	main()
   





