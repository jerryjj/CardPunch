#!/usr/bin/env python2.5

# Setup our import paths
import os, sys
local_module_dir = os.path.join(os.path.dirname(sys.argv[0]),  'libs')
if os.path.isdir(local_module_dir):                                       
    sys.path.append(local_module_dir)

from libs import server

if __name__ == "__main__":
    server.start()

