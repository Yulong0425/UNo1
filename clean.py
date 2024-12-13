# If files in one folder are empty, delete all of these file

import os
import shutil

for root, dirs, files in os.walk("."):
    if len(files) == 0:
        shutil.rmtree(root)