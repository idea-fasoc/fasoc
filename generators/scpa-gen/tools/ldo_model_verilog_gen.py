#!/usr/bin/env python2

#------------------------------------------------------------------------------
# LDO MODEL VERILOG GEN
# IDEA & POSH Integration Excercises
# Date: 12/21/2018
#------------------------------------------------------------------------------
import argparse
import sys
import math
import getopt
import os

#------------------------------------------------------------------------------
# Initialize the config variables
#------------------------------------------------------------------------------
genDir = os.path.join(os.path.dirname(os.path.relpath(__file__)),"../")
head_tail_0 = os.path.split(os.path.abspath(genDir))
head_tail_1 = os.path.split(head_tail_0[0])
privateGenDir = os.path.relpath(os.path.join(genDir, '../../', 'private', head_tail_1[1], head_tail_0[1]))
digitalFlow = os.path.join(privateGenDir , './flow')
aCell = ''

#------------------------------------------------------------------------------
# Parse the command line arguments
#------------------------------------------------------------------------------
try:
   opts, args = getopt.getopt(sys.argv[1:],'ha:')
except getopt.GetoptError:
   print('usage: ldo_model_verilog_gen.py ' + \
         '-a <AuxCellName> ' + \
         '[-d <DigitalFlowPath>]')
   sys.exit(1)

for opt, arg in opts:
   if opt == '-h':
      print('usage: ldo_model_verilog_gen.py ' + \
            '-a <AuxLibName> ' + \
            '[-d <DigitalFlowPath>]')
      sys.exit(1)
   elif opt in ('-a'):
      aCell = arg

#------------------------------------------------------------------------------
# Check for configuration errors
#------------------------------------------------------------------------------
if aCell == '':
   print('usage: ldo_model_verilog_gen.py ' + \
         '-a <AuxCellName> ' + \
         '[-d <DigitalFlowPath>]')
   print('Please specify the auxiliary cell name.')
   sys.exit(1)

#------------------------------------------------------------------------------
# Get the PT array size 
#------------------------------------------------------------------------------
arrSize = int(args[0])

# Get no. of bits required to represent array size
arrSizeNumBits = int(math.ceil(math.log((arrSize+1)/1.0, 2)))

# Get ctrl word initialization in hex
ctrlWordHexCntF = int(math.floor(arrSize/4.0))
ctrlWordHexCntR = int(arrSize % 4.0)
ctrlWordHex = ['h']
ctrlWordHex.append(str(hex(pow(2,ctrlWordHexCntR)-1)[2:]))
for i in range(ctrlWordHexCntF):
   ctrlWordHex.append('f')
ctrlWdRst = str(arrSize) + '\'' + ''.join(ctrlWordHex)

#------------------------------------------------------------------------------
# Open the Verilog file
#------------------------------------------------------------------------------
vmodule = 'LDO_' + str(arrSize)
vfile = vmodule + '.v'
vfilepath = digitalFlow + '/src/' + vfile
f = open(vfilepath, 'w')

#------------------------------------------------------------------------------
# Write the Verilog file
#------------------------------------------------------------------------------

# Module Instantiation
f.write('module %s(\n' % vmodule)
f.write('   input  clk, reset,\n')
f.write('   input  [%d:0] ctrl,\n' % (arrSizeNumBits-1))
f.write('   output [1:0] cnt);\n\n')

# Declare local variables
f.write('   wire vout;\n')
f.write('   reg [%d:0] pt_ctrl_word = %s;\n' % (arrSize-1, ctrlWdRst))
f.write('   reg [%d:0] ctrl_decode;\n' % (arrSize-1))
f.write('   reg [1:0] cnt;\n\n')

# Adding a Thermometer Controller
f.write('   // Thermometer controller\n')
f.write('   always@(*) begin\n')
f.write('      case(ctrl[%d:0])\n' % (arrSizeNumBits-1))
for i in range(arrSize+1):
   caseWdHexCntF = int(math.floor((arrSize-i)/4.0))
   caseWdHexCntR = int((arrSize-i) % 4.0)
   caseWdHex = []
   caseWdHex.append(str(hex(pow(2,caseWdHexCntR)-1)[2:]))
   for j in range(caseWdHexCntF):
      caseWdHex.append('f')
   ctrlWdRst = str(arrSize) + '\'' + ''.join(ctrlWordHex)
   f.write('         %d\'h%s: ctrl_decode' % (arrSizeNumBits, str(hex(i)[2:])))
   f.write(' = %d\'h%s;\n' % (arrSize, ''.join(caseWdHex)))
f.write('         default: ctrl_decode = %s;\n' % ctrlWdRst)
f.write('      endcase\n')
f.write('   end\n\n')

f.write('   always @(posedge clk) begin\n')
f.write('      if (reset) begin\n')
f.write('         cnt <= 2\'h0;\n')
f.write('         pt_ctrl_word <= %s;\n' % ctrlWdRst)
f.write('      end\n')
f.write('      else begin\n')
f.write('         cnt <= cnt + 1;\n')
f.write('         pt_ctrl_word <= ctrl_decode;\n')
f.write('      end\n')
f.write('   end\n\n')

# Print the Transistor Array
f.write('   // Power Transistor Cell\n')
for i in range(arrSize):
   f.write('   %s pt_array_unit%d (.CTRL(pt_ctrl_word[%d]));\n' % (aCell, i, i))
f.write('\n')

# End Module 
f.write('endmodule')

# Close the file
f.close()
