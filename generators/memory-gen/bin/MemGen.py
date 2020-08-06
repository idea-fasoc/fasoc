#!/usr/bin/env python3.7

###################################################################################
# Version : Alpha-1.0                                      #
# Date    : Apr 26, 2019                                     #
# Author  : Sumanth Kamineni                                 #
# Contact : SumanthKamineni@virginia.edu                                #
###################################################################################
# What's in the release?                                                          #
# First version of the Memory generator alpha release.                         #
# This version generates the memory and its associated (GDS, LEF, LIB, DB)        #
# files for the given user specifications.                  #
# This relase includes verilog generation, synthesis and auto place & route       #
###################################################################################

import os
import sys
import re
import datetime
import time
import smtplib
import logging
import getpass
from optparse import OptionParser
import math
import shutil
import tempfile
import subprocess as sp
#import matplotlib.pyplot as p
#import numpy as np
#from itertools import izip
import json

global log

log=logging.getLogger(__name__)

class PDKError(Exception):
        ''' Raised when all the required variables for PDK is not set'''
        pass

class MemGen():
        '''
        Wrapper Class on the memory macro generation. It takes the user spec and generates the memory macro.
        Inputs  : User spec in JSON format.
        Outputs : Memory macro and its associated views for top-level SoC.
        '''
        def __init__(self):
               '''
               Grabs the input spec file and runs the memory generation step-by-step.

               '''
               if p_options['Toolenvt']:
                     pass 
                     #self.toolsetuptemplate()
               else:
                     #self.toolenv()
                     try:
                          os.mkdir('runfiles')
                     except OSError:
                          if os.path.exists('runfiles'):
                              log.debug("Directory already exists")
                          else:
                              log.error("Unable to create the dir, check the permissions of the run dir %s"%rundir)
                              sys.exit(1)
                     self.runfilesdir = os.path.join(rundir,'runfiles')
                     self.digitalflowdir = os.path.join(rundir, 'apr')
                     self.digitalflowsrcdir = os.path.join(self.digitalflowdir, 'src')
                     if p_options['Mode'] == 'verilog':
                        self.ConfigParser()
                        self.SRAMConfig()
                        self.VerilogGen()
                        self.Filemanage()
                     elif p_options['Mode'] == 'macro':
                        binDir = os.path.dirname(os.path.abspath(__file__)) #Directory in which the top-level python executable is present. 
                        genDir = os.path.dirname(binDir) #Generator Directory
                        genName = os.path.split(genDir)[1]
                        genParentdir = os.path.split(genDir)[0]
                        genParentdirName = os.path.split(genParentdir)[1]
                        Fasocdir = os.path.split(genParentdir)[0]
                        self.Fasocdir = Fasocdir
                        self.digitalflowdir = os.path.join(Fasocdir, 'private', genParentdirName, genName, 'apr')
                        self.digitalflowsrcdir = os.path.join(self.digitalflowdir, 'src')
                        self.ConfigParser()
                        self.SRAMConfig()
                        self.VerilogGen()
                        log.info("Successfully generated the SRAM verilog files")
                        if  os.path.exists(os.path.join(Fasocdir, 'private')):
                             self.DataPrep()
                             self.Synthesis()
                             self.PNR()
                             self.Filemanage()
                             log.info("Successfully generated the syntehsizable SRAM. Refer the outputs dir for all the generated outputs")
                        else:
                             log.error("Unable to find the directory %s with MemGen synthesis and apr scripts. Unable to run the synthesis and PNR of the memory"%os.path.join(Fasocdir, 'private'))
                             sys.exit(1)
                        
        def ConfigParser(self):
               '''
                Parsers the input spec file and creates the necessary variables.

               '''
               log.info(" Loading the memory specs config file %s"%p_options['Config'])
               try:
                     with open(p_options['Config']) as file:
                         self.config = json.load(file)
               except ValueError as e:
                   log.error('Error occurred opening or loading json file.')
                   log.error('Exception: %s' % str(e))
                   sys.exit(1)
               self.sram_name   = self.config["module_name"]
               self.nowords     = self.config["specifications"]["nowords"]
               self.word_size   = self.config["specifications"]["word_size"]

        def SRAMConfig(self):
               '''
                Determines the SRAM configuration for the specs specified in the input spec file.

                '''
               log.info("Determining the SRAM Configuration")
               nbfra, nbwhole         = math.modf((self.nowords*self.word_size)/16384); # Dividing by 2KB = 2*1024*8 = 16384 bits
               if nbfra:
                     log.error("The memory for the specified words %d can not be generated"%self.nowords)
                     log.error("Due to current limitations of the tool, the memory not in multiples of 2 Kilo Bytes can not be generated")               
                                 
                     log.error("Please specify the size in multiples of 2KB and re-run")  
                     sys.exit(1)
               elif not nbfra:
                     bsbfra, bsbwhole       = math.modf(math.log2(nbwhole))
                     if bsbfra:
                          log.error("The number of banks should be integer powers of 2 Ex: 2^n, where n=natural number (1,2,3,4). Please specify the correct size and re-run the MemGen")
                          sys.exit(1)
                     else:
                          self.no_banks = int(nbwhole)
                          self.banksel_bits = int(bsbwhole)
               self.bank_address_size        =      9
               self.address_size     =   (self.banksel_bits+self.bank_address_size)
               self.decoder_bits     =   self.banksel_bits
               self.muxsel_bits      =    self.banksel_bits
               log.info("Below is the SRAM configuration:\n SRAM Capacity : %d KB \n No of Banks : %d \n Address bits : %d \n Bank Address Size : %d \n"%(self.no_banks*2, self.no_banks, self.address_size, self.bank_address_size))

        def VerilogGen(self):
               '''
                Generates the required verilog files for the SRAM.

                '''
               log.info("Generating the verilog modules")
               #time.sleep(5)
               self.Verilogrundir    =  os.path.join(self.runfilesdir, 'VerilogGen')
               try:
                     os.mkdir(self.Verilogrundir)
                     os.chdir(self.Verilogrundir)
               except OSError:
                     if os.path.exists(self.Verilogrundir):
                          log.info("Directory %s already exists"%self.Verilogrundir)
                          log.info(" Cleaning up the existing SRAM verilog files")
                          os.chdir(self.Verilogrundir)
                          evs=li=os.popen("ls *.v*").read().split() #Existing verilog files
                          for l in evs:
                              log.info("Removing %s"%l)
                              os.remove(l)
                     else:
                                log.error("Unable to create the dir %s, Can not run the VerilogGen. Exitting MemGen.."%self.Verilogrundir)
                                sys.exit(1)
               self.decoder_name = "decoder_%dto%d"%(self.decoder_bits, self.no_banks)
               self.mux_name     = "mux_%dto1"%self.no_banks
               #self.sram_name    = "SRAM_%dKB"%self.memory_size
               self.VerilogGen_decoder()
               self.VerilogGen_mux()
               self.VerilogGen_SRAM()

               log.info("Successfully completed the generation of all the required verilog modules.")
               os.chdir(rundir)

        def VerilogGen_decoder(self):
               '''
                Generates the SRAM input decoder verilog file.

               '''
               self.decoder=os.path.join(self.Verilogrundir,self.decoder_name+'.v')
               log.info("Generating the verilog file %s"%self.decoder_name)
               dfh=open(self.decoder, 'w')
               dfh.write("module %s (DATA_REQ, ADDR, DATA_REQIN);\n"%self.decoder_name)
               dfh.write("   parameter no_banks = %d;\n"%self.no_banks)
               dfh.write("   parameter banksel_bits = %d;\n"%self.banksel_bits)
               dfh.write("   output [no_banks-1:0] DATA_REQ;\n")
               dfh.write("   input  [banksel_bits-1:0] ADDR;\n")
               dfh.write("   input DATA_REQIN;\n")
               dfh.write("   reg [no_banks-1:0] DATA_REQ;\n")
               dfh.write("   always @(DATA_REQIN or ADDR) begin\n")
               dfh.write("     if (DATA_REQIN == 1'b1)\n")
               dfh.write("         case (ADDR)\n")
               addr = '0'*self.banksel_bits
               for i in range (1, self.no_banks+1):
                     decoded_addr='0'*self.no_banks
                     if i!=1:
                                addr=self.add('1',addr)
                     decoded_addr=decoded_addr[0:self.no_banks-i]+'1'+decoded_addr[self.no_banks-i:self.no_banks-1]
                     dfh.write("               %d'b%s: DATA_REQ = %d'b%s;\n"%(self.banksel_bits, addr, self.no_banks, decoded_addr))
               dfh.write("         endcase\n")
               dfh.write("     else if (DATA_REQIN == 0)\n")
               data_req_val = '0'*self.no_banks
               dfh.write("         DATA_REQ = %d'b%s;\n"%(self.no_banks, data_req_val))
               dfh.write("   end\n")
               dfh.write("endmodule\n")
               dfh.close()
               log.info("Successfully generated the verilog file %s"%self.decoder_name)

        def VerilogGen_mux(self):
               '''
                Generates the output multiplexer verilog file.

               '''
               self.mux=os.path.join(self.Verilogrundir,self.mux_name+'.v')
               log.info("Generating the verilog file %s"%self.mux_name)
               mfh=open(self.mux, 'w')
               mfh.write("module %s (DATA_OUT, DATA_IN, DATA_SEL);\n"%self.mux_name)
               mfh.write("   parameter word_size = %d;\n"%self.word_size)
               mfh.write("   parameter no_banks = %d;\n"%self.no_banks)
               mfh.write("   parameter banksel_bits = %d;\n"%self.banksel_bits)
               mfh.write("   output [word_size-1:0] DATA_OUT;\n")
               mfh.write("   input [word_size-1:0] DATA_IN [no_banks-1:0];\n")
               mfh.write("   input [banksel_bits-1:0] DATA_SEL;\n")
               mfh.write("   reg [word_size-1:0] DATA_OUT;\n")
               DATA_IN_str =''
               for ba in range(0, self.no_banks):
                     DATA_IN_str=DATA_IN_str+"DATA_IN[%d]"%ba
                     DATA_IN_str=DATA_IN_str+' or '
               mfh.write("   always @(%s DATA_SEL) begin\n"%DATA_IN_str)
               mfh.write("        case ( DATA_SEL )\n")
               addr = '0'*self.banksel_bits
               for k in range(0, self.no_banks):
                     if k!=0:
                               addr=self.add('1',addr)
                     mfh.write("                        %d'b%s: DATA_OUT = DATA_IN[%d];\n"%(self.banksel_bits, addr, k))
               default_data_out = 'x'*self.word_size
               mfh.write("                     default: DATA_OUT = %d'b%s;\n"%(self.word_size, default_data_out))
               mfh.write("        endcase\n")
               mfh.write("     end\n")
               mfh.write("endmodule\n")
               mfh.close()
               log.info("Successfully generated the verilog file %s"%self.mux_name)

        def VerilogGen_SRAM(self):
               '''
                Generates the SRAM verilog file.

                '''
               self.sram=os.path.join(self.Verilogrundir,self.sram_name+'.v')
               log.info("Generating the verilog file %s"%self.sram_name)
               sfh=open(self.sram, 'w')
               sfh.write("`timescale 1ns / 1ns\n")
               sfh.write('`include "%s.v"\n'%self.decoder_name)
               sfh.write('`include "%s.v"\n\n\n'%self.mux_name)
               sfh.write("module %s (DOUT, ADDR, CLK, DBE, CEN, DIN, WE);\n"%self.sram_name)
               sfh.write("   parameter address_size = %d;\n"%self.address_size)
               sfh.write("   parameter no_banks = %d;\n"%self.no_banks)
               sfh.write("   parameter bank_address_size = %d;\n"%self.bank_address_size)
               sfh.write("   parameter word_size    = %d;\n"%self.word_size)
               sfh.write("   input  CLK, CEN,  WE;\n")
               sfh.write("   input [3:0]  DBE;\n")
               sfh.write("   input [address_size-1:0]  ADDR;\n")
               sfh.write("   input [word_size-1:0]  DIN;\n")
               sfh.write("   output [word_size-1:0]  DOUT;\n")
               sfh.write("   wire  [no_banks-1:0]  DATA_REQ;\n")
               sfh.write("   wire [word_size-1:0] DATA_SRAM_BANK_OUT [no_banks-1:0];\n")
               sfh.write("   %s DI (.DATA_REQ(DATA_REQ), .ADDR(ADDR[address_size-1:bank_address_size]), .DATA_REQIN(CEN));\n"%(self.decoder_name))
               for j in range(0, self.no_banks):
                     sfh.write("   SRAM_2KB SR%d ( .DOUT(DATA_SRAM_BANK_OUT[%d]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[%d]), .DIN(DIN), .WE_IN(WE));\n"%(j, j, j))
               sfh.write("   %s MI (.DATA_OUT(DOUT), .DATA_IN(DATA_SRAM_BANK_OUT), .DATA_SEL(ADDR[address_size-1:bank_address_size]));\n"%(self.mux_name))
               sfh.write("endmodule\n")
               sfh.close()
               log.info("Successfully generated the verilog file %s"%self.sram_name)

        def DataPrep(self):
               '''
                Prepares all the required data for running the synthesis and PNR.

               ''' 
               log.info("Preparing the Data for running the synthesis and PNR")
               if not os.path.isdir(self.digitalflowsrcdir):
                     log.info("The dir %s  does not exists"%self.digitalflowsrcdir)
                     try:
                          log.info("Creating the directory %s"%self.digitalflowsrcdir)
                          os.mkdir(self.digitalflowsrcdir)
                     except OSError:
                          log.error("Unable to create the %s directory"%self.digitalflowsrcdir)
                          log.error("Can not proceed to synthesis and PNR. Exiting.....")
                          sys.exit(1)

               try:
                        shutil.copy(self.sram, self.digitalflowsrcdir)
               except IOError as e:
                        log.error("Unable to copy the file to %s under the digital flow source directory %s"%(self.sram, self.digitalflowsrcdir))
                        if not os.path.exists(self.sram):
                                log.error("%s verilog is not created. Check the run log for the errors"%self.sram)
                                log.error("SRAM  generation failed. Check the log file for more information.")
                                sys.exit(1)
               try:
                        shutil.copy(self.decoder, self.digitalflowsrcdir)
               except IOError as e:
                        log.error("Unable to copy the file to %s under the digital flow source directory %s"%(self.decoder, self.digitalflowsrcdir))
                        if not os.path.exists(self.decoder):
                                log.error("%s verilog is not created. Check the run log for the errors"%self.decoder)
                                log.error("Decoder generation failed. Check the log file for more information.")
                                sys.exit(1)
               try:
                        shutil.copy(self.mux, self.digitalflowsrcdir)
               except IOError as e:
                        log.error("Unable to copy the file to %s under the digital flow source directory %s"%(self.mux, self.digitalflowsrcdir))
                        if not os.path.exists(self.mux):
                                log.error("%s verilog is not created. Check the run log for the errors"%self.mux)
                                log.error("Multiplexer generation failed. Check the log file for more information.")
                                sys.exit(1)
               # Update the design name and platfrom
               log.info("Updating the include.mk file")
               with open(self.digitalflowdir + '/include.mk', 'r') as file:
                     filedata = file.read()
                     filedata = re.sub(r'export DESIGN_NAME :=.*', r'export DESIGN_NAME := ' + \
                     self.sram_name, filedata)
                     filedata = re.sub(r'export PLATFORM *:=.*', r'export PLATFORM    := ' + \
                     p_options["PDK"], filedata)
               with open(self.digitalflowdir + '/include.mk', 'w') as file:
                     file.write(filedata)
               # Update the verilog file list for Synthesis
               with open(self.digitalflowdir + '/scripts/dc/dc.filelist.tcl', 'r') as file:
                     filedata = file.read()
                     sourcefile = "./src/"+self.sram_name+'.v'
                     filedata = re.sub(r'set SVERILOG_SOURCE_FILES ".*"', r'set SVERILOG_SOURCE_FILES "' + sourcefile + '\"', filedata)
               with open(self.digitalflowdir + '/scripts/dc/dc.filelist.tcl', 'w') as file:
                     file.write(filedata)
               # Load json config file
               log.info('Loading platform_config file...')
               try:
                     with open(self.Fasocdir+'/config/platform_config.json') as file:
                          platformConfig = json.load(file)
               except ValueError as e:
                     log.error('Error occurred opening or loading json file.')
                     log.error('Exception: %s' % str(e))
                     sys.exit(1)
               digitalflowexprdir=os.path.join(self.digitalflowdir,'blocks/SRAM_2KB/export')
               SRAM_2KB_dir=os.path.join(platformConfig["platforms"][p_options["PDK"]]["aux_lib"],'SRAM_2KB/latest')
               if not os.path.isdir(digitalflowexprdir):
                     os.makedirs(digitalflowexprdir)
               log.info("Copying the SRAM_2KB macro related files to %s dir "%digitalflowexprdir)
               try:
                     files = os.listdir(SRAM_2KB_dir)
                     for f in files:
                         file_name = os.path.join(SRAM_2KB_dir, f)
                         if (os.path.isfile(file_name)):
                                  shutil.copy(file_name, digitalflowexprdir)
               except IOError as e:
                        log.error("Unable to copy the SRAM_2KB library under the directory %s"%(digitalflowexprdir))
                        if not os.path.exists(SRAM_2KB_dir):
                                log.error("%s does not exist. Provide the correct path in the config json file"%SRAM_2KB_dir)
                                sys.exit(1)

        def Synthesis(self):
               '''
                Runs the synthesis.

               '''
               log.info("Running the synthesis for the design %s"%self.sram_name)
               os.chdir(self.digitalflowdir)
               p1=sp.Popen("make synth", shell=True)
               p1.wait()
               # Get the cell area estimate from synthesis report
               with open(self.digitalflowdir + '/reports/dc/' + self.sram_name + '.mapped.area.rpt', 'r')as file:
                   filedata = file.read()
               m = re.search('Total cell area: *([0-9.]*)', filedata)
               if m:
                   self.coreCellArea = float(m.group(1))
                   log.info("Completed the synthesis for the design %s"%self.sram_name)
               else:
                   log.error('Synthesis Failed')
                   sys.exit(1)
               os.chdir(rundir)

        def PNR(self):
               '''
                Runs the PNR.

               '''
               log.info("Running the APR for the design %s"%self.sram_name)
               os.chdir(self.digitalflowdir)
               # Run the APR flow
               p2 = sp.Popen("make design", shell=True)
               p2.wait()

               p3 = sp.Popen(['make','lvs'], shell=True) #CADRE flow is not enabled for tsmc 65 LP DRC and LVS at the moment.
               p3.wait()

               p4 = sp.Popen(['make','drc'], shell=True)
               p4.wait()
               p5 = sp.Popen("make export", shell=True)
               p5.wait()

               with open(self.digitalflowdir + '/reports/innovus/' + self.sram_name + '.main.htm.ascii', 'r') as file:
                   filedata = file.read()
               m = re.search('Total area of Chip: ([0-9.]*)', filedata)
               if m:
                     self.designArea = float(m.group(1))
                     log.info("Completed the APR for the design %s"%self.sram_name)
               else:
                   log.error('APR Failed')
                   sys.exit(1)
               os.chdir(rundir)

        def Filemanage(self):
               # Function that copies all the required outputs to outputs directory from different run directories
               fileName= self.digitalflowdir +'/export/'+self.sram_name
               if p_options['Mode'] == 'verilog':
                       #Verilog files
                       try:
                             shutil.copy(self.decoder, p_options['Opdir'])
                             shutil.copy(self.mux, p_options['Opdir'])
                             shutil.copy(self.sram, p_options['Opdir'])
                       except IOError as e:
                             log.error("Unable to copy the generated verilog files to the outputs dir, %s"%(p_options['Opdir']))
                             if not os.path.exists(self.decoder):
                                        log.error("SRAM decoder verilog is not created.")
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1) 
                             if not os.path.exists(self.mux):
                                        log.error("SRAM Multiplexer verilog is not created.")
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1)
                             if not os.path.exists(self.sram):
                                        log.error("SRAM macro verilog is not created.")
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1)  
                       #Results JSON file generation
                       self.config['results'] = {'platform': p_options['PDK']}
                       mem_x = 310.05 ; #Was in meters, changing the units to micro meters as per the top-level requirements. Sumanth, 9/26/2019
                       mem_y = 198.06 ; #Was in meters, changing the units to micro meters as per the top-level requirements. Sumanth, 9/26/2019
                       BLOCK_OFFSET = 10 ;#Was in meters, changing the units to micro meters as per the top-level requirements. Sumanth, 9/26/2019
                       nofbanks = self.no_banks                         ; # Gets the number of 2KB SRAM memory instances in the top SRAM.
                       cols = nofbanks/2                                  ; # No of 2KB SRAM macro coulmns in the top SRAM.
                       rows=2                                           ; # No of 2KB SRAM macro rows in the top SRAM. Fixed for 2 now.
                       MACROS_WIDTH =  cols*(BLOCK_OFFSET+mem_x+BLOCK_OFFSET) ; 
                       MACROS_HEIGHT = rows*(BLOCK_OFFSET+mem_y+BLOCK_OFFSET) ; # Overall multi-bank macro height.
                       CORE_WIDTH = MACROS_WIDTH
                       CORE_HEIGHT = MACROS_HEIGHT+50 ;#Was in meters, Changing the units to micro meters as per the top-level requirements. Sumanth, 9/26/2019
                       mem_area =  CORE_WIDTH*CORE_HEIGHT
                       mem_ar = CORE_WIDTH/CORE_HEIGHT
                       mem_power =  nofbanks*100e-6*1.2 ;#Was in watts, changing the units to milli watts as per with top-level requirements. Sumanth, 9/26/2019 
                       self.config['results'].update({'area': mem_area}) 
                       self.config['results'].update({'aspect_ratio': str(mem_ar)+':1'})
                       self.config['results'].update({'power': mem_power})
                       self.config['results'].update({'word_size': self.word_size })
                       self.config['results'].update({'nowords': self.nowords})

                       with open(p_options['Opdir'] + '/' + self.sram_name + '.json', 'w') as resultSpecfile:
                          json.dump(self.config, resultSpecfile, indent=True)
 
               elif p_options['Mode'] == 'macro':
                       fileName= self.digitalflowdir +'/export/'+self.sram_name
	               #Verilog files
                       try:
                             vf = fileName+'.lvs.v'
                             shutil.copy(vf, p_options['Opdir'])
                       except IOError as e:
                             log.error("Unable to copy the file %s to the outputs dir, %s"%(vf, p_options['Opdir']))
                             if not os.path.exists(vf):
                                        log.error("%s verilog is not created. Check if the APR is successful and the verilog file is generated. Check the run log"%vf)
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1)
		       #GDS file
                       try:
                             gds = fileName+'.gds.gz'
                             shutil.copy(gds, p_options['Opdir'])
                       except IOError as e:
                                log.error("Unable to copy the file %s to the outputs dir, %s"%(gds, p_options['Opdir']))
                                if not os.path.exists(gds):
                                        log.error("%s GDS is not created. Check if the APR is successful and the GDS is generated. Check the run log"%gds)
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1)
                       #LEF FIles
                       try:
                             lef = fileName+'.lef'
                             shutil.copy(lef, p_options['Opdir'])
                       except IOError as e:
                                log.error("Unable to copy the file %s to the outputs dir, %s"%(lef, p_options['Opdir']))
                                if not os.path.exists(lef):
                                        log.error("%s LEF is not created. Check if the APR is successful and the GDS is generated. Check the run log"%lef)
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1)
                       #LIB File
                       try:
                                lib = fileName+'_min.lib'
                                shutil.copy(lib, p_options['Opdir'])
                       except IOError as e:
                                log.error("Unable to copy the file %s to the outputs dir, %s"%(lib, p_options['Opdir']))
                                if not os.path.exists(lib):
                                        log.error("%s Lib is not created. Check if the APR is successful and the GDS is generated. Check the run log"%lib)
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1)
                       #DB Files
                       try:
                                db = fileName+'_min.db'
                                shutil.copy(db, p_options['Opdir'])
                       except IOError as e:
                                log.error("Unable to copy the file %s to the outputs dir, %s"%(db, p_options['Opdir']))
                                if not os.path.exists(db):
                                        log.error("%s DB is not created. Check if the APR is successful and the GDS is generated. Check the run log"%db)
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1)
                       ''' #CDL #Commented out for now as CADRE is not enabled for calibre DRC and LVS. CDL will generated as part of LVS process.
                       try:
                                cdl = fileName+'.spi'
                                shutil.copy(cdl, p_options['Opdir'])
                       except IOError as e:
                                log.error("Unable to copy the file %s to the outputs dir, %s"%(cdl, p_options['Opdir']))
                                if not os.path.exists(cdl):
                                        log.error("%s Spice netlist is not created. Check if the APR is successful and the GDS is generated. Check the run log"%cdl)
                                        log.error("SRAM Macro Generation Failed. Check the log file for more information.")
                                        sys.exit(1) '''

                       #Results JSON file generation
                       self.config['results'] = {'platform': p_options['PDK']}
                       #self.config['results'].update({'area': self.designArea})
                       mem_x = 310.05 ;#Was in meters, changing the units to micro meters as per the top-level requirements. Sumanth, 9/26/2019
                       mem_y = 198.06 ;#Was in meters, changing the units to micro meters as per the top-level requirements. Sumanth, 9/26/2019
                       BLOCK_OFFSET = 10 ;#Was in meters, changing the units to micro meters as per the top-level requirements. Sumanth, 9/26/2019
                       nofbanks = self.no_banks                         ; # Gets the number of 2KB SRAM memory instances in the top SRAM.
                       cols = nofbanks/2                                  ; # No of 2KB SRAM macro coulmns in the top SRAM.
                       rows=2                                           ; # No of 2KB SRAM macro rows in the top SRAM. Fixed for 2 now.
                       MACROS_WIDTH =  cols*(BLOCK_OFFSET+mem_x+BLOCK_OFFSET) ;
                       MACROS_HEIGHT = rows*(BLOCK_OFFSET+mem_y+BLOCK_OFFSET) ; # Overall multi-bank macro height.
                       CORE_WIDTH = MACROS_WIDTH
                       CORE_HEIGHT = MACROS_HEIGHT+50 ; #Was in meters, changing the units to micro meters as per the top-level requirements. Sumanth, 9/26/2019
                       mem_area =  CORE_WIDTH*CORE_HEIGHT
                       mem_ar = CORE_WIDTH/CORE_HEIGHT
                       mem_power =  nofbanks*100e-6*1.2 ;#Was in watts, changing the units to milli watts as per the top-level requirements. Sumanth, 9/26/2019
                       self.config['results'].update({'area': mem_area})
                       self.config['results'].update({'aspect_ratio': str(mem_ar)+':1'})
                       self.config['results'].update({'power': mem_power})
                       self.config['results'].update({'aspect_ratio': str(mem_ar)+':1'})
                       self.config['results'].update({'power': mem_power})
                       self.config['results'].update({'word_size': self.word_size })
                       self.config['results'].update({'nowords': self.nowords})

                       with open(p_options['Opdir'] + '/' + self.sram_name + '.json', 'w') as resultSpecfile:
                               json.dump(self.config, resultSpecfile, indent=True)
 
        def toolenv(self):
               '''
               Checks the environment of the required tools for running the sims.

               '''
               self.hspicepath=os.popen("which hspice").read().replace('\n','')
               #proc1=sp.Popen(["which", "hspice"])#, shell=True) #.read().replace('\n','')
               #(out1, err1) = proc1.communicate()
               #self.hspicepath=out1.replace('\n','')
               self.spectrepath=os.popen("which spectre").read().replace('\n','')
               self.liberatepath=os.popen("which liberate").read().replace('\n','')
               self.virtuosopath=os.popen("which virtuoso").read().replace('\n','')

               if os.path.exists(self.hspicepath):
                     vli=os.popen("hspice -v").read().split()
                     self.hversion=vli[vli.index("Version")+1]
                     log.info(" Using %s hspice version for the library characterization"%self.hversion)
               elif os.path.exists(self.spectrepath):
                     #vli=os.popen("spectre -V").read().split()
                        #self.sversion=vli[vli.index("version")+1]
                        log.info(" Using spectre  for the library characterization")#%self.sversion)
               else:
                     log.warning("No simulators are set. Lib generation for SRAM might fail...")
               if os.path.exists(self.virtuosopath):
                        #vli=os.popen("spectre -V").read().split()
                        #self.sversion=vli[vli.index("version")+1]
                        log.info(" Using Ocean  for the design space exploration")#%self.sversion)
               else:
                        log.error("OCEAN  is not set. Can not generate the SRAM. Exiting now...")
                        sys.exit(1)
               if os.path.exists(self.spectrepath):
                        #vli=os.popen("spectre -V").read().split()
                        #self.sversion=vli[vli.index("version")+1]
                        log.info(" Using spectre  for the design space exploration")#%self.sversion)
               else:
                        log.error("Spectre simulator is not set. Can not generate the SRAM. Exiting now...")
                        sys.exit(1)

               if os.path.exists(self.liberatepath):
                     #vli=os.popen("liberate -V").read().split()
                        #self.lversion=vli[vli.index("version")+1]
                        log.info(" Using Liberate for Lib characterization")#%self.lversion
               else:
                     log.warning("Liberate is not set. Can not generate Lib files for SRAM ")

        def add(self, x,y):
                '''
                Adds the number x and y and converts the result to a binary number.

                '''
                maxlen = max(len(x), len(y))
                #Normalize lengths
                x = x.zfill(maxlen)
                y = y.zfill(maxlen)
                result = ''
                carry = 0
                for i in range(maxlen-1, -1, -1):
                   r = carry
                   r += 1 if x[i] == '1' else 0
                   r += 1 if y[i] == '1' else 0
                   # r can be 0,1,2,3 (carry + x[i] + y[i])
                   # and among these, for r==1 and r==3 you will have result bit = 1
                   # for r==2 and r==3 you will have carry = 1
                   result = ('1' if r % 2 == 1 else '0') + result
                   carry = 0 if r < 2 else 1
                if carry !=0 : result = '1' + result
                return result.zfill(maxlen)

def main():
        parser=OptionParser()
        parser.add_option('-m','--mode',
                         type='string',
                         dest='Mode',
                         help='''Mode in which MemGen has to run. Supported options are "verilog" and "macro". Default mode is "verilog".
                         Ex: -m macro or --Mode= verilog''',
                         default='verilog')
        parser.add_option('-s','--specfile',
                         type='string',
                         dest='Spec',
                         help='''Configuration file in Json format with Specifications of the memory to be generated.
                         Ex: -c memgen_config.json or --Config= memgen_config.json ''',
                         default='')
        parser.add_option('-o','--outputDir',
                         type='string',
                         dest='Opdir',
                         help='''Output directory: A place holder for all the memory output.
                         Ex: -output ./output/SRAM  or --Output= ./output/SRAM ''',
                         default='')
        parser.add_option('-p','--platform',
                         type='string',
                         dest='PDK',
                         help='''Process Design Kit: The pdk process info in which the memory to be generated. Specify this if CADRE flow is to be used. Else, ignore this option and specify the pdk info with options Node and Foundry.
                         Ex: -platform tsmc65  or --Platform= tsmc65 ''',
                         default='')
        parser.add_option('-n','--Node',
                      type='string',
                      dest='Node',
                      help='''Technology node in which SRAM has to be generated
                      Ex: -n "65nm" or --Node="65nm" ''',
                      default='')
        parser.add_option("--debug",
                     action="store_true",
                     dest='log_debug',
                     help="Setting this value to True enables logging in Debug mode",
                     default=False)
        parser.add_option('-f','--Foundry',
                         type='string',
                         dest='Foundry',
                         help='''Technology foundry in which SRAM has to be generated
                         Ex: -n "tsmc" or --Node="tsmc" ''',
                         default='')
        parser.add_option('-c','--Capacity',
                         type='string',
                         dest='Capacity',
                         help='''Capacity of the SRAM to be generated, mention in bits. For Ex: 2KB, mention as 16384 bits. No units are required
                         Ex: -c "16384" or --Capacity="16384" ''',
                         default='')
        parser.add_option('-w','--Words',
                         type='int',
                         dest='Words',
                         help='''Number of bits per word of the SRAM to be generated. For Ex: 32, 64 No units are required
                         Ex: -w 32 or --Words=64 ''',
                         default=0)
        parser.add_option('-l','--LibGen',
                         type='int',
                         dest='LibGen',
                         help='''Set this option to 1 to generate library files, else set to 0. By default its 1.
                         Ex: -l 1 or --LibGen=1 ''',
                         default=0)
        parser.add_option('-v','--VerilogGen',
                         type='int',
                         dest='VerilogGen',
                         help='''Set this option to 1 to generate the synthesizable verilog files, else set to 0. By default its 1.
                         Ex: -v 1 or --VerilogGen=1 ''',
                         default=1)
        parser.add_option('-t','--Toolenvt',
                         type='int',
                         dest='Toolenvt',
                         help='''Generates the EDA tool env template
                         Ex: -t 1 or --Toolenvt=1 ''',
                         default=0)

        (options,argv)=parser.parse_args()
        global p_options
        p_options = {}
        p_options['Mode']  =options.Mode
        p_options['Config']=options.Spec
        p_options['Opdir']=options.Opdir
        p_options['PDK']=options.PDK
        p_options['Node']=options.Node
        p_options['Foundry']=options.Foundry
        p_options['LibGen']=options.LibGen
        p_options['VerilogGen']=options.VerilogGen
        p_options['Capacity']=options.Capacity
        p_options['Words']=options.Words
        p_options['Toolenvt']=options.Toolenvt
        #Gets the directory structure absoulte paths
        global rundir, ipdir, pydir, Opdir #, tdir, ViProdir
        rundir =  os.getcwd() #Top level directory where MemGen is triggered.
        ipdir  =  os.path.join(rundir, 'inputs') #inputs dir
        pydir   =  os.path.join(rundir, 'bin/tools') #python dir
        #opdir =  os.path.join(rundir, 'outputs') #outputs dir
        #tdir  =  os.path.join(rundir, 'tool_templates') #tool templates dir
        #ViProdir=  os.path.join(rundir, 'ViPro') #TASE dir

        #######################
        ####### LOGGING #######
        #######################

        logFile=os.path.join(rundir, 'MemGen.log')
        if options.log_debug:
               loglevel=logging.DEBUG
        else:
               loglevel=logging.INFO
        logging.basicConfig( filename = logFile, filemode = 'w',format='%(filename)s:%(lineno)d - %(asctime)s - %(levelname)s -> %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
        log.setLevel(loglevel)
        stdouth=logging.StreamHandler(sys.stdout) #Used to direct the logging into log file as well as stdout.
        log.addHandler(stdouth)

        #######################################
        ## Checking the command line options.##
        #######################################

        if not os.access(rundir,os.W_OK):
              log.error('Do not have the write permissions of the run directory %s. Can not run the tool. Hence Exiting...'%rundir)
              log.error('Ensure the %s directory has the write permissions and re-run the tool.'%rundir)
              sys.exit(1)
        if not p_options['Toolenvt']:
               if p_options['Config'] in ['', ' ']:
                        log.error('Configuration file is not specified. Can not determine the specifications to generate the SRAM. Exting....')
                        log.error('Please specify the configuration file and re-run the tool.')
               if not os.path.isfile(p_options['Config']):
                        log.error('The provided config file %s does not exist. Can not proceed further Exiting...')
                        log.error('Provide a valid config file and re-run the MemGen')
                        sys.exit(1)
               if p_options['Opdir'] in ['', ' ']:
                     log.info('The output directory is not specified.')
                     p_options['Opdir'] = os.path.join(rundir, 'outputs')
                     log.info('Using the  %s output directory for storing all the outputs'%Opdir)
                     log.info("Creating the Output dir %s under %s"%(os.path.basename(Opdir), os.path.dirname(Opdir)))
                     os.mkdir(Opdir)
               else:
                     if not os.path.isdir(p_options['Opdir']):
                               log.warning('The specified output dir %s does not exists.'%p_options['Opdir'])
                               if os.access(os.path.dirname(p_options['Opdir']), os.W_OK):
                                       log.info("Creating the Output dir %s under %s"%(os.path.basename(p_options['Opdir']), os.path.dirname(p_options['Opdir'])))
                                       os.mkdir(p_options['Opdir'])
                                       #Opdir=os.path.join(os.path.dirname(Opdir), Outputs)
                               else:
                                       log.error('Unable to create an specified output directory.Can not store the outputs. Exiting... ')
                                       sys.exit(1)
               if p_options['PDK'] in ['', ' ']:
                     log.error('The PDK technology information is not provided. Can not generate the tool. Exting....')
                     log.error('Please specify the trchnology info and re-run the tool.')
                     sys.exit(1)
               elif p_options['PDK'] != 'tsmc65lp':
                     log.error('Currently MemGen supports only TSMC 65nm.')
                     log.error('Provided PDK info is not TSMC 65nm. Exiting the MemGen...')
                     sys.exit(1)
               if not (p_options['Config'] or p_options['PDK']):
                     sys.exit(1)
        MemGen()

if __name__ == '__main__':
        main()
