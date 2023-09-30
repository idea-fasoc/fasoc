import os
import logging
import sys

global log
log=logging.getLogger(__name__)

class MultibankVerilogGen:

    def __init__(self):
        """
         Generates the required verilog files for the SRAM.
        """
        log.info("Generating the verilog modules")
        # time.sleep(5)
        self.Verilogrundir = os.path.join(self.runfilesdir, 'verilog')
        try:
            os.mkdir(self.Verilogrundir)
            os.chdir(self.Verilogrundir)
        except OSError:
            if os.path.exists(self.Verilogrundir):
                log.info("Directory %s already exists" % self.Verilogrundir)
                log.info(" Cleaning up the existing SRAM verilog files")
                os.chdir(self.Verilogrundir)
                evs = li = os.popen("ls *.v*").read().split()  # Existing verilog files
                for l in evs:
                    log.info("Removing %s" % l)
                    os.remove(l)
            else:
                log.error("Unable to create the dir %s, Can not run the VerilogGen. Exitting MemGen.." % self.Verilogrundir)
                sys.exit(1)
        self.decoder_name = "decoder_%dto%d" % (self.decoder_bits, self.no_banks)
        self.mux_name = "mux_%dto1" % self.no_banks
        # self.sram_name    = "SRAM_%dKB"%self.memory_size
        self.VerilogGen_decoder()
        self.VerilogGen_mux()
        self.verilo

        log.info("Successfully completed the generation of all the required verilog modules.")


    def VerilogGen_decoder(self):
        '''
         Generates the SRAM input decoder verilog file.
        '''
        self.decoder = os.path.join(self.Verilogrundir, self.decoder_name + '.v')
        log.info("Generating the verilog file %s" % self.decoder_name)
        dfh = open(self.decoder, 'w')
        dfh.write("module %s (DATA_REQ, ADDR, DATA_REQIN);\n" % self.decoder_name)
        dfh.write("   parameter no_banks = %d;\n" % self.no_banks)
        dfh.write("   parameter banksel_bits = %d;\n" % self.banksel_bits)
        dfh.write("   output [no_banks-1:0] DATA_REQ;\n")
        dfh.write("   input  [banksel_bits-1:0] ADDR;\n")
        dfh.write("   input DATA_REQIN;\n")
        dfh.write("   reg [no_banks-1:0] DATA_REQ;\n")
        dfh.write("   always @(DATA_REQIN or ADDR) begin\n")
        dfh.write("     if (DATA_REQIN == 1'b1)\n")
        dfh.write("         case (ADDR)\n")
        addr = '0' * self.banksel_bits
        for i in range(1, self.no_banks + 1):
            decoded_addr = '0' * self.no_banks
            if i != 1:
                addr = self.add('1', addr)
            decoded_addr = decoded_addr[0:self.no_banks - i] + '1' + decoded_addr[self.no_banks - i:self.no_banks - 1]
            dfh.write(
                "               %d'b%s: DATA_REQ = %d'b%s;\n" % (self.banksel_bits, addr, self.no_banks, decoded_addr))
        dfh.write("         endcase\n")
        dfh.write("     else if (DATA_REQIN == 0)\n")
        data_req_val = '0' * self.no_banks
        dfh.write("         DATA_REQ = %d'b%s;\n" % (self.no_banks, data_req_val))
        dfh.write("   end\n")
        dfh.write("endmodule\n")
        dfh.close()
        log.info("Successfully generated the verilog file %s" % self.decoder_name)


    def veriloggen_mux(self):
        '''
         Generates the output multiplexer verilog file.

        '''
        self.mux = os.path.join(self.Verilogrundir, self.mux_name + '.v')
        log.info("Generating the verilog file %s" % self.mux_name)
        mfh = open(self.mux, 'w')
        mfh.write("module %s (DATA_OUT, DATA_IN, DATA_SEL);\n" % self.mux_name)
        mfh.write("   parameter word_size = %d;\n" % self.word_size)
        mfh.write("   parameter no_banks = %d;\n" % self.no_banks)
        mfh.write("   parameter banksel_bits = %d;\n" % self.banksel_bits)
        mfh.write("   output [word_size-1:0] DATA_OUT;\n")
        mfh.write("   input [word_size-1:0] DATA_IN [no_banks-1:0];\n")
        mfh.write("   input [banksel_bits-1:0] DATA_SEL;\n")
        mfh.write("   reg [word_size-1:0] DATA_OUT;\n")
        DATA_IN_str = ''
        for ba in range(0, self.no_banks):
            DATA_IN_str = DATA_IN_str + "DATA_IN[%d]" % ba
            DATA_IN_str = DATA_IN_str + ' or '
        mfh.write("   always @(%s DATA_SEL) begin\n" % DATA_IN_str)
        mfh.write("        case ( DATA_SEL )\n")
        addr = '0' * self.banksel_bits
        for k in range(0, self.no_banks):
            if k != 0:
                addr = self.add('1', addr)
            mfh.write("                        %d'b%s: DATA_OUT = DATA_IN[%d];\n" % (self.banksel_bits, addr, k))
        default_data_out = 'x' * self.word_size
        mfh.write("                     default: DATA_OUT = %d'b%s;\n" % (self.word_size, default_data_out))
        mfh.write("        endcase\n")
        mfh.write("     end\n")
        mfh.write("endmodule\n")
        mfh.close()
        log.info("Successfully generated the verilog file %s" % self.mux_name)


    def generate_multi_bank_top_module(self, p_options):
        """
         Generates the SRAM verilog file.
         """
        self.sram = os.path.join(self.Verilogrundir, self.sram_name + '.v')
        log.info("Generating the verilog file %s" % self.sram_name)
        sfh = open(self.sram, 'w')
        sfh.write("`timescale 1ns / 1ns\n")
        sfh.write('`include "%s.v"\n' % self.decoder_name)
        sfh.write('`include "%s.v"\n\n\n' % self.mux_name)
        if p_options['PDK'] == 'gf12lp':
            sfh.write("module %s (DOUT, ADDR, CLK, CEN, DIN, WE);\n" % self.sram_name)
        else:
            sfh.write("module %s (DOUT, ADDR, CLK, DBE, CEN, DIN, WE);\n" % self.sram_name)
        sfh.write("   parameter address_size = %d;\n" % self.address_size)
        sfh.write("   parameter no_banks = %d;\n" % self.no_banks)
        sfh.write("   parameter bank_address_size = %d;\n" % self.bank_address_size)
        sfh.write("   parameter word_size    = %d;\n" % self.word_size)
        sfh.write("   input  CLK, CEN,  WE;\n")
        if p_options['PDK'] != 'gf12lp':
            sfh.write("   input [3:0]  DBE;\n")
        sfh.write("   input [address_size-1:0]  ADDR;\n")
        sfh.write("   input [word_size-1:0]  DIN;\n")
        sfh.write("   output [word_size-1:0]  DOUT;\n")
        sfh.write("   wire  [no_banks-1:0]  DATA_REQ;\n")
        sfh.write("   wire [word_size-1:0] DATA_SRAM_BANK_OUT [no_banks-1:0];\n")
        sfh.write("   %s DI (.DATA_REQ(DATA_REQ), .ADDR(ADDR[address_size-1:bank_address_size]), .DATA_REQIN(CEN));\n" % (
            self.decoder_name))
        for j in range(0, self.no_banks):
            if p_options['PDK'] == 'gf12lp':
                sfh.write(
                    "   SRA SR%d ( .DOUT(DATA_SRAM_BANK_OUT[%d]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .CE_IN(DATA_REQ[%d]), .DIN(DIN), .WE_IN(WE));\n" % (
                    j, j, j))
            else:
                sfh.write(
                    "   SRAM SR%d ( .DOUT(DATA_SRAM_BANK_OUT[%d]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[%d]), .DIN(DIN), .WE_IN(WE));\n" % (
                    j, j, j))
        sfh.write(
            "   %s MI (.DATA_OUT(DOUT), .DATA_IN(DATA_SRAM_BANK_OUT), .DATA_SEL(ADDR[address_size-1:bank_address_size]));\n" % (
                self.mux_name))
        sfh.write("endmodule\n")
        sfh.close()
        log.info("Successfully generated the verilog file %s" % self.sram_name)