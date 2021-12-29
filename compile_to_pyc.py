import os
import sys
import py_compile

rootDir = None
if (len(sys.argv) > 1 and isinstance(sys.argv[1], str) and (len(sys.argv[1]) > 0)):
    rootDir = sys.argv[1]
    
venvDir = None
if (len(sys.argv) > 2 and isinstance(sys.argv[2], str) and (len(sys.argv[2]) > 0)):
    venvDir = sys.argv[2]
    venvDir = venvDir.replace("/bin/activate", "/")
    
if (rootDir is None):
    print("Usage: compile_to_pyc.py <rootDir> <venvDir>")
    sys.exit(0)

if (venvDir is None):
    print("Usage: compile_to_pyc.py <rootDir> <venvDir>")
    sys.exit(0)

THIS_FILE = os.path.abspath(__file__)

print('venvDir: {}'.format(venvDir))

for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
    for fname in fileList:
        fpath = os.path.join(dirName, fname)
        if (os.path.splitext(fpath)[1] == '.py') and (fpath != THIS_FILE) and (fpath.find(venvDir) == -1):
            print('Compiling ({}) {}'.format(fpath.find(venvDir), fpath))
            py_compile.compile(fpath)
