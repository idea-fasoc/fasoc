#!/usr/bin/env python3

import sys
import subprocess
import re
import os
from distutils.version import LooseVersion, StrictVersion

if sys.version_info < (3, 0):
  print("Error: Python 3 is not supported")
  sys.exit(1)

#TODO: Test all required python libraries

# Function to test for tool installation and version
# ==============================================================================
def checkTool(toolName, cmd, pattern, requiredVersion):
  status= toolName +": required " + requiredVersion + " (or greater), detected "
  output=""
  error=1
  ret=1

  try:
    # Note that some tools print out the version information to stderr (e.g spectre)
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, error = process.communicate()
  except:
    pass

  if (not error):
    m =  re.search(pattern, output.decode('utf-8'))
    if m:
      version = m.group(1)
    else:
      version = "unknown"


    if LooseVersion(version) >= LooseVersion(requiredVersion):
      status += version + " - PASS"
      ret = 0
    else:
      status += version + " - FAIL"
  else:
    status += "no install - FAIL"

  print(status)
  return ret

# Main
# ==============================================================================

toolList =[
  {
    "toolName":"PERL",
    "cmd":"perl -v",
    "pattern": "This is perl, (v\S+)",
    "requiredVersion": "v5.10.1"
  },
  {
    "toolName":"Synopsys Design Compiler",
    "cmd":"dc_shell -v",
    "pattern": "dc_shell\sversion\s+-\s+(\S+)",
    "requiredVersion": "L-2016.03-SP2"
  },
  {
    "toolName":"Cadence Innovus",
    "cmd":"innovus -version | reset",
    "pattern": "CDS: Innovus (v\S+)",
    "requiredVersion": "v15.21-s080_1"
  },
  {
    "toolName":"Synopsys Primetime",
    "cmd":"primetime -version",
    "pattern": "pt_shell\sversion\s+-\s+(\S+)",
    "requiredVersion": "L-2016.06"
  },
  {
    "toolName":"Mentor Graphics Calibre",
    "cmd":"calibre -version",
    "pattern": "Calibre (v\S+)",
    "requiredVersion": "v2016.1_23.16"
  },
  {
    "toolName":"Synopsys HSPICE",
    "cmd":"hspice -v",
    "pattern": "HSPICE Version (\S+)",
    "requiredVersion": "M-2017.03-SP1"
  },
  {
    "toolName":"Cadence Spectre",
    "cmd":"spectre -version",
    "pattern": "spectre\s+version\s+(\S+)",
    "requiredVersion": "15.1.0"
  },
  {
    "toolName":"Cadence Liberate",
    "cmd":"liberate -v",
    "pattern": "LIBERATE version (\S+)",
    "requiredVersion": "16.1.1.132"
  }
]

status = 0
for tool in toolList:
  status += checkTool(tool["toolName"],
                  tool["cmd"],
                  tool["pattern"],
                  tool["requiredVersion"])
  # Innovus will often leave the terminal in a bad state. Cleaning up the
  # terminal
  os.system("stty sane")

if status:
  print("\n\nTotal issues detected: " + str(status) + "\n")
else:
  print("\n\nEnvironment is successfully setup to run the FASoC flow\n")

