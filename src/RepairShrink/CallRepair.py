#this script is used to call repair for many objects
import subprocess, sys, os, shutil

def Main():
    #all the scripts python2.7
    runCityGML2SPoly = [r"..\\CityGML2SPoly\TestCityGML2SPoly\bin\ ", 'run.bat ']
    runObj2Poly = r"python.exe ..\\obj2poly\obj2poly\obj2polyfolder.py "
    runSPolys2CityGML = r"python.exe ..\\SPolys2CityGML\spolys2citygml.py "
    runRepair = r"python.exe ..\\RepairShrink\RepairShrink\RepairShrink.py "
	
    if sys.argv[2] == "poly" or sys.argv[2] == "obj":
		#run repair for an object
		runstr = runRepair + sys.argv[1] + " 0"
		print runstr
		op = subprocess.Popen(runstr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if op.poll():
			print op.communicate()
			op.terminate()
		op.communicate()
    elif sys.argv[2] == "folder":
		#run repair for a folder
		try:
			os.chdir(sys.argv[1])
			dFiles = {}
			for f in os.listdir('.'):
				if f[-4:] == 'poly':
					i = (f.split('.poly')[0]).rfind('.')
					f1 = f[:i]
					if f1 not in dFiles:
						dFiles[f1] = [f]
					else:
						dFiles[f1].append(f)
			if len(dFiles) > 0:
				bIsFolder = True
		except:
			print ("The input parameter 1 should be a OBJ or POLY file or a folder of a set of model file")
			sys.exit()
	
		for polyname in dFiles:
			runstr = runRepair + dFiles[polyname][0] + " -s 0"
			print runstr
			op = subprocess.Popen(runstr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			if op.poll():
				print op.communicate()
				op.terminate()
			op.communicate()
			
			
			
    elif sys.argv[2] == "citygml":
		#run the whole process for a CityGML model
          #extract the path and create the path for the files
          strFilePath, strFileName = os.path.split(sys.argv[1])
          strFolderName = strFileName[:-4] + '_polys'
          strSubFolder = strFilePath + '/' + strFolderName
          if not os.path.exists(strSubFolder):
              os.mkdir(strSubFolder)
          else:
              shutil.rmtree(strSubFolder)
              os.mkdir(strSubFolder)
		#extract polys
          os.chdir(runCityGML2SPoly[0])
          run_script(runCityGML2SPoly[1], sys.argv[1] + ' ' + strSubFolder + ' -s')
          os.chdir(strSubFolder)
		#tesselate polys
          run_script(runObj2Poly, strSubFolder + ' poly2poly')
		#repair polys
          run_script(runRepair, strSubFolder + ' -s 0')
		#assemble the polys
          run_script(runSPolys2CityGML, strSubFolder + ' > ' + strFileName[:-4] + '_repaired.xml')
    else:
		print("wrong augments")
  
def run_script(strScritp, strAugments):
    runstr = strScritp + strAugments
    print runstr
    subprocess.call(runstr)
#    op = subprocess.Popen(runstr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    if op.poll():
#        print op.communicate()
#        op.terminate()
#    op.communicate()
    
if __name__ == '__main__':
    Main()
