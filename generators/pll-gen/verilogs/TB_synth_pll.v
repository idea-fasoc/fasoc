


`include "ANALOG_CORE.v"


`ifdef SYN
	`define SYNorAPR
`elsif APR
	`define SYNorAPR
`endif

`ifdef SYNorAPR
	`include "sc9_cln65lp_base_rvt_udp.v"
	`include "sc9_cln65lp_base_rvt.v"
`endif	
	

`ifdef SYN
	`include "AQUANTIA_CONTROLLER.syn.v"
`elsif APR
	`include "pared_PLL_CONTROLLER_TDC_COUNTER.v"
`else
	`include "AQUANTIA_CONTROLLER.v"
`endif



`timescale 1ns/1ps

module TB_AQUANTIA_CONTROLLER();


	// Functions
		`include "FUNCTIONS.v"


		function integer func_floor;
			// return the floor of value
		
			input real func_floor_value;
				
			func_floor = func_floor_value;

		endfunction


	//Parameters

		// ANALOG CORE
		parameter DCO_FBASE = 450e6;
		parameter DCO_OFFSET = 0;
		parameter DCO_CCW_MAX = 31;
		parameter DCO_CSTEP = 40.013e6;
		parameter DCO_FCW_MAX = 1023;
		parameter DCO_FSTEP = 250.017e3;
		parameter DCO_VT_VARIATION = 75e6;


		// CONTROLLER
		parameter TDC_MAX = 63;	
		//parameter TDC_EXTRA_BITS = 0;
		parameter FCW_MAX = 31;
		//parameter FCW_MIN = 3;
		parameter KP_WIDTH = 12;
		parameter KP_FRAC_WIDTH = 2;
		parameter KI_WIDTH = 12;
		parameter KI_FRAC_WIDTH = 6;
		//parameter ACCUM_EXTRA_BITS = 1;
		//parameter FILTER_EXTRA_BITS = 1;
		
		parameter NUM_COARSE_LOCK_REGIONS = 5;
		parameter COARSE_LOCK_THSH_MAX = 32;
		parameter COARSE_LOCK_COUNT_MAX = 127;
		parameter FINE_LOCK_THSH_MAX = 127;
		parameter FINE_LOCK_COUNT_MAX = 127;		

		parameter CAPTURE_WIDTH = 25;


		// TDC_COUNTER
		//parameter TDC_NUM_RETIME_CYCLES = 2;
		//parameter TDC_NUM_RETIME_DELAYS = 2;
		//parameter TDC_NUM_COUNTER_DIVIDERS = 2;



	// Local Parameters
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);
		localparam DCO_NUM_PHASES = TDC_MAX+1;
		//localparam TDC_WIDTH = func_clog2(TDC_MAX);
		localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
		
		localparam COARSE_LOCK_REGION_WIDTH = func_clog2(NUM_COARSE_LOCK_REGIONS);
		localparam COARSE_LOCK_THSH_WIDTH = func_clog2(COARSE_LOCK_THSH_MAX);
		localparam COARSE_LOCK_COUNT_WIDTH = func_clog2(COARSE_LOCK_COUNT_MAX);

		localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
		localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);

		localparam TIME_SCALE = 1e-9;


	// Operation Modes
		localparam [4:0]
			MODE_B_250P0_750P0 	= {2'd2,3'd1},
			MODE_B_250P0_125P0 	= {2'd2,3'd6},

			MODE_B_50P0_750P0 	= {2'd0,3'd1},
			MODE_B_50P0_125P0 	= {2'd0,3'd6},

			MODE_X_250P0_312P5 	= {2'd2,3'd2},
			MODE_X_250P0_156P25 = {2'd2,3'd4},
			MODE_X_250P0_125P0 	= {2'd2,3'd5},
			
			MODE_X_156P25_312P5  = {2'd1,3'd2},
			MODE_X_156P25_156P25 = {2'd1,3'd4},
			MODE_X_156P25_125P0  = {2'd1,3'd5},
			
			MODE_X_50P0_312P5 	= {2'd0,3'd2},			
			MODE_X_50P0_156P25 	= {2'd0,3'd4},
			MODE_X_50P0_125P0 	= {2'd0,3'd5};
			





	// Input Signals

		reg  		[FCW_INT_WIDTH-1:0] 			fcw_int;
		reg 										input_dcw;
		reg 		[2:0]							output_dcw;

		reg 										clkref;
		reg 										rst;
		reg 		[4:0]							mode_select;

		reg 										dco_open_loop_en;
		reg 		[DCO_CCW_WIDTH-1:0]				dco_open_loop_cc;
		reg 		[DCO_FCW_WIDTH-1:0] 			dco_open_loop_fc;

		reg 										dlf_adjust_en;
		reg 		[KP_WIDTH-1:0]					dlf_slow_kp;
		reg 		[KI_WIDTH-1:0] 					dlf_slow_ki;
		reg 		[KP_WIDTH-1:0]					dlf_fast_kp;
		reg 		[KI_WIDTH-1:0] 					dlf_fast_ki;
		reg 		[KP_WIDTH-1:0]					dlf_slew_kp;
		reg 		[KI_WIDTH-1:0] 					dlf_slew_ki;


		reg 										coarse_lock_enable;	
		reg signed 	[COARSE_LOCK_REGION_WIDTH-1:0]	coarse_lock_region_sel;
		reg 	 	[COARSE_LOCK_THSH_WIDTH-1:0]	coarse_lock_threshold;
		reg 	 	[COARSE_LOCK_COUNT_WIDTH-1:0]	coarse_lock_count;


		reg 										fine_lock_enable;	
		reg 	 	[FINE_LOCK_THSH_WIDTH-1:0]		fine_lock_threshold;
		reg 	 	[FINE_LOCK_COUNT_WIDTH-1:0]		fine_lock_count;

		reg 		[3:0]							capture_mux_sel;


	// Output Signals
		wire 										pll_vout_ip;
		wire 										pll_vout_im;
		wire 										pll_vout_qp;
		wire 										pll_vout_qm;

		wire 										fine_lock_detect;
		wire		[CAPTURE_WIDTH-1:0]				capture_mux_out;
        


	// Interconnect

		wire		[DCO_NUM_PHASES-1:0] 			sampled_phases;
		wire										clkref_delay;

		wire 										dco_clkref;
		wire		[DCO_CCW_WIDTH-1:0]				dco_ccw;
		wire		[DCO_FCW_WIDTH-1:0]				dco_fcw;

		wire										dco_outp;
		wire										dco_outm;



	// Structural
		AQUANTIA_CONTROLLER aquantia_controller (
				.SAMPLED_PHASES_IN(sampled_phases),
				.DCO_OUTP(dco_outp),
				.DCO_OUTM(dco_outm),
				.FCW_INT(fcw_int),
				.INPUT_DCW(input_dcw),
				.OUTPUT_DCW(output_dcw),
				.CLKREF(clkref_delay),
				.RST(rst),
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
				.COARSE_LOCK_ENABLE(coarse_lock_enable),
				.COARSE_LOCK_REGION_SEL(coarse_lock_region_sel),
				.COARSE_LOCK_THRESHOLD(coarse_lock_threshold),
				.COARSE_LOCK_COUNT(coarse_lock_count),
				.FINE_LOCK_ENABLE(fine_lock_enable),
				.FINE_LOCK_THRESHOLD(fine_lock_threshold),
				.FINE_LOCK_COUNT(fine_lock_count),
				.CAPTURE_MUX_SEL(capture_mux_sel ),
				.VOUT_IP(pll_vout_ip),
				.VOUT_IM(pll_vout_im),
				.VOUT_QP(pll_vout_qp),
				.VOUT_QM(pll_vout_qm),
				.DCO_CLKREF(dco_clkref),
				.DCO_CCW_OUT(dco_ccw),
				.DCO_FCW_OUT(dco_fcw),
				.FINE_LOCK_DETECT(fine_lock_detect),
				.CAPTURE_MUX_OUT(capture_mux_out)
		);


		ANALOG_CORE #(
				.DCO_FBASE(DCO_FBASE),
				.DCO_OFFSET(DCO_OFFSET),
				.DCO_VT_VARIATION(DCO_VT_VARIATION),
				.DCO_CCW_MAX(DCO_CCW_MAX),
				.DCO_CSTEP(DCO_CSTEP),
				.DCO_FCW_MAX(DCO_FCW_MAX),
				.DCO_FSTEP(DCO_FSTEP),
				.DCO_NUM_PHASES(DCO_NUM_PHASES))
			analog_core( 
				.DCO_CCW_IN(dco_ccw), 
				.DCO_FCW_IN(dco_fcw),
				.CLKREF(dco_clkref),
				.DCO_OUTP(dco_outp),
				.DCO_OUTM(dco_outm),
				.SAMPLED_PHASES_OUT(sampled_phases)
		);
		

	// testBench

		// Window frequency function
			parameter window_pts = 500;
			real window_values [window_pts-1:0];
			real window_value_temp;
			real window_avg;

			integer window_ii;


		// variables 
			real max_periods = 1000;
			integer periods;

			real clkref_period = 1/(50.001e6);
			//real clkref_period = 1/(156.2501e6);
			//real clkref_period = 1/(250.0001e6);


		// Initialize Everything
			initial
			begin
				`ifdef SYN
					$sdf_annotate("AQUANTIA_CONTROLLER.syn.sdf", aquantia_controller,,"annotate_syn.log");
					$display("Synthesis");
				`endif

				`ifdef APR
					$sdf_annotate("pared_PLL_CONTROLLER_TDC_COUNTER.sdf", pll_controller_tdc_counter,,"annotate_apr.log");
					$display("ARP");
				`endif


				$dumpvars; 	
				$dumpfile("data.vcd");


				periods = 0;

				clkref = 1'b0;

				mode_select = MODE_X_50P0_125P0;

				dco_open_loop_en = 0;
				dco_open_loop_cc = 0;
				dco_open_loop_fc = 0;

				dlf_adjust_en = 1;

				coarse_lock_enable = 1;
				coarse_lock_region_sel = 0;
				coarse_lock_threshold = 25;
				coarse_lock_count = 64;

				fine_lock_enable = 1;
				fine_lock_threshold = 8;
				fine_lock_count = 64;

				capture_mux_sel = 3;


				case (mode_select)

					MODE_B_250P0_750P0 : 
						begin
							fcw_int = 5'd12;
							input_dcw = 1'b1;
							output_dcw = 3'd1;
		
							dlf_slow_kp = func_floor(216.1956*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(2.8300*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end

					MODE_B_250P0_125P0 : 
						begin
							fcw_int = 5'd12;
							input_dcw = 1'b1;
							output_dcw = 3'd6;
		
							dlf_slow_kp = func_floor(216.1956*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(2.8300*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end

					MODE_B_50P0_750P0 : 
						begin
							fcw_int = 5'd30;
							input_dcw = 1'b0;
							output_dcw = 3'd1;

							dlf_slow_kp = func_floor(86.4782*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(1.1320*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end

					MODE_B_50P0_125P0 : 
						begin
							fcw_int = 5'd30;
							input_dcw = 1'b0;
							output_dcw = 3'd6;

							dlf_slow_kp = func_floor(86.4782*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(1.1320*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end



					MODE_X_250P0_312P5 : 
						begin
							fcw_int = 5'd10;
							input_dcw = 1'b1;
							output_dcw = 3'd2;
		
							dlf_slow_kp = func_floor(216.1956*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(2.8300*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end

					MODE_X_250P0_156P25 : 
						begin
							fcw_int = 5'd10;
							input_dcw = 1'b1;
							output_dcw = 3'd4;
		
							dlf_slow_kp = func_floor(216.1956*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(2.8300*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end

					MODE_X_250P0_125P0 :
						begin
							fcw_int = 5'd10;
							input_dcw = 1'b1;
							output_dcw = 3'd5;
		
							dlf_slow_kp = func_floor(216.1956*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(2.8300*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end


					MODE_X_156P25_312P5 : 
						begin
							fcw_int = 5'd8;
							input_dcw = 1'b0;
							output_dcw = 3'd2;
		
							dlf_slow_kp = func_floor(270.2445*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(3.5375*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end

					MODE_X_156P25_156P25 : 
						begin
							fcw_int = 5'd8;
							input_dcw = 1'b0;
							output_dcw = 3'd4;
		
							dlf_slow_kp = func_floor(270.2445*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(3.5375*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end

					MODE_X_156P25_125P0 : 
						begin
							fcw_int = 5'd8;
							input_dcw = 1'b0;
							output_dcw = 3'd5;
		
							dlf_slow_kp = func_floor(270.2445*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(3.5375*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end



					MODE_X_50P0_312P5 : 
						begin
							fcw_int = 5'd25;
							input_dcw = 1'b0;
							output_dcw = 3'd2;

							dlf_slow_kp = func_floor(86.4782*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(1.1320*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end


					MODE_X_50P0_156P25 : 
						begin
							fcw_int = 5'd25;
							input_dcw = 1'b0;
							output_dcw = 3'd4;

							dlf_slow_kp = func_floor(86.4782*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(1.1320*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end


					MODE_X_50P0_125P0 : 
						begin
							fcw_int = 5'd25;
							input_dcw = 1'b0;
							output_dcw = 3'd5;

							dlf_slow_kp = func_floor(86.4782*(2**KP_FRAC_WIDTH));
							dlf_slow_ki = func_floor(1.1320*(2**KI_FRAC_WIDTH));
							dlf_fast_kp = dlf_slow_kp;
							dlf_fast_ki = dlf_slow_ki;
							dlf_slew_kp = dlf_slow_kp;
							dlf_slew_ki = func_floor(61*(2**KI_FRAC_WIDTH));
						end



				endcase

	
				//$finish;

				rst = 1'b0;
				#(clkref_period/TIME_SCALE) rst = 1'b1;
				#(2*clkref_period/TIME_SCALE) rst = 1'b0;

				#(max_periods*clkref_period/TIME_SCALE) $finish;
			end



		// Create the reference clock
			always begin
				#(clkref_period/TIME_SCALE/2) clkref = ~clkref;
			end
			assign #(1/1e9/TIME_SCALE) clkref_delay = clkref;

			always @(posedge dco_outp) begin

				window_avg = 0;
				for (window_ii = window_pts-1;window_ii>=0;window_ii=window_ii-1) begin

					if (window_ii > 0)
						window_values[window_ii] = window_values[window_ii-1];
					else
						window_values[window_ii] = analog_core.dco_model.frequency;
				
					window_avg = window_avg + window_values[window_ii]/window_pts;
				end
				
			end



		// ramp the vt_variation
			real vt_variation;
			real vt_variation_delta;
			integer count;

			integer count_start = 3000;
			integer count_stop = 4000;
			integer vt_variation_start = 1;
			integer vt_variation_stop = -1;
		
			

			initial begin
				count = 0;
				vt_variation = vt_variation_start;
				vt_variation_delta = $itor(vt_variation_stop - vt_variation_start)/$itor(count_stop - count_start);
			end

			always @(posedge clkref) begin

				if (count < count_stop) 
				begin
					count = count + 1;
				end
				
				if (count > count_start)
				begin
					vt_variation = vt_variation_start + (count-count_start)*vt_variation_delta;
				end

				analog_core.vt_variation = vt_variation;				

			end


	endmodule 

