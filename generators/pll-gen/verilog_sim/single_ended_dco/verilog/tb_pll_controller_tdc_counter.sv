//`include "analog_core.v"
//`include "functions.v"
//`include "pll_controller_tdc_counter.sv"

`timescale 1ns/1ps
module tb_pll_controller_tdc_counter();

	//Parameters
		//DESIGN PARAMETER -km
	parameter NSTG=5;
	parameter NCC=54;
	parameter NFC=336; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 

// ANALOG CORE
	//parameter DCO_FBASE = 0.90e+08;	//scale
	//parameter DCO_OFFSET = 0;
	//parameter DCO_CCW_MAX = NCC-1;	//scale
	//parameter DCO_CSTEP = 8.319144e+05;	//scale
	//parameter DCO_FCW_MAX = NFC-1;	//scale
	//parameter DCO_FSTEP = 8.337365e+03;	//scale
// ANALOG CORE
	parameter DCO_FBASE = 0.86e+09;	//scale
	parameter DCO_OFFSET = 0;
	parameter DCO_CCW_MAX = NCC;	//scale
	//parameter DCO_CSTEP = 60e+06;	//scale
	//parameter DCO_CSTEP = 135e+06;	//scale nominal
	//parameter DCO_CSTEP = 148e+06;	// rfff, cold (3.2GHz)
	parameter DCO_CSTEP = 203e+06;	// rfff, cold (3.2GHz)
//	parameter DCO_CSTEP = 227e+06;	// rfff, cold (1.6GHz)
	parameter DCO_FCW_MAX = NFC;	//scale
	//parameter DCO_FSTEP = 2.4e+06;	//scale
	parameter DCO_FSTEP = 3.6e+06;	// dco5: 3.2GHz
//	parameter DCO_FSTEP = 1.65e+06;	// dco5: 1.6 GHz
	

// testBench variables
	// Window frequency function
	parameter window_pts = 500;
	real window_values [window_pts-1:0];
	real window_avg;

	integer window_ii;

	//real clkref_period = 1/(100.001e6);  //Fref=0.1G => Fvco=2.5G
	real clkref_period = 1/(1.000000e+08);  //Fref=100MHz => Fvco= 3.20GHz
	real kp_real = 0.20;
//	real ki_real = 0e-2;
	real ki_real = kp_real/16;
	integer multiply = 32;
//	integer multiply = 16;

	real max_periods = 550;
	integer periods;

// controller parameters
	parameter TDC_MAX = (NSTG*2-1)*2;	//-km	
	parameter FCW_MAX = 100;  //km for test
	parameter FCW_MIN = 10;
	parameter KP_WIDTH = 12;
	parameter KP_FRAC_WIDTH = 6;
	parameter KI_WIDTH = 12;
	parameter KI_FRAC_WIDTH = 10;
	parameter ACCUM_EXTRA_BITS = 9;
	parameter FILTER_EXTRA_BITS = 4;
	
	parameter integer FINE_LOCK_THSH_MAX = DCO_FCW_MAX/4;	//scale not sure
	parameter integer FINE_LOCK_COUNT_MAX = DCO_FCW_MAX;	//scale not sure
	parameter CAPTURE_WIDTH = 25;

	// TDC_COUNTER
	parameter TDC_NUM_RETIME_CYCLES = 2;
	parameter TDC_NUM_RETIME_DELAYS = 2;
	parameter TDC_NUM_COUNTER_DIVIDERS = 2;

// Local Parameters
	localparam DCO_CCW_WIDTH = $clog2(DCO_CCW_MAX);
	localparam DCO_FCW_WIDTH = $clog2(DCO_FCW_MAX);
	localparam DCO_NUM_PHASES = (TDC_MAX/2+1)/2;
	localparam TDC_WIDTH = $clog2(TDC_MAX);
	localparam FCW_INT_WIDTH = $clog2(FCW_MAX);
	
	localparam FINE_LOCK_THSH_WIDTH = $clog2(FINE_LOCK_THSH_MAX);
	localparam FINE_LOCK_COUNT_WIDTH = $clog2(FINE_LOCK_COUNT_MAX);

	localparam TIME_SCALE = 1e-9;


	integer write_file;
	initial begin
	   write_file = $fopen("pll_lock_report.txt", "w");
	end

	real fine_lock_time;
	real coarse_lock_time;
	logic  	[18:0]					phase_error;
	// Input Signals
	reg						clkref;
	reg 						rst;
	reg 						ctrl_en;
	reg	[FCW_INT_WIDTH-1:0] 			fcw_int;

	reg						dco_open_loop_en;
	reg	[DCO_CCW_WIDTH-1:0]			dco_open_loop_cc;
	reg	[DCO_FCW_WIDTH-1:0] 			dco_open_loop_fc;

	reg						dlf_adjust_en;
	reg	[KP_WIDTH-1:0] 				dlf_lock_kp;
	reg	[KI_WIDTH-1:0] 				dlf_lock_ki;
	reg	[KP_WIDTH-1:0] 				dlf_track_kp;
	reg	[KI_WIDTH-1:0] 				dlf_track_ki;
	reg	[KP_WIDTH-1:0] 				dlf_slew_kp;
	reg	[KI_WIDTH-1:0] 				dlf_slew_ki;

	reg 						fine_lock_enable;	
	reg  	[FINE_LOCK_THSH_WIDTH-1:0]		fine_lock_threshold;
	reg  	[FINE_LOCK_COUNT_WIDTH-1:0]		fine_lock_count;

	reg 	[3:0]					capture_mux_sel;

	reg 						dither_en;
	reg 						ssc_en;
	reg 	[11:0]					ssc_ref_count;
	reg 	[3:0]					ssc_shift;
	reg 	[3:0]					ssc_step;

	// Output Signals
	wire	 					fine_lock_detect;
	wire	[CAPTURE_WIDTH-1:0]			capture_mux_out;

	wire						dco_outp;
	wire						dco_outm;

	// Interconnect
	wire	[DCO_CCW_MAX-1:0]			dco_ccw; //therm
	wire	[DCO_CCW_MAX-1:0]			dco_ccwn; //therm
	wire	[DCO_FCW_MAX-1:0]			dco_fcw;
	wire	[DCO_FCW_MAX-1:0]			dco_fcwn;
	wire	[DCO_CCW_WIDTH-1:0]			dco_ccw_bin; //bin
	wire	[DCO_FCW_WIDTH-1:0]			dco_fcw_bin;
	wire	[DCO_FCW_WIDTH-1:0]			dco_fcw_bin_final;
	wire	[DCO_NUM_PHASES-1:0] 			sampled_phases;
	wire						clkref_delay;
	wire						clkref_retimed;

	reg 						clk_dither;
	reg 						clk_div2;

	// Structural
		pll_controller_tdc_counter 
			`ifndef SYNorAPR
				#(	
					.TDC_MAX(TDC_MAX),
					.FCW_MAX(FCW_MAX),
					.FCW_MIN(FCW_MIN),
					.DCO_CCW_MAX(DCO_CCW_MAX),
					.DCO_FCW_MAX(DCO_FCW_MAX),
					.KP_WIDTH(KP_WIDTH),
					.KP_FRAC_WIDTH(KP_FRAC_WIDTH),
					.KI_WIDTH(KI_WIDTH),
					.KI_FRAC_WIDTH(KI_FRAC_WIDTH),
					.ACCUM_EXTRA_BITS(ACCUM_EXTRA_BITS),
					.FILTER_EXTRA_BITS(FILTER_EXTRA_BITS),
					.FINE_LOCK_THSH_MAX(FINE_LOCK_THSH_MAX),
					.FINE_LOCK_COUNT_MAX(FINE_LOCK_COUNT_MAX),
					.CAPTURE_WIDTH(CAPTURE_WIDTH))
			`endif
			u_pll_controller_tdc_counter (
				.CLKREF_RETIMED(clkref_retimed),
				.RST(rst),
				.FCW_INT(fcw_int),
				.SAMPLED_PHASES_IN(sampled_phases),
				.DCO_OUTP(dco_outp),
				.CLKREF(clkref_delay),
				.DCO_OPEN_LOOP_EN(dco_open_loop_en),
				.DCO_OPEN_LOOP_CC(dco_open_loop_cc),
				.DCO_OPEN_LOOP_FC(dco_open_loop_fc),
				.DLF_ADJUST_EN(dlf_adjust_en),
				.DLF_LOCK_KP(dlf_lock_kp),
				.DLF_LOCK_KI(dlf_lock_ki),
				.DLF_TRACK_KP(dlf_track_kp),
				.DLF_TRACK_KI(dlf_track_ki),
				.FINE_LOCK_ENABLE(fine_lock_enable),
				.FINE_LOCK_THRESHOLD(fine_lock_threshold),
				.FINE_LOCK_COUNT(fine_lock_count),
				.CAPTURE_MUX_SEL(capture_mux_sel ),
				.DITHER_EN(dither_en),
				.CLK_DITHER(clk_div2),

				.SSC_EN(ssc_en),
				.SSC_REF_COUNT(ssc_ref_count),
				.SSC_STEP(ssc_step),
				.SSC_SHIFT(ssc_shift),

				.DCO_CCW_OUT(dco_ccw),
				.DCO_FCW_OUT(dco_fcw),
				.FINE_LOCK_DETECT(fine_lock_detect),
				.CAPTURE_MUX_OUT(capture_mux_out)
		);

		analog_core #(
				.DCO_FBASE(DCO_FBASE),
				.DCO_OFFSET(DCO_OFFSET),
				.DCO_CCW_MAX(DCO_CCW_MAX),
				.DCO_CSTEP(DCO_CSTEP),
				.DCO_FCW_MAX(DCO_FCW_MAX),
				.DCO_FSTEP(DCO_FSTEP),
				.DCO_NUM_PHASES(DCO_NUM_PHASES))
			u_analog_core( 
				.DCO_CCW_IN(dco_ccw_bin), 
				.DCO_FCW_IN(dco_fcw_bin_final),
				.CLKREF(clkref_delay),
				.CLK_DITHER(clk_div2),
				.DCO_OUTP(dco_outp),
				.DCO_OUTM(dco_outm),
				.SAMPLED_PHASES_OUT(sampled_phases)
		);
	
		therm2bin #(.NTHERM(DCO_CCW_MAX), .NBIN(DCO_CCW_WIDTH)) u_t2b1 (.thermin(dco_ccw), .binout(dco_ccw_bin));
		therm2bin #(.NTHERM(DCO_FCW_MAX-1), .NBIN(DCO_FCW_WIDTH)) u_t2b2 (.thermin(dco_fcw[DCO_FCW_MAX-1:1]), .binout(dco_fcw_bin));
		assign dco_fcw_bin_final = dco_fcw_bin + dco_fcw[0];

		// clk dither
		always@(posedge dco_outp) begin
			clk_div2 <= ~clk_div2;
		end

		always@ (posedge clk_div2) begin
			clk_dither <= ~clk_dither;
		end
		// Initialize Everything
			initial
			begin
				`ifdef SYN
					$sdf_annotate("../output/synthesis/PLL_CONTROLLER_TDC_COUNTER.syn.sdf", pll_controller_tdc_counter,,"annotate_syn.log");
					$display("SYN_sdf_file");
				`endif

				`ifdef APR
					$sdf_annotate("../output/apr/pared_PLL_CONTROLLER_TDC_COUNTER.sdf", pll_controller_tdc_counter,,"annotate_apr.log");
				`endif


				$dumpvars; 	
				$dumpfile("ignore_data.vcd");


				periods = 0;

				clkref = 1'b0;
				clk_dither = 1'b0;
				clk_div2 = 1'b0;
				ctrl_en = 1'b1;
				fcw_int = multiply;

				dco_open_loop_en = 0;
				dco_open_loop_cc = 0;
				dco_open_loop_fc = 0;

				dlf_adjust_en = 1;

				dlf_lock_kp = $floor(kp_real*(2**KP_FRAC_WIDTH));
				dlf_lock_ki = $floor(ki_real*(2**KI_FRAC_WIDTH));
				dlf_track_kp = dlf_lock_kp;
				dlf_track_ki = dlf_lock_ki;


				fine_lock_enable = 1;
				//fine_lock_threshold = 2**TDC_WIDTH;
				fine_lock_threshold = 16; // 3.2GHz
				//fine_lock_threshold = 8; // 1.6GHz
				fine_lock_count = 16;

				capture_mux_sel = 3;

				dither_en = 1'b1;

				ssc_en = 1'b0;
				ssc_ref_count = 3030;
				ssc_step = 5;
				ssc_shift = 10;

				//$display(kp_real);
				//$display($itor(dlf_lock_kp)/(2**KP_FRAC_WIDTH));
				//$display(ki_real);				
				//$display($itor(dlf_lock_ki)/(2**KI_FRAC_WIDTH));


				//$finish;

				rst = 1'b0;
				#(clkref_period/TIME_SCALE) rst = 1'b1;
				#(6*clkref_period/TIME_SCALE) rst = 1'b0;
				$display("*** Running verilog simulation for generated PLL_CONTROLLER_TDC_COUNTER");

				#(max_periods*clkref_period/TIME_SCALE)
				$display("*** simulation ended. if fine lock detection didn't appear, try with longer simulation time or debug it");
				 $finish;
			end

		// Create the reference clock
			always begin
				#(clkref_period/TIME_SCALE/2) clkref = ~clkref;
			end
			assign #(1/1e9/TIME_SCALE) clkref_delay = clkref;   //1ns delay
			
			assign phase_error= u_pll_controller_tdc_counter.u_pll_controller.phase_ramp_error_true>>>TDC_WIDTH;

			//windows is to record the frequency changes
		//	always @(posedge dco_outp) begin

		//		window_values[window_pts-1:1] = window_values[window_pts-2:0];  //shift left
		//		window_values[0]= u_analog_core.u_dco_model.frequency;

		//		window_avg = 0;
		//		for (window_ii = window_pts-1;window_ii>=0;window_ii=window_ii-1) begin
		//			window_avg = window_avg + window_values[window_ii]/window_pts;
		//		end
		//		
		//	end

		//	always @(posedge fine_lock_detect) begin
		//		fine_lock_time= $realtime;	
		//		$fwrite(write_file, "fine lock detected on %d ns",fine_lock_time);
		//		$display("*** fine lock detected on %d ns",fine_lock_time);
		//	end
			//always @(posedge u_pll_controller_tdc_counter.u_pll_controller.u_coarse_lock_controller.coarse_lock_detect) begin
			//	coarse_lock_time= $realtime;	
			//	$fwrite(write_file, "coarse lock detected on %d ns\n",coarse_lock_time);
			//end

	endmodule 


module therm2bin (thermin, binout);
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
				bin1 = i;
			end
		end
	end

	always @(bin1) begin
		binout = bin1;
	end

endmodule


//module refclknoise(
//		input logic refclkin,
//		input logic en_refnoise,
//		output logic refclk_out
//		);
//
//
////logic refclkin;
//logic  clk;
//logic clk_refnoise;
//logic clk_refnoise_b;
//logic [31:0] file_counter; // counter for noise freq/period sampling counter
//
//parameter f0 = 0.1;       // GHz based on timescale above , ref clk frequency of 100 Mhz
//parameter phnoiseen = 1;  // Phase noise enable
//parameter noisepsd = -143; // noise PSD in dBc/Hz
//
//
//real jitterPrev;
//real jitter;
//real jitterDiff;
//real noiseSig;
//real noiseScale;
//real temp;
//real refclkfreq;
//integer seed;
//integer file;
//
//initial 
//begin
//  seed = $random % 64;
//  noiseScale = $sqrt( 0.5 * f0 * 1e9 * $pow(10, 0.1 * noisepsd) * 2 ) / (f0 * 6.28); 
//  jitterPrev = 0;
//  jitter = 0;
//  jitterDiff = 0;
//  //refclkin = 0;
//  clk = 0;
//  clk_refnoise = 0;
//  temp = noisepsd;
//  file_counter = 1048000;
//  write_freq_csv(file_counter);
//  refclkfreq = 0.1;
//end
//
//assign refclk_out = en_refnoise ? (clk_refnoise_b):(refclkin);
//assign clk_refnoise_b = ~clk_refnoise;
//
//always @(posedge clk)
//begin
//  noiseSig = $dist_normal(seed, 0, 1e3) * 1e-3; 
//  jitterPrev = jitter;
//  jitter = phnoiseen * noiseScale * noiseSig;
//  jitterDiff = jitter - jitterPrev;
//end
//
//always @(negedge clk)
//begin
//  jitterDiff = 0;
//end
//
//
////default timescale is 1ps/100fs 
//always
//begin
//  #((0.25)*1000/f0) clk <= refclkin;
//end
//
//always
//begin
//  refclkfreq = 1/(1/f0 +jitterDiff);
//  #(((0.5)/f0 + (jitterDiff))*1000) clk_refnoise <= ~clk_refnoise;
//end 
//
//task write_freq_csv(ref logic [31:0] file_counter);
//    file = $fopen("RefClkfreq.csv"); //opening the file
//    $fdisplay(file, "Freq(Hz)");  
//    while(file_counter!=0)
//    begin
//    	@(posedge clk_refnoise)
//	begin
//        	$fdisplay(file," %1.12f,",refclkfreq);
//        	file_counter = file_counter- 32'b1; 
//	end
//    end
//    $fclose(file);    
//endtask     
//
//endmodule
