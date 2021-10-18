// tb_pll_top
`ifdef SYN
	`define SYNorAPR
`elsif APR
	`define SYNorAPR
`endif

//`define BEH_SIM
@@	`define @vo

// default: long-sim
//`define SHORT_SIM 
//`define LONG_SIM 
//`define MID_SIM 

//`timescale 1ps/1ps
`timescale 1ps/1fs
module tb_pll_top ();

// testBench variables
	integer iii;
	integer file;
	integer file2;
	integer file3;
	integer file_calib;
	real file_calib_flag;
	real fcw_real;
	real fcw_frac_real;
@@		real clkref_period = 1/(@rf);  // ble_test 40MHz => 2.400250G
	real pre_fb_delay_0;
	real pre_fb_delay_1;
	real pre_fb_delay_2;
	real pre_fb_delay_3;
	real pre_fb_delay_4;
	real pre_ref_delay;
	real phase_noise_accum;
	real phase_noise_accum_fr;
	real phase_noise_accum_avg;
	real fref = 1/clkref_period;  // ble_test 40MHz => 2.400250G
	real sim_end = 0;
@@		real kp_real = @kp; // int-N
	//real kp_real = 0.20;
	real ki_real = kp_real/16;
@@		integer multiply = @fc;
	real dco_rise;
	real time_diff; 
	real time_diff_abs; 
	real debug_period = 400;
	real fcw_change_period0 = 400;
	real fsk_duration = 40;
	real fsk_fine_duration = 5;
	real super_max_ref_per = 60000;
	real max_ref_per = 24000;
	real short_ref_per = 2000;
	real mid_ref_per = 15000;

// DCO parameters
@@		parameter NSTG=@ns;
	parameter DCO_NUM_PH = NSTG;
@@		parameter NCC=@nc;
@@		parameter NFC=@nf; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 
	parameter DCO_CCW_MAX = NCC*NSTG;	//scale
	parameter DCO_FCW_MAX = NFC*NSTG*2;	//scale

// tstdc_counter parameters
	parameter TDC_NUM_PHASE_LATCH = 2;
	parameter TDC_NUM_RETIME_CYCLES = 5;
	parameter TDC_NUM_RETIME_DELAYS = 2;
	parameter TDC_NUM_COUNTER_DIVIDERS = 3;
@@			localparam EMBTDC_WIDTH = @ew;
		localparam TDC_WIDTH = EMBTDC_WIDTH;

// pll_controller parameters
	parameter FCW_MAX = 100;  //km for test
	parameter FCW_MIN = 10;
	parameter KP_WIDTH = 12;
	parameter KP_FRAC_WIDTH = 6;
	parameter KI_WIDTH = 12;
	parameter KI_FRAC_WIDTH = 10;
	parameter ACCUM_EXTRA_BITS = 8;
	parameter FILTER_EXTRA_BITS = 4;
	parameter integer FINE_LOCK_THSH_MAX = 20;	//scale not sure
	parameter integer FINE_LOCK_COUNT_MAX = DCO_FCW_MAX;	//scale not sure
	parameter CAPTURE_WIDTH = 25;
	parameter SSC_COUNT_WIDTH = 12;
	parameter SSC_ACCUM_WIDTH = 16;
	parameter SSC_MOD_WIDTH = 5;
	parameter SSC_SHIFT_WIDTH = func_clog2(SSC_ACCUM_WIDTH-1);

// Local Parameters
	localparam DCO_CCW_BIN_WIDTH = func_clog2(DCO_CCW_MAX);
	localparam DCO_FCW_BIN_WIDTH = func_clog2(DCO_FCW_MAX);
	//localparam DCO_CCW_WIDTH = $clog2(DCO_CCW_MAX);
	//localparam DCO_FCW_WIDTH = $clog2(DCO_FCW_MAX);
	//localparam FCW_INT_WIDTH = $clog2(FCW_MAX);
	localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
	localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);
	localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
	localparam FCW_FRAC_WIDTH = 9; // ble_test
	localparam FCW_WIDTH = FCW_INT_WIDTH+FCW_FRAC_WIDTH; // ble_test
	localparam TDC_ROUND_WIDTH = FCW_FRAC_WIDTH; // ble_test
	localparam REF_ACCUM_WIDTH = FCW_WIDTH + ACCUM_EXTRA_BITS;
	localparam TDC_COUNT_ACCUM_WIDTH = REF_ACCUM_WIDTH - FCW_FRAC_WIDTH;	
	localparam TDC_SHIFT=FCW_FRAC_WIDTH-TDC_WIDTH;	
	//localparam FINE_LOCK_THSH_WIDTH = $clog2(FINE_LOCK_THSH_MAX);
	//localparam FINE_LOCK_COUNT_WIDTH = $clog2(FINE_LOCK_COUNT_MAX);
	localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
	localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);


	// ports
	logic						CLK_REF;
	logic						RST;
	logic	[DCO_NUM_PH*2-1:0][TDC_WIDTH-1:0]	EMBTDC_LUT;

	// pll_controller
	logic 		[FCW_INT_WIDTH-1:0] 		FCW_INT;
	logic 		[FCW_FRAC_WIDTH-1:0]		FCW_FRAC;  
	logic 		[DCO_CCW_WIDTH +
	      			 DCO_FCW_WIDTH-1:0]	DCO_OPEN_LOOP_CTRL;
	logic 						FINE_LOCK_ENABLE;	
	logic  	[FCW_WIDTH-1:0]				FINE_LOCK_THRESHOLD;
	logic						DCO_OPEN_LOOP_EN;	// switch between open and close loop
	logic	[KP_WIDTH-1:0]				DLF_KP;
	logic	[KI_WIDTH-1:0] 				DLF_KI;
	logic	[3:0] 					CAPTURE_MUX_SEL;
	logic						DITHER_EN;
	logic  	[FCW_WIDTH-1:0]				FREQ_LOCK_THRESHOLD;
	logic  	[FINE_LOCK_COUNT_WIDTH-1:0]		FREQ_LOCK_COUNT;
	logic  	[FINE_LOCK_COUNT_WIDTH-1:0]		FINE_LOCK_COUNT;
	logic 						SSC_EN;
	logic 	[11:0]					SSC_REF_COUNT;
	logic 	[3:0]					SSC_SHIFT;
	logic 	[3:0]					SSC_STEP;
	logic 		[DCO_FCW_BIN_WIDTH-1:0]		DCO_FCW_MAX_LIMIT;	
	logic	 					DCO_CCW_OV;
	logic 		[DCO_CCW_BIN_WIDTH-1:0]		DCO_CCW_OV_VAL;

	// outputs 
	logic [2:0]					ns_pll;
	logic [2:0] 					cs_pll;
	logic						DCO_FCW_MAX_LIMIT_HIT;
	logic						FINE_LOCK_DETECT;	// OUTPUT: lock detect; goes high when error is within lock_thsh; also if goes high; PLL switches to slow mode. 
	logic						PLL_LOCKED;	        // high when OPERATE state & FINE_LOCK_DETECT 
	logic 	[CAPTURE_WIDTH-1 :0]			CAPTURE_MUX_OUT;
	logic						CLK_OUT;

	// dco
	logic						OSC_EN;
   	logic 						SCPA_CLK_EN;
   	logic 						CLK_OUT_EN;
   	logic [8:0] 					DIV_SEL;

	// internal probe
	logic signed	[REF_ACCUM_WIDTH-1:0]		ref_phase_ramp_int;
	logic signed	[REF_ACCUM_WIDTH-1:0]		ref_phase_ramp_frac;
	logic signed	[REF_ACCUM_WIDTH-1:0]		dco_phase_ramp_frac;
	logic signed	[REF_ACCUM_WIDTH-1:0]		phase_error_int;
	logic signed	[REF_ACCUM_WIDTH-1:0]		phase_error_frac;
	logic signed	[REF_ACCUM_WIDTH-1:0]		phase_ramp_error_int;

	// 2d mapping
	logic	[DCO_NUM_PH*2*TDC_WIDTH-1:0] 			embtdc_lut_2d;
   	logic [23:0] 					dco_phase_ramp_d;
   	logic [23:0] 					dco_phase_ramp_int;
   	logic [23:0] 					dco_phase_ramp_diff_int;
   	logic [23:0] 					dco_phase_ramp_d_d;
   	logic [23:0] 					dco_phase_ramp_diff;
   	logic [23:0] 					dco_phase_ramp_diff_diff;
   	logic [24:0] 					dco_phase_ramp_diff_d;

	logic 		[DCO_FCW_BIN_WIDTH-1:0]		DCO_FCW_OV_VAL; // 060221
	logic 						DCO_FCW_OV; // 060221
	logic	[FCW_FRAC_WIDTH-1:0]			embtdc_offset_user; // v 060121
	logic						EMBTDC_OFFSET_OV; 
	logic						EDGE_CNT_OV;
	logic	[2:0]					edge_cnt_user; // ^ 060121
	logic	 	CS_PLL_OV; // v 053121
	logic [2:0] 	cs_pll_user;
	logic        	CS_PLL_CTRL_OV;
	logic [1:0] 	cs_pll_ctrl_user;
	logic        	CS_TSTDC_OV;
	logic [2:0] 	cs_tstdc_user; // ^ 
	logic [1:0] 				cs_pll_ctrl; // 053121

	// time scale
	localparam TIME_SCALE = 1e-12;

@@		@pn	u_pll_top(
	// inputs
		.CLK_REF			(CLK_REF		),
		.RST			(RST			),
		`ifdef APR
			.EMBTDC_LUT		(embtdc_lut_2d	),
		`else
			.EMBTDC_LUT		(EMBTDC_LUT	),
		`endif
                                                                 
	// pll_c.ontroller                
		.FCW_INT			(FCW_INT		),			// integer FCW to the PLL 
		.FCW_FRAC		(FCW_FRAC		),			// fractional FCW to the PLL, not tested yet 
		.DCO_OPEN_LOOP_CTRL	(DCO_OPEN_LOOP_CTRL	),	// combined CW to the DCO, only valid in open loop    
		.DCO_OPEN_LOOP_EN	(DCO_OPEN_LOOP_EN	),	// switch between open and close loop
		.DLF_KP			(DLF_KP			),		// loop filter Kp for slow mode 
		.DLF_KI			(DLF_KI			),		// loop filter Ki for slow mode
		.CAPTURE_MUX_SEL		(CAPTURE_MUX_SEL	),	// Select among different internal signals to view for testing purposes.
		.DITHER_EN		(DITHER_EN		),
		.FINE_LOCK_ENABLE	(FINE_LOCK_ENABLE	),
		.FINE_LOCK_THRESHOLD	(FINE_LOCK_THRESHOLD	),
		.FREQ_LOCK_THRESHOLD	(FREQ_LOCK_THRESHOLD	),
		.FREQ_LOCK_COUNT		(FREQ_LOCK_COUNT	),
		.FINE_LOCK_COUNT		(FINE_LOCK_COUNT	),
		.SSC_EN			(SSC_EN			),
		.SSC_REF_COUNT		(SSC_REF_COUNT		),
		.SSC_SHIFT		(SSC_SHIFT		),
		.SSC_STEP		(SSC_STEP		),
		.DCO_CCW_OV_VAL		(DCO_CCW_OV_VAL		),
		.DCO_CCW_OV		(DCO_CCW_OV		),
		.DCO_FCW_MAX_LIMIT	(DCO_FCW_MAX_LIMIT	), 		// valid range of FCW
                                                                 
		.DCO_FCW_OV_VAL		(DCO_FCW_OV_VAL		), // v 0602
		.DCO_FCW_OV		(DCO_FCW_OV		), // ^ 0602
		.EMBTDC_OFFSET_OV	(EMBTDC_OFFSET_OV	), // v 0601
		.embtdc_offset_user	(embtdc_offset_user	), 
		.CS_PLL_OV		(CS_PLL_OV		), // v 0531
		.cs_pll_user		(cs_pll_user		),
		.CS_PLL_CTRL_OV		(CS_PLL_CTRL_OV		),
		.cs_pll_ctrl_user	(cs_pll_ctrl_user	),
                                                                 
	// outpu.ts                       ts
		.cs_pll			(cs_pll			),
		.cs_pll_ctrl		(cs_pll_ctrl		), // ^ 053121
		.ns_pll			(ns_pll			),
		.DCO_FCW_MAX_LIMIT_HIT	(DCO_FCW_MAX_LIMIT_HIT	), 		// valid range of FCW
		.FINE_LOCK_DETECT	(FINE_LOCK_DETECT	),	// OUTPUT: lock detect, goes high when error is within lock_thsh, also if goes high, PLL switches to slow mode.
		.PLL_LOCKED		(PLL_LOCKED		), 
		.CAPTURE_MUX_OUT		(CAPTURE_MUX_OUT	),	// OUTPUT: The internal signal selected to view as an output.
		.CLK_OUT			(CLK_OUT		),
                                                                 
	// dco                                                   
		.OSC_EN			(OSC_EN			),
		.SCPA_CLK_EN		(SCPA_CLK_EN		), 
		.CLK_OUT_EN		(CLK_OUT_EN		), 
		.DIV_SEL			(DIV_SEL		));

	// map the luts
	genvar i;
	generate
		for (i=0; i<DCO_NUM_PH*2; i=i+1) begin
			assign embtdc_lut_2d[TDC_WIDTH*(i+1)-1:TDC_WIDTH*i] = EMBTDC_LUT[i];
		end
	endgenerate


	`ifndef APR
		assign phase_error_int=u_pll_top.u_pll_controller.phase_ramp_error_true>>>FCW_FRAC_WIDTH;
		assign phase_error_frac=u_pll_top.u_pll_controller.phase_ramp_error_true[FCW_FRAC_WIDTH-1:0];
		assign ref_phase_ramp_int=u_pll_top.u_pll_controller.ref_phase_ramp_shifted>>>FCW_FRAC_WIDTH;
		//assign dco_phase_ramp_int=u_pll_top.u_pll_controller.dco_phase_ramp_diff>>>FCW_FRAC_WIDTH;
		assign ref_phase_ramp_frac=u_pll_top.u_pll_controller.ref_phase_ramp_shifted[FCW_FRAC_WIDTH-1:0];
		assign dco_phase_ramp_frac=u_pll_top.u_pll_controller.dco_phase_ramp_diff[FCW_FRAC_WIDTH-1:0];
		
		assign phase_ramp_error_int=u_pll_top.u_pll_controller.phase_ramp_error>>>FCW_FRAC_WIDTH;
		assign dco_phase_ramp_int=u_pll_top.u_pll_controller.dco_phase_ramp_d>>>FCW_FRAC_WIDTH;
		assign dco_phase_ramp_diff_int=u_pll_top.u_pll_controller.dco_phase_ramp_diff>>>FCW_FRAC_WIDTH;
		assign dco_phase_ramp_diff=u_pll_top.u_pll_controller.dco_phase_ramp_diff;

		always @(negedge u_pll_top.u_pll_controller.CLKREF_RETIMED) begin
			dco_phase_ramp_diff_d <=dco_phase_ramp_diff;
		end

		assign dco_phase_ramp_diff_diff = dco_phase_ramp_diff - dco_phase_ramp_diff_d;
		
	`endif

	`ifdef SYN
		always @(posedge u_pll_top.u_pll_controller.CLKREF_RETIMED) begin
			dco_phase_ramp_d <= u_pll_top.u_pll_controller.dco_phase_ramp_d;
			dco_phase_ramp_d_d <= dco_phase_ramp_d;
		end
		assign dco_phase_ramp_diff=dco_phase_ramp_d - dco_phase_ramp_d_d;
	`endif
	`ifdef APR
		//always @(posedge u_pll_top.u_pll_controller.CLKREF_RETIMED) begin
		always @(posedge u_pll_top.u_pll_controller.clkref_retimed) begin
			dco_phase_ramp_d <= u_pll_top.u_pll_controller.dco_phase_ramp_d;
			dco_phase_ramp_d_d <= dco_phase_ramp_d;
		end
		assign dco_phase_ramp_diff=dco_phase_ramp_d - dco_phase_ramp_d_d;
	`endif
	// Create the reference clock
		always begin
			#(clkref_period/TIME_SCALE/2) CLK_REF = ~CLK_REF;
		end

		//assign fcw_real = {FCW_INT,FCW_FRAC}/2**FCW_FRAC_WIDTH;
		assign fcw_real = FCW_INT + fcw_frac_real/2**FCW_FRAC_WIDTH;
	// Initialize Everything
		initial
			begin
			`ifdef SYN
				$sdf_annotate("./synVerilog/pll_top.mapped.sdf", u_pll_top);
				$display("SYN_sdf_file");
			`endif
			`ifdef APR
				$sdf_annotate("./aprVerilog/pll_top.sdf", u_pll_top,,"annotate_apr.log","maximum");
				$display("APR_sdf_file");
				`ifdef TDC_APR
					$sdf_annotate("./../tdc_counter_v2/aprVerilog/tdc_counter.sdf", u_pll_top.u_tdc_counter,,"annotate_apr.log","maximum");
					$display("TDC APR_sdf_file");
				`endif
			`endif
			//$dumpfile("pllFreq.vcd");

			// debug_testing		
			CS_PLL_OV = 0; // v 053121
			EMBTDC_OFFSET_OV = 0; // ^ 060121
			CS_PLL_CTRL_OV = 0;
			DCO_CCW_OV = 0;
			DCO_FCW_OV = 0; // ^ 053121
			embtdc_offset_user = 0; // v 060121
			cs_pll_user = 3;
			cs_pll_ctrl_user = 2; // phase track state
			DCO_CCW_OV_VAL = 26; // ^ 053121
			DCO_FCW_OV_VAL = 10; // ^ 053121

			file_calib_flag = 0;
			phase_noise_accum = 0;
			phase_noise_accum_avg = 0;
			OSC_EN = 1;	
   			SCPA_CLK_EN = 1;
   			CLK_OUT_EN = 0;
   			DIV_SEL = 0;

			// LUTs	
			//EMBTDC_LUT[0]= 1;
			//EMBTDC_LUT[1]= 4; 
			//EMBTDC_LUT[2]= 7;
			//EMBTDC_LUT[3]= 10;
			//EMBTDC_LUT[4]= 13;
			//EMBTDC_LUT[5]= 16;
			//EMBTDC_LUT[6]= 19; 
			//EMBTDC_LUT[7]= 22;
			//EMBTDC_LUT[8]= 25;
			//EMBTDC_LUT[9]= 28;
@@				EMBTDC_LUT[@ei]= @ev;

			FCW_FRAC = 0;
			fcw_frac_real = 0;

			// pll_controller
			DCO_FCW_MAX_LIMIT = DCO_FCW_MAX*3/4;	
			
			FCW_INT = multiply;
			DCO_OPEN_LOOP_CTRL = 0;
			DCO_OPEN_LOOP_EN = 0;
			DLF_KP = $floor(kp_real*(2**KP_FRAC_WIDTH));
			DLF_KI = $floor(ki_real*(2**KI_FRAC_WIDTH));
			//DLF_KP = 12'b0000_0111_1110; 
			//DLF_KI = 12'b0000_0111_1110; 
			CAPTURE_MUX_SEL = 10;	
			DITHER_EN = 1'b1;	
			FINE_LOCK_ENABLE = 1'b1;	
			//FINE_LOCK_THRESHOLD = 60*2**(TDC_SHIFT); // 3.2GHz
			//FINE_LOCK_THRESHOLD = 5*2**(TDC_SHIFT); // 3.2GHz
@@				FINE_LOCK_THRESHOLD = @fT*2**(TDC_SHIFT); // 3.2GHz
			FINE_LOCK_COUNT = 16;
			//FREQ_LOCK_THRESHOLD = 160*2**(TDC_SHIFT); // 3.2GHz
			//FREQ_LOCK_THRESHOLD = 12*2**(TDC_SHIFT); // 3.2GHz
@@				FREQ_LOCK_THRESHOLD = @FT*2**(TDC_SHIFT); // 3.2GHz
			FREQ_LOCK_COUNT = 16;
			SSC_EN	= 0;	
			SSC_REF_COUNT = 3030;	
			SSC_SHIFT = 10;	
			SSC_STEP = 5;		

			sim_end = 0;
			CLK_REF = 1'b0;

			RST = 1'b0;
			#(1.0*clkref_period/TIME_SCALE) RST = 1'b1;
			#(6.0*clkref_period/TIME_SCALE) RST = 1'b0;
			$display("*** Running verilog simulation for pll_top for BLE");

			`ifdef SHORT_SIM 
				#(short_ref_per*clkref_period/TIME_SCALE)
			`elsif MID_SIM
				#(mid_ref_per*clkref_period/TIME_SCALE)
			`elsif LONG_SIM // super long sim
				#(super_max_ref_per*clkref_period/TIME_SCALE)
			`else // long sim
				#(max_ref_per*clkref_period/TIME_SCALE)
			`endif
			sim_end = 1;
			$finish;
		end

	// write pll frequency
	initial begin: csvWrite
		file = $fopen("pllClkfreq.csv"); //opening the file
		`ifdef EMBTDC_RUN
			file2 = $fopen("dco_fr_noise.csv"); //opening the file
			if (FCW_FRAC==0) begin
				file3 = $fopen("pll_freq_for_noise_embtdc.csv"); //opening the file
			end else begin
				file3 = $fopen("pll_freq_for_noise_embtdc_frac.csv"); //opening the file
			end
		`elsif HTDC_RUN
			file2 = $fopen("dco_fr_noise.csv"); //opening the file
			if (FCW_FRAC==0) begin
				file3 = $fopen("pll_freq_for_noise_htdc.csv"); //opening the file
			end else begin
				`ifdef IDEAL_TDC
					file3 = $fopen("pll_freq_for_noise_htdc_frac_ideal_tdc.csv"); //opening the file
				`else
					file3 = $fopen("pll_freq_for_noise_htdc_frac.csv"); //opening the file
				`endif
			end
		`endif
		//$fdisplay(file, "Freq(Hz)");  
		while(sim_end==0) @(posedge u_pll_top.u_dco.CLK_OUT) begin
		//always @(posedge u_pll_top.u_dco.CLK_OUT) begin
			$fwrite(file,"%1.1f,",u_pll_top.u_dco.u_dco_model.frequency);
			`ifdef EMBTDC_RUN
				$fwrite(file2,"%1.10e,\n",u_pll_top.u_dco.u_dco_model.period_noise_accum);
				$fwrite(file3,"%1.10e,\n",u_pll_top.u_dco.u_dco_model.frequency);
			`elsif HTDC_RUN
				$fwrite(file2,"%1.10e,\n",u_pll_top.u_dco.u_dco_model.period_noise_accum);
				$fwrite(file3,"%1.10e,\n",u_pll_top.u_dco.u_dco_model.frequency);
			`endif
        	  end
		$fclose(file);  
		$fclose(file2);  
		$fclose(file3);  
	end



	// record the time difference
	//always @(posedge u_pll_top.u_dco.PH_out[0] or posedge u_pll_top.u_dco.PH_out[1] or posedge u_pll_top.u_dco.PH_out[2] or posedge u_pll_top.u_dco.PH_out[3] or posedge u_pll_top.u_dco.PH_out[4]) begin
	//	dco_rise = $realtime;
	//end
	always @(posedge u_pll_top.u_dco.PH_out[0]) begin
		dco_rise = $realtime;
	end
	
	always @(posedge CLK_REF) begin
		time_diff=($realtime - dco_rise);
	end

	always @* begin
		if (time_diff > 200) begin
			//time_diff_abs = time_diff - (clkref_period/multiply/TIME_SCALE);
			time_diff_abs = time_diff - (clkref_period/fcw_real/TIME_SCALE);
		end else begin
			time_diff_abs = time_diff;
		end
	end 

endmodule

//module bin2therm (binin, thermout);
//	parameter NBIN = 4;
//	parameter NTHERM = 16;
//	input [NBIN-1:0] binin;
//	output [NTHERM-1:0] thermout;
//
//	generate
//		genvar i;
//		for(i=0; i<=NTHERM-1; i=i+1) begin: thermloop
//			assign thermout[i] = (binin > i) ? 1: 0;
//		end
//	endgenerate
//
//endmodule
//
//module therm2bin (thermin, binout);
//	parameter NBIN = 4;
//	parameter NTHERM = 16;
//	input [NTHERM-1:0] thermin;
//	output logic [NBIN-1:0] binout;
//	logic [NBIN-1:0] bin1;
//	
//	integer i;
//
//	always @(thermin) begin
//		bin1 = 0;
//		for (i=0; i<=NTHERM-1; i=i+1) begin
//			if(thermin[i] == 1'b1) begin
//				//bin1 = i;  // only applicable for thermal: 1000111 => 7
//				bin1 = bin1+1; // counts the total number of 1s: 1000111 => 4
//			end
//		end
//	end
//
//	always @(bin1) begin
//		binout = bin1;
//	end
//
//endmodule
