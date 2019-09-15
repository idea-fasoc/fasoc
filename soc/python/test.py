#!/usr/bin/env python3

import os
soc_dir = os.path.dirname(__file__)
fasoc_dir  = os.path.relpath(os.path.join(soc_dir,"../.."))
rubiDir = os.path.join(soc_dir,'..','rubi')
print(soc_dir)
print(fasoc_dir)
print(rubiDir)