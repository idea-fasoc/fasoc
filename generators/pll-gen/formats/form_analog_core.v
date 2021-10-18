// verilog
`ifndef __ANALOG_CORE__
`define __ANALOG_CORE__


//`timescale 1ns/1ps
//`timescale 1ps/1ps

//`include "dco_model.v"
//`include "dco_model_noise.v"

@@ module @DN( 
	PH_out, 
	CC, // thermal 
	FC, // thermal 
	FCB, // thermal 
	osc_en, 
	CLK_OUT, 
	SCPA_CLK, 
	clk, 
	dum_in, 
	dum_out);

	// Functions
//	`include "functions.v"


	// Parameters
		parameter TIME_SCALE = 1e-12;
		parameter NSTG=5;
		parameter NCC=24;
		//parameter NFC=16; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 
		parameter NFC=28; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 
		parameter DCO_CCW_MAX = NCC*NSTG;	//scale
		parameter DCO_FCW_MAX = NFC*NSTG*2;	//scale
		parameter DCO_FCW_MAX_H = NFC*NSTG*1;	//scale

		// DCO Base operating frequency
		parameter DCO_CENTER_FREQ = 2.4e9;
		parameter DCO_FBASE = 2.30e+09;	//scale
		parameter DCO_OFFSET = 0;
		parameter DCO_VT_VARIATION = 150e6;

		// resolutions 
		parameter DCO_CSTEP = 3.5e+06;	// ble_test 
		parameter DCO_FSTEP = 180e+03;	// ble_test 

		// DCO number of phases
		parameter DCO_NUM_PHASES = NSTG;

	// Local Parameters
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);

	// Ports
		input 	[DCO_CCW_MAX-1: 0] 		CC;
		input 	[DCO_FCW_MAX_H-1: 0] 		FC;
		input 	[DCO_FCW_MAX_H-1: 0] 		FCB;
		input					osc_en; 
		input					clk; 
		input					dum_in;
 
		output reg	[DCO_NUM_PHASES-1:0]	PH_out; 
		output					CLK_OUT; 
		output					SCPA_CLK; 
		output					dum_out;


	// Internal Signals
		wire 	[DCO_NUM_PHASES-1:0] 		phases;
		reg 	[DCO_CCW_WIDTH-1: 0] 		dco_ccw_bin;
		reg 	[DCO_FCW_WIDTH-1: 0] 		dco_fcw_bin;
		reg 	[DCO_FCW_MAX-1:0]		dco_fcw_fcbw_merged;


	// Variables
		real vt_variation;


		assign dco_fcw_fcbw_merged = {FCB,~FC};
	
		therm2bin #(.NTHERM(DCO_CCW_MAX), .NBIN(DCO_CCW_WIDTH)) u_t2b2 (.thermin(CC), .binout(dco_ccw_bin));
		scat_therm2bin #(.NTHERM(DCO_FCW_MAX), .NBIN(DCO_FCW_WIDTH)) u_t2b3 (.thermin(dco_fcw_fcbw_merged), .binout(dco_fcw_bin));

	// Structural
		//dco_model #(
		dco_model_noise #(
				.TIME_SCALE(TIME_SCALE),
				.DCO_CENTER_FREQ(DCO_CENTER_FREQ), 
				.DCO_FBASE(DCO_FBASE), 
				.DCO_OFFSET(DCO_OFFSET),
				.DCO_VT_VARIATION(DCO_VT_VARIATION),
				.DCO_CCW_MAX(DCO_CCW_MAX), 
				.DCO_CSTEP(DCO_CSTEP),
				.DCO_FCW_MAX(DCO_FCW_MAX), 
				.DCO_FSTEP(DCO_FSTEP),
				.DCO_NUM_PHASES(DCO_NUM_PHASES))
			u_dco_model ( 
				.DCO_CCW_IN(dco_ccw_bin), 
				.DCO_FCW_IN(dco_fcw_bin), 
				.PHASES_OUT(phases)
		);

		assign CLK_OUT = phases[0];  // test-km
		assign SCPA_CLK = phases[1];  // test-km
		assign PH_out = phases;

	// Behavioral

		initial begin
			vt_variation = 0;
		end


		always @* begin
			u_dco_model.vt_variation = vt_variation;
		end


endmodule

module scat_therm2bin (thermin, binout);
	parameter NBIN = 4;
	parameter NTHERM = 16;
	input [NTHERM-1:0] thermin;
	output logic [NBIN-1:0] binout;
	logic [NBIN-1:0] bin1;
	
	integer i;

	always @(thermin) begin
		bin1 = 0;
		for (i=0; i<=NTHERM-1; i=i+1) begin
			if(thermin[i] == 1'b1) begin
				//bin1 = i;
				bin1 = bin1 + 1;
			end
		end
	end

	always @(bin1) begin
		binout = bin1;
	end

endmodule

`endif
