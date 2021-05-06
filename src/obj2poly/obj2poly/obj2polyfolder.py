import os, sys, subprocess

def Main():
	obj2poly = "c:\\python27\\python "
	path = os.path.dirname(os.path.realpath(__file__))
	obj2poly = obj2poly + path + "\\obj2poly.py"
	os.chdir(sys.argv[1])
	if sys.argv[2] == "obj2poly":
		dFiles = []
		for f in os.listdir('.'):
			if f[-3:] == 'obj':
				dFiles.append(f)
		if len(dFiles) == 0:
			return
		for f in dFiles:
			fout = f[:-4] + '.poly'
			runstr = obj2poly + ' ' + f + ' ' + fout
			#print runstr
			op = subprocess.call(runstr)
			if op.poll():
				print op.communicate()
				op.terminate()
			op.communicate()
	elif sys.argv[2] == "poly2obj":
		dFiles = []
		for f in os.listdir('.'):
			if f[-4:] == 'poly':
				dFiles.append(f)
		if len(dFiles) == 0:
			return
		for f in dFiles:
			fout = f[:-5] + '.obj'
			runstr = obj2poly + ' ' + f + ' ' + fout
			#print runstr
			op = subprocess.call(runstr)
	elif sys.argv[2] == "poly2poly":
		dFiles = []
		for f in os.listdir('.'):
			if f[-4:] == 'poly':
				dFiles.append(f)
		if len(dFiles) == 0:
			return
		for f in dFiles:
			fout = f[:-5] + '.poly'
			runstr = obj2poly + ' ' + f + ' ' + fout + ' True'
			#print runstr
			op = subprocess.call(runstr)

if __name__ == '__main__':
    Main()