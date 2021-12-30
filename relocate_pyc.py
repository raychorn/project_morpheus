import os
import sys

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
        if (os.path.splitext(fpath)[1] == '.pyc') and (fpath != THIS_FILE) and (fpath.find(venvDir) == -1):
            if (fpath.find('.cpython-') > -1):
                toks = fpath.split('.')
                new_fpath = '.'.join(toks[0:-2]+toks[-1:])
                print('Moving ({}) {} --> {} [{}]'.format(fpath.find(venvDir), fpath, new_fpath, toks))
                os.rename(fpath, new_fpath)
