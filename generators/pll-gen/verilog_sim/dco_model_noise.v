`ifndef __DCO_MODEL__
`define __DCO_MODEL__

//`timescale 1fs/1fs
//`timescale 1ps/1ps

module dco_model_noise( 
    DCO_CCW_IN, 
    DCO_FCW_IN, 
    PHASES_OUT);


	// Functions

        
    // Parameters


//		localparam TIME_SCALE = 1e-15;
		parameter TIME_SCALE = 1e-12;

		//parameter DCO_CENTER_FREQ = 2.4e9;
		parameter clkref_period = 1/(40e+06);  // ble_test 40MHz => 2.400250G
		parameter multiply = 60;
		parameter DCO_CENTER_FREQ = multiply*(1/clkref_period);
		// DCO Base operating frequency
		parameter DCO_FBASE = 450e6;
		parameter DCO_OFFSET = 0;
		parameter DCO_VT_VARIATION = 175e6;

		// DCO Coarse Controls (covers ~3GHz)
		parameter DCO_CCW_MAX = 31;
		parameter DCO_CSTEP = 40e6;

		// DCO Fine Controls (covers ~50MHz)
		parameter DCO_FCW_MAX = 1023;
		parameter DCO_FSTEP = 180e3;

		// DCO number of phases
		parameter DCO_NUM_PHASES = 5;


	// Local Parameters
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);


	// Ports
		input			[DCO_CCW_WIDTH-1: 0]	DCO_CCW_IN;
		input			[DCO_FCW_WIDTH-1: 0]	DCO_FCW_IN;
		output reg		[DCO_NUM_PHASES-1:0]	PHASES_OUT;


	// Internal Signals
		reg dco_clk;

	// noise
		real freq_noise;

	// Variables
		real frequency;
		real frequency_fr;
		real frequency_ideal;
		real vt_variation;
		real period;	
		real period_ideal;	
		real period_noise;	
		real period_noise_fr;	
		real period_fr;	
		real period_noise_accum;	
		real period_noise_accum_fr;	
		real stg_delay0;	
		real stg_delay1;	
		real stg_delay2;	
		real stg_delay3;	

	// Functional

		// flicker noise
			//adpll_flicker_noise #(.center_frequency(DCO_CENTER_FREQ)) flicknoise (dco_clk, freq_noise);
			adpll_white_noise #(.center_frequency(DCO_CENTER_FREQ)) flicknoise (dco_clk, freq_noise);
		// Initialze the frequency and generate and edge
			initial begin
				frequency = DCO_FBASE;
				// test purpose
				//frequency = 2.4e9 + 250e3;  
				vt_variation = 0;

				period_noise_accum = 0;
				period_noise_accum_fr = 0;
				dco_clk = 1'b0;
				#(1/frequency/2/TIME_SCALE);
				dco_clk = ~dco_clk;
			end

		// Set the DCO frequency and delay betwen phases
			always @* begin
				frequency = DCO_FBASE + DCO_FSTEP*$itor(DCO_FCW_IN) + DCO_CSTEP*$itor(DCO_CCW_IN) + freq_noise;
				frequency_fr = DCO_CENTER_FREQ + freq_noise;
				frequency_ideal = DCO_FBASE + DCO_FSTEP*$itor(DCO_FCW_IN) + DCO_CSTEP*$itor(DCO_CCW_IN);
				//frequency_ideal = DCO_CENTER_FREQ;
				//frequency = DCO_FBASE + DCO_FSTEP*$itor(DCO_FCW_IN) + DCO_CSTEP*$itor(DCO_CCW_IN);
				//frequency = DCO_FBASE + DCO_CSTEP*$itor(DCO_CCW_IN);
				period=(1/frequency/TIME_SCALE);
				period_fr=(1/frequency_fr/TIME_SCALE);
				period_ideal=(1/frequency_ideal/TIME_SCALE);
				period_noise = (period_ideal - period)*TIME_SCALE;
				period_noise_fr = (period_ideal - period_fr)*TIME_SCALE;
				// (3,4), (0,1), (2,3), (4,0), (1,2)
				stg_delay0 = (period/DCO_NUM_PHASES/2)*1.0;
				stg_delay1 = (period/DCO_NUM_PHASES/2)*1.0;
				stg_delay2 = (period/DCO_NUM_PHASES/2)*1.0;
				stg_delay3 = (period/DCO_NUM_PHASES/2)*1.0;
				// stg_delay4 = (period/DCO_NUM_PHASES/2)*1;
			end
			//// test purpose
			//always @* begin
			//	frequency = 2.4e9 + 250e3;  
			//end

		// Make the fast clocks oscillate
			always @(posedge dco_clk) begin
				period_noise_accum <= period_noise_accum + period_noise;
				period_noise_accum_fr <= period_noise_accum_fr + period_noise_fr;
				#(1/frequency/2/TIME_SCALE) dco_clk <= ~dco_clk;
			end


			always @(negedge dco_clk) begin
				#(1/frequency/2/TIME_SCALE) dco_clk <= ~dco_clk;
			end

		// generate the phases

			always @(posedge dco_clk or negedge dco_clk) begin
				PHASES_OUT[0] = dco_clk;
			end

			always @(posedge PHASES_OUT[0] or negedge PHASES_OUT[0]) begin
				#(stg_delay0) PHASES_OUT[1] = ~PHASES_OUT[0];
			end

			always @(posedge PHASES_OUT[1] or negedge PHASES_OUT[1]) begin
				#(stg_delay1) PHASES_OUT[2] = ~PHASES_OUT[1];
			end

			always @(posedge PHASES_OUT[2] or negedge PHASES_OUT[2]) begin
				#(stg_delay2) PHASES_OUT[3] = ~PHASES_OUT[2];
			end

			always @(posedge PHASES_OUT[3] or negedge PHASES_OUT[3]) begin
				#(stg_delay3) PHASES_OUT[4] = ~PHASES_OUT[3];
			end
		


		//	genvar genvar_ii;
		//	generate

		//		for (genvar_ii=0;genvar_ii<DCO_NUM_PHASES;genvar_ii=genvar_ii+1) 
		//			begin : GEN_PHASE

		//				if (genvar_ii == 0 ) 
		//					begin

		//						always @(posedge dco_clk) begin
		//							PHASES_OUT[genvar_ii] = dco_clk;
		//						end

		//						always @(negedge dco_clk) begin
		//							PHASES_OUT[genvar_ii] = dco_clk;
		//						end
		//					end
		//				else
		//					begin

		//						always @(posedge PHASES_OUT[genvar_ii-1]) begin
		//							#(1/frequency/TIME_SCALE/DCO_NUM_PHASES/2) PHASES_OUT[genvar_ii] = ~PHASES_OUT[genvar_ii-1];
		//						end

		//						always @(negedge PHASES_OUT[genvar_ii-1]) begin
		//							#(1/frequency/TIME_SCALE/DCO_NUM_PHASES/2) PHASES_OUT[genvar_ii] = ~PHASES_OUT[genvar_ii-1];
		//						end
		//					end
		//			end

		//		endgenerate

endmodule

module adpll_flicker_noise (clk, x);

    // Parameter declarations
    parameter real center_frequency = 2.4e9;
    parameter real sampling_frequency = 1e9;    ///
    parameter real corner_frequency   = 1e4;    ///
    parameter int  number_of_segments = 1000;     ///
   // parameter real rms_noise_at_dc    = $sqrt(2*3.141592653589793*1e6*$pow(10,(-70.0+120)/10));//(10**((37)/10))) ; //$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**((-80+120)/10))) ;//$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**4));)
    parameter real rms_noise_at_dc    = $sqrt(2*3.141592653589793*1e6*1e6*$pow(10,(-88)/10)*center_frequency);//(10**((37)/10))) ; //$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**((-80+120)/10))) ;//$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**4));)

//    parameter real rms_noise_at_dc    = $sqrt(2*3.141592653589793*(1e6)*(10**((-83+120)/10))) ; //$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**((-80+120)/10))) ;//$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**4));)
    parameter int unsigned seed       = 1453;   ///
    parameter real precision          = 0.000001;  /// normalized precision within (0,1)    
    
    // Port declarations
    input logic clk;    /// sample clock signal
    output real x;      /// output signal
    
    // Local signals and variables
    const real pi = 3.141592653589793;    
    integer i;
    real dlf, dcgain, a0, b0, filter_sum;
    real f_corner[0:number_of_segments-1];
    real filt_num[0:number_of_segments-1];
    real filt_den[0:number_of_segments-1];
    real filter[0:number_of_segments-1];
    real filter_prev[0:number_of_segments-1]; 
    real rand_sample, rand_sample_hist;
    int recip_precision;
    int unsigned myseed; // if seed is directly passed to $dist_normal, ncelab complains.
    
/*    // Initialization
    initial begin    
        // Assertions
        assert (seed >= 0) else begin
            $display("ERROR: SEED %f HAS TO BE NON-NEGATIVE. In module: %m",seed);
            $fatal(0);
        end
        assert (rms_noise_at_dc >= 0) else begin
            $display("ERROR: INPUT POWER %f HAS TO BE NON-NEGATIVE. In module: %m",rms_noise_at_dc);
            $fatal(0);
        end
        assert ((precision > 0) && (precision < 1)) else begin
            $display("ERROR: PRECISION %f HAS TO BE WITHIN (0,1). In module %m", precision);
            $fatal(0);
        end
        assert (corner_frequency < sampling_frequency/8) else begin
            $display("ERROR: CORNER FREQUENCY %e HAS TO BE LESS THAN 1/8 of SAMPLING FREQUENCY %e. In module %m", corner_frequency, sampling_frequency);
            $fatal(0);
        end
        // Create flicker noise filter    
        // determine the corner frequencies of each filter slice
        dlf  = ($log10(sampling_frequency/8) - $log10(corner_frequency))/(number_of_segments-1);    
        for (i = 0; i <= number_of_segments; i=i+1) begin
            f_corner[i] = $pow(10,$log10(corner_frequency) + i*dlf);
            //$display("%m: f_corner[i] = %e",f_corner[i]);
        end        
        // dc gain correction for filters connected in parallel        
        for (i = 0; i < number_of_segments; i=i+1) begin
            dcgain = dcgain + $pow(10,-0.5*dlf*i);
        end    
        // calculate filter coefficients for flicker noise           
        for (i = 0; i < number_of_segments; i=i+1) begin        
            // continuous  filter coefficients: a0 / (b0*s+1)
            a0 = $pow(10,-0.5*dlf*i)/dcgain;
            b0 = 1/(2*pi*f_corner[i]);
            //$display("%m a0=%e  b0=%e",a0,b0);              
            // discretize filter coefficients via bilinear transform
            // discretized filter coefficients: (filt_num*z + filt_num) / (z + filt_den)
            filt_num[i] = a0/(b0*2*sampling_frequency + 1);
            filt_den[i] = (1 - b0*2*sampling_frequency)/(1 + b0*2*sampling_frequency);
            $display("%m num=%e den=%e",filt_num[i],filt_den[i]);              
        end
        // Initialize local variables
        for (i = 0; i < number_of_segments; i=i+1) begin 
            filter[i] = 0;
        end                                    
        myseed = seed;
        recip_precision = 1/precision;
        rand_sample_hist <= 0;
        rand_sample      <= ($dist_normal(myseed, 0, recip_precision)*precision)*rms_noise_at_dc;
    end
*/
    initial begin
	filt_num[0] = 1;
        for (i = 1; i < number_of_segments; i=i+1) begin
            filt_num[i] = 0;
            //$display("%m: filt_num[i] = %e",filt_num[i]);
        end    
	filt_den[0] = 1;
        for (i = 1; i < number_of_segments; i=i+1) begin
            filt_den[i] = (i+1 - 2.5) * filt_den[i - 1] / (i+1 - 1);
            //$display("%m: filt_den[i] = %e",filt_den[i]);
        end   
        // Initialize local variables
        for (i = 0; i < number_of_segments; i=i+1) begin 
            filter[i] = 0;
            //$display("%m: filt_den[i] = %e",filt_den[i]);
        end     
        myseed = seed;
        recip_precision = 1/precision;
        rand_sample_hist <= 0;
        rand_sample      <= ($dist_normal(myseed, 0, recip_precision)*precision)*rms_noise_at_dc;

    end
    // Behavior
    always @(posedge clk) begin 
/*        filter_sum = 0;
        for (i = 0; i < number_of_segments; i=i+1) begin 
            filter[i] = filt_num[i]*(rand_sample + rand_sample_hist) - filt_den[i]*filter_prev[i]; 
            filter_prev[i] = filter[i];
            filter_sum = filter_sum + filter[i];
        end       
*/
        filter_sum = filt_num[0]*rand_sample;
        for (i = 1; i < number_of_segments; i=i+1) begin 
            filter_sum = filter_sum - filt_den[i]*filter_prev[i-1]; 
        end
        for (i = number_of_segments-1; i > 0; i=i-1) begin 
            filter_prev[i] = filter_prev[i-1]; 
        end
	filter_prev[0] = filter_sum;
 
        rand_sample_hist <= rand_sample;
        x <= filter_sum;
        rand_sample <= ($dist_normal(myseed, 0, recip_precision)*precision)*rms_noise_at_dc;        
    end

endmodule

module adpll_white_noise (clk, x);

    // Parameter declarations
    parameter real center_frequency = 2.4e9;
    parameter real sampling_frequency = 1e9;    ///
    parameter real corner_frequency   = 1e4;    ///
    parameter int  number_of_segments = 1000;     ///
   // parameter real rms_noise_at_dc    = $sqrt(2*3.141592653589793*1e6*$pow(10,(-70.0+120)/10));//(10**((37)/10))) ; //$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**((-80+120)/10))) ;//$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**4));)
   `ifdef LOW_NOISE
	    parameter real nfreq_sigma    = $sqrt(1e6*1e6*$pow(10,(-118)/10)*center_frequency);//(10**((37)/10))) ; //$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**((-80+120)/10))) ;//$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**4));)
   `else
	    parameter real nfreq_sigma    = $sqrt(1e6*1e6*$pow(10,(-98)/10)*center_frequency);//(10**((37)/10))) ; //$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**((-80+120)/10))) ;//$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**4));)
   `endif

//    parameter real rms_noise_at_dc    = $sqrt(2*3.141592653589793*(1e6)*(10**((-83+120)/10))) ; //$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**((-80+120)/10))) ;//$pow(10,(5.3/2)) * $sqrt(2*3.141592653589793*(1e6)*(10**4));)
    parameter int unsigned seed       = 1453;   ///
    parameter real precision          = 0.000001;  /// normalized precision within (0,1)    
    
    // Port declarations
    input logic clk;    /// sample clock signal
    output real x;      /// output signal
    
    // Local signals and variables
    const real pi = 3.141592653589793;    
    integer i;
    real dlf, dcgain, a0, b0, filter_sum;
    real f_corner[0:number_of_segments-1];
    real filt_num[0:number_of_segments-1];
    real filt_den[0:number_of_segments-1];
    real filter[0:number_of_segments-1];
    real filter_prev[0:number_of_segments-1]; 
    real rand_sample, rand_sample_hist;
    int recip_precision;
    int unsigned myseed; // if seed is directly passed to $dist_normal, ncelab complains.
    initial begin
	x <= center_frequency;
        recip_precision = 1/precision;
        myseed = seed;
    end
    // Behavior
    always @(posedge clk) begin 
        x <= ($dist_normal(myseed, 0, recip_precision)*precision)*nfreq_sigma;        
    end

endmodule


`endif
