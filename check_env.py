#!/usr/bin/env python3

import sys
import subprocess
import re
import os
from distutils.version import LooseVersion, StrictVersion

if sys.version_info < (3, 0):
  print("Error: Python 2 is not supported")
  sys.exit(1)

print("Python:", sys.version_info)

try:
    import numpy
except ImportError:
    print("Error: Failed to import required modules: numpy")
    sys.exit(1)


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
    # print(output.decode('utf-8'))
    if m:
      version = m.group(1)
    else:
      version = "unknown"


    if version == "unknown":
      status += version + " - FAIL"
    elif LooseVersion(version) >= LooseVersion(requiredVersion):
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
    "pattern": ".*(v\S+)",
    "requiredVersion": "v5.10.1"
  },
  {
    "toolName":"Synopsys Design Compiler",
    "cmd":"dc_shell -v",
    "pattern": "dc_shell\sversion\s+-\s+(\S+)",
    "requiredVersion": "O-2018.06"
  },
  {
    "toolName":"Synopsys Library Compiler",
    "cmd":"lc_shell -v",
    "pattern": "lc_shell\sversion\s+-\s+(\S+)",
    "requiredVersion": "O-2018.06"
  },
  {
    "toolName":"Cadence Innovus",
    "cmd":"innovus -version | reset",
    "pattern": "CDS: Innovus (v\S+)",
    "requiredVersion": "v18.10-p002_1"
  },
  {
    "toolName":"Synopsys Primetime",
    "cmd":"primetime -version",
    "pattern": "pt_shell\sversion\s+-\s+(\S+)",
    "requiredVersion": "O-2018.06-1"
  },
  {
    "toolName":"Mentor Graphics Calibre",
    "cmd":"calibre -version",
    "pattern": "Calibre (v\S+)",
    "requiredVersion": "v2019.3_25.15"
  },
  {
    "toolName":"Synopsys HSPICE",
    "cmd":"hspice -v",
    "pattern": "HSPICE Version (\S+)",
    "requiredVersion": "N-2017.12-SP2-1"
  },
  {
    "toolName":"Cadence Spectre",
    "cmd":"spectre -version",
    "pattern": "spectre\s+version\s+(\S+)",
    "requiredVersion": "15.1.0"
  }
  # {
  #   "toolName":"Cadence Liberate",
  #   "cmd":"liberate -v",
  #   "pattern": "LIBERATE version (\S+)",
  #   "requiredVersion": "16.1.1.132"
  # }
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

