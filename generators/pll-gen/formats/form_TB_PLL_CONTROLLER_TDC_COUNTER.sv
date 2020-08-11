

//`include "ANALOG_CORE.v"
//
//`ifdef SYN
//	`define SYNorAPR
//`elsif APR
//	`define SYNorAPR
//`endif
//
//`ifdef SYNorAPR
//	`include "sc9_cln65lp_base_rvt_udp.v"
//	`include "sc9_cln65lp_base_rvt.v"
//`endif	
//	
//
//`ifdef SYN
//	`include "PLL_CONTROLLER_TDC_COUNTER.syn.v"
//`elsif APR
//	`include "pared_PLL_CONTROLLER_TDC_COUNTER.v"
//`else
//	`include "PLL_CONTROLLER_TDC_COUNTER.v"
//`endif

`timescale 1ns/1ps
module TB_PLL_CONTROLLER_TDC_COUNTER();


	//Parameters
		//DESIGN PARAMETER -km
@@		parameter NSTG=@ns;
@@		parameter NCC=@nc;
@@		parameter NFC=@nf;
@@		parameter NDRV=@nd;

		// ANALOG CORE
@@		parameter DCO_FBASE = @fb;	//scale
		parameter DCO_OFFSET = 0;
		parameter DCO_CCW_MAX = NSTG*NCC-1;	//scale
@@		parameter DCO_CSTEP = @dc;	//scale
		parameter DCO_FCW_MAX = NSTG*NFC-1;	//scale
@@		parameter DCO_FSTEP = @df;	//scale


		// CONTROLLER
		parameter TDC_MAX = NSTG*4-1;	//-km	
		parameter TDC_EXTRA_BITS = 1;
		//parameter FCW_MAX = 55;
		parameter FCW_MAX = 550;  //km for test
		parameter FCW_MIN = 10;
		parameter KP_WIDTH = 12;
		parameter KP_FRAC_WIDTH = 2;
		parameter KI_WIDTH = 12;
		parameter KI_FRAC_WIDTH = 6;
		parameter ACCUM_EXTRA_BITS = 1;
		parameter FILTER_EXTRA_BITS = 1;
		
		parameter NUM_COARSE_LOCK_REGIONS = 2;
		parameter integer COARSE_LOCK_THSH_MAX = DCO_CCW_MAX/4;	//scale -km
		parameter integer COARSE_LOCK_COUNT_MAX = DCO_CCW_MAX;	//scale not sure -km ???
		parameter integer FINE_LOCK_THSH_MAX = DCO_FCW_MAX/4;	//scale not sure
		parameter integer FINE_LOCK_COUNT_MAX = DCO_FCW_MAX;	//scale not sure
//		parameter COARSE_LOCK_THSH_MAX = 31;	//scale -km
//		parameter COARSE_LOCK_COUNT_MAX = 127;	//scale	-km
//		parameter FINE_LOCK_THSH_MAX = 127;
//		parameter FINE_LOCK_COUNT_MAX = 127;		

		parameter CAPTURE_WIDTH = 25;


		// TDC_COUNTER
		parameter TDC_NUM_RETIME_CYCLES = 2;
		parameter TDC_NUM_RETIME_DELAYS = 2;
		parameter TDC_NUM_COUNTER_DIVIDERS = 2;



	// Local Parameters
		localparam DCO_CCW_WIDTH = $clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = $clog2(DCO_FCW_MAX);
		localparam DCO_NUM_PHASES = TDC_MAX+1;
		localparam TDC_WIDTH = $clog2(TDC_MAX);
		localparam FCW_INT_WIDTH = $clog2(FCW_MAX);
		
		localparam COARSE_LOCK_REGION_WIDTH = $clog2(NUM_COARSE_LOCK_REGIONS);
		localparam COARSE_LOCK_THSH_WIDTH = $clog2(COARSE_LOCK_THSH_MAX);
		localparam COARSE_LOCK_COUNT_WIDTH = $clog2(COARSE_LOCK_COUNT_MAX);

		localparam FINE_LOCK_THSH_WIDTH = $clog2(FINE_LOCK_THSH_MAX);
		localparam FINE_LOCK_COUNT_WIDTH = $clog2(FINE_LOCK_COUNT_MAX);

		localparam TIME_SCALE = 1e-9;


	integer write_file;
	initial begin
	   write_file = $fopen("pll_lock_report.txt", "w");
	end

	real fine_lock_time;
	real coarse_lock_time;

	// Input Signals
		reg 										clkref;
		reg 										rst;
		reg 										ctrl_en;
		reg			[FCW_INT_WIDTH-1:0] 			fcw_int;

		reg 										dco_open_loop_en;
		reg 		[DCO_CCW_WIDTH-1:0]				dco_open_loop_cc;
		reg 		[DCO_FCW_WIDTH-1:0] 			dco_open_loop_fc;

		reg 										dlf_adjust_en;
		reg 		[KP_WIDTH-1:0] 					dlf_slow_kp;
		reg 		[KI_WIDTH-1:0] 					dlf_slow_ki;
		reg 		[KP_WIDTH-1:0] 					dlf_fast_kp;
		reg 		[KI_WIDTH-1:0] 					dlf_fast_ki;
		reg 		[KP_WIDTH-1:0] 					dlf_slew_kp;
		reg 		[KI_WIDTH-1:0] 					dlf_slew_ki;


		reg 										coarse_lock_enable;	
		reg signed 	[COARSE_LOCK_REGION_WIDTH-1:0]	coarse_lock_region_sel;
		reg 	 	[COARSE_LOCK_THSH_WIDTH-1:0]	coarse_lock_threshold;
		reg 	 	[COARSE_LOCK_COUNT_WIDTH-1:0]	coarse_lock_count;


		reg 										fine_lock_enable;	
		reg 	 	[FINE_LOCK_THSH_WIDTH-1:0]		fine_lock_threshold;
		reg 	 	[FINE_LOCK_COUNT_WIDTH-1:0]		fine_lock_count;


		reg 		[3:0]							capture_mux_sel;

		reg 										ssc_en;
		reg 		[11:0]							ssc_ref_count;
		reg 		[3:0]							ssc_shift;
		reg 		[3:0]							ssc_step;

	// Output Signals
		wire 										fine_lock_detect;
		wire		[CAPTURE_WIDTH-1:0]				capture_mux_out;
        
		wire										dco_outp;
		wire										dco_outm;


	// Interconnect
		wire		[DCO_CCW_WIDTH-1:0]				dco_ccw;
		wire		[DCO_FCW_WIDTH-1:0]				dco_fcw;
		wire		[DCO_NUM_PHASES-1:0] 			sampled_phases;
		wire										clkref_delay;



	// Structural
		PLL_CONTROLLER_TDC_COUNTER 
			`ifndef SYNorAPR
				#(	
					.TDC_MAX(TDC_MAX),
					.TDC_EXTRA_BITS(TDC_EXTRA_BITS),
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
					.NUM_COARSE_LOCK_REGIONS(NUM_COARSE_LOCK_REGIONS),
					.COARSE_LOCK_THSH_MAX(COARSE_LOCK_THSH_MAX),
					.COARSE_LOCK_COUNT_MAX(COARSE_LOCK_COUNT_MAX),
					.FINE_LOCK_THSH_MAX(FINE_LOCK_THSH_MAX),
					.FINE_LOCK_COUNT_MAX(FINE_LOCK_COUNT_MAX),
					.CAPTURE_WIDTH(CAPTURE_WIDTH))
			`endif
			pll_controller_tdc_counter (
				.SAMPLED_PHASES_IN(sampled_phases),
				.DCO_OUTP(dco_outp),
				.CLKREF(clkref_delay),
				.RST(rst),
				.FCW_INT(fcw_int),
				.DCO_OPEN_LOOP_EN(dco_open_loop_en),
				.DCO_OPEN_LOOP_CC(dco_open_loop_cc),
				.DCO_OPEN_LOOP_FC(dco_open_loop_fc),
				.DLF_ADJUST_EN(dlf_adjust_en),
				.DLF_SLOW_KP(dlf_slow_kp),
				.DLF_SLOW_KI(dlf_slow_ki),
				.DLF_FAST_KP(dlf_fast_kp),
				.DLF_FAST_KI(dlf_fast_ki),
				.DLF_SLEW_KP(dlf_slew_kp),
				.DLF_SLEW_KI(dlf_slew_ki),
//				.COARSE_LOCK_ENABLE(coarse_lock_enable),
//				.COARSE_LOCK_REGION_SEL(coarse_lock_region_sel),
//				.COARSE_LOCK_THRESHOLD(coarse_lock_threshold),
//				.COARSE_LOCK_COUNT(coarse_lock_count),
				.FINE_LOCK_ENABLE(fine_lock_enable),
				.FINE_LOCK_THRESHOLD(fine_lock_threshold),
				.FINE_LOCK_COUNT(fine_lock_count),
				.CAPTURE_MUX_SEL(capture_mux_sel ),
				.DCO_CCW_OUT(dco_ccw),
				.DCO_FCW_OUT(dco_fcw),
				.FINE_LOCK_DETECT(fine_lock_detect),
				.SSC_EN(ssc_en),
				.SSC_REF_COUNT(ssc_ref_count),
				.SSC_STEP(ssc_step),
				.SSC_SHIFT(ssc_shift),
				.CAPTURE_MUX_OUT(capture_mux_out)
		);


		ANALOG_CORE #(
				.DCO_FBASE(DCO_FBASE),
				.DCO_OFFSET(DCO_OFFSET),
				.DCO_CCW_MAX(DCO_CCW_MAX),
				.DCO_CSTEP(DCO_CSTEP),
				.DCO_FCW_MAX(DCO_FCW_MAX),
				.DCO_FSTEP(DCO_FSTEP),
				.DCO_NUM_PHASES(DCO_NUM_PHASES))
			analog_core( 
				.DCO_CCW_IN(dco_ccw), 
				.DCO_FCW_IN(dco_fcw),
				.CLKREF(clkref_delay),
				.DCO_OUTP(dco_outp),
				.DCO_OUTM(dco_outm),
				.SAMPLED_PHASES_OUT(sampled_phases)
		);
		

	// testBench

		// Window frequency function
			parameter window_pts = 500;
			real window_values [window_pts-1:0];
			real window_avg;

			integer window_ii;


		// variables 


			//real clkref_period = 1/(100.001e6);  //Fref=0.1G => Fvco=2.5G
@@			real clkref_period = 1/(@FR);  //Fref=0.01G => Fvco=2.5G
@@			real kp_real = @Kp;
@@			real ki_real = @Ki;
@@			integer multiply = @FW;

			real max_periods = 5000;
			integer periods;

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
				ctrl_en = 1'b1;
				fcw_int = multiply;

				dco_open_loop_en = 0;
				dco_open_loop_cc = 0;
				dco_open_loop_fc = 0;

				dlf_adjust_en = 1;

				dlf_slow_kp = $floor(kp_real*(2**KP_FRAC_WIDTH));
				dlf_slow_ki = $floor(ki_real*(2**KI_FRAC_WIDTH));
				dlf_fast_kp = dlf_slow_kp;
				dlf_fast_ki = dlf_slow_ki;
				dlf_slew_kp = dlf_slow_kp;
				dlf_slew_ki = $floor(63*(2**KI_FRAC_WIDTH));

			//	coarse_lock_enable = 1;
				coarse_lock_enable = 0;
				coarse_lock_region_sel = 0;
@@				coarse_lock_threshold = @CT;
@@				coarse_lock_count = @CC;

				fine_lock_enable = 1;
@@				fine_lock_threshold = @FT;
@@				fine_lock_count = @FC;

				capture_mux_sel = 3;

				ssc_en = 1'b1;
				ssc_ref_count = 3030;
				ssc_step = 5;
				ssc_shift = 10;

				//$display(kp_real);
				//$display($itor(dlf_slow_kp)/(2**KP_FRAC_WIDTH));
				//$display(ki_real);				
				//$display($itor(dlf_slow_ki)/(2**KI_FRAC_WIDTH));


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

			//windows is to record the frequency changes
			always @(posedge dco_outp) begin

				window_values[window_pts-1:1] = window_values[window_pts-2:0];  //shift left
				window_values[0]= analog_core.dco_model.frequency;

				window_avg = 0;
				for (window_ii = window_pts-1;window_ii>=0;window_ii=window_ii-1) begin
					window_avg = window_avg + window_values[window_ii]/window_pts;
				end
				
			end

			always @(posedge fine_lock_detect) begin
				fine_lock_time= $realtime;	
				$fwrite(write_file, "fine lock detected on %d ns",fine_lock_time);
				$display("*** fine lock detected on %d ns",fine_lock_time);
			end
			//always @(posedge pll_controller_tdc_counter.pll_controller.coarse_lock_controller.coarse_lock_detect) begin
			//	coarse_lock_time= $realtime;	
			//	$fwrite(write_file, "coarse lock detected on %d ns\n",coarse_lock_time);
			//end

	endmodule 

