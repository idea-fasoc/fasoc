
# PLL-GEN: All Digital Phase-Locked Loop Generation
This is a fully autonomous tool to generate an all digital phase-locked loop circuit from user specification to GDSII enabling autonomous power mangement in SoC design.
See more at https://fasoc.engin.umich.edu/ad-pll/

# Version Details
```
Version : Beta-1.0                                                             
Date    : May 27, 2020 
```
# Major updates 
```
Date    : May 3, 2020
	1. Supported specifications are added (inband phase noise, dco power etc.). For details, refer to the example in "Running the tools" section below.
	2. For the noise performance, power domain of DCO is separated from the controller. The layout style resembles that of the taped-out chip on summer 2019. Measurement results will be updated in FASoC web-page.
	3. Output buffer/ divder block is embedded in PLL to drive large load of pad and to enable devided output clock. Power domain of this block is separated from controller and DCO as well for the noise performance.
Date    : May 27, 2020
	1. Codes are modified to support gf12lp and tsmc65lp
	
```

# Environment Setup
1. Ensure that your machine has all of the required tools setup and have access to the technology PDK. More instructions on this step can be found at https://github.com/idea-fasoc/fasoc/blob/master/README.md. "pll-gen" specific tools are "irun","ncverilog" only if you want to run verilog simulation by setting "--run_vsim 1" in pll_gen option

1. Directory tree: below are the explanation about the directory tree of pll-gen
    ```bash
	1. pll-gen dir: 'fasoc/generators/pll-gen/'
		Role: The top directory of pll-gen that contains generally used python functions and tools ( Beta release supports tsmc65lp & gf12lp )
	2. General python function dir: 'fasoc/generators/pll-gen/pymodules/'
		Role: Directory that contains the general purposed python functions for pll-gen 
	3. Design dir: 'fasoc/private/generators/pll-gen/'
		Role: Directory where the pll layouts for tsmc65lp or gf12lp are generated. Access to private directory is required to generate the layout of pll. 
    ```

1. Add the Auxiliary library and Model directory paths to the `fasoc/config/platform_config.json` file under the corresponding technology node (currently only supports tsmc65lp and gf12lp). PLL has two aux cells: "dco_CC", "dco_FC". In side the "aux_lib", it has to contain "dco_CC/export/", "dco_FC/export/", and all the files should be under "/export/". An example of the platform_config is shown below. Example model file is in "/pll-gen/tsmc65lp/model/".
    ```bash
    "tsmc65lp": {
      "nominal_volatage": 1.2,
      "aux_lib": "/net/ludington/v/kmkwon/forTutu/aux_lib",
      "model_lib": "/net/ludington/v/kmkwon/forTutu/model",
    }

	** example of file paths ** 
	aux_lib/dco_CC/export/dco_CC.cdl    
	aux_lib/dco_CC/export/dco_CC.gds    
	aux_lib/dco_CC/export/dco_CC.lef    
	aux_lib/dco_FC/export/dco_FC.cdl    
	aux_lib/dco_FC/export/dco_FC.gds    
	aux_lib/dco_FC/export/dco_FC.lef    
    ```
   
# Running the tools
1. First, you need to setup the CADRE flow for certain technology (this only applies for macro or full mode). Go to /fasoc/private/cad/ and type: (1) git checkout master (for TSMC65), (2) git checkout gf14 (for GF12).

1. Prepare an input spec "Input_Spec_File.json" file similar to below. Alpha version supports only nominal frequency range as an input spec. More specs (Phase noise, Jitter, power, area, frequency range) will be added in the future release. 
    ```bash
	{
	"generator": "pll-gen",
	"module_name": "test_synth_pll",
	"specifications": 
	   {
		"Fnom_min":2.80e8,	<= lowend of the nominal frequency range (nominal frequency is the DCO frequency when the control word is medium)
		"Fnom_max":3.00e8,	<= highend of the nominal frequency range
		"FCR_min":1,     	<= frequency coverage ratio of fine/coarse (fine frequency tuning range / coarse frequency step) 
		"Fmax":5e8,		<= maximum frequency
		"Fmin":35e6,		<= minimum frequency
		"Fres":20e3,		<= frequency resolution
		"inband_PN":-80,	<= inband phase noise in dBc/Hz
		"dco_PWR":24e-3		<= dco power
	   }
	}
    ```

1. Running the PLL generator. 
   To run the latest PLL generator, execute the below command from any location. Hierarchical layout with separate power domains for DCO and buffer will be generated. Silicon performance measured in tsmc65lp.
    ```bash
    .{Path_to_Generator_Folder}/tsmc65lp/tools/PLL_GEN_Beta.py --specfile {Input_Spec_File.json} --output {Output_Folder} --platform {Technology_Node} [--mode {Run_Mode}] [--run_vsim {Verilog_sim}] [--synth_tool {Synth_Tool}] [--track {Matal_Track}]
    ```
   All the options specified in square brackets [] are optional. When `--clean` option is provided, the tool exits after a cleanup of the workspace. Each of the command line variables are described below in detail.
   
   __{Input_Spec_File.json}__
   - This file is similar to `test_beta65.json, test_alpha12.json` files and contains the input specifications of the PLL module.
   
   __{Output_Folder}__
   - This variable specifies the directory where the final outputs of the tool are saved.
   
   __{Technology_Node}__
   - This variable must be either "tsmc65lp" or "gf12lp" as of now.
   
   __{Run_Mode}__
   - This must be either "verilog", "macro" or "full". Default mode used is "verilog" if this option is not specified. 
     - "verilog" mode do not need access to the PDK or the CADRE flow and generates only the verilog description of the design. 
     - "macro" mode needs access to PDK/CADRE flow and generates the netlist and gds files along with the verilog description. 
     - "full" mode does a full post-pex extraction of the design netlist and layout files and runs a complete post-pex spice simulation.

   __{Verilog_sim}__
   - This must be either "0", "1" 
     - "0" mode do not run the verilog simulation (default) 
     - "1" mode runs the verilog simulation with dco  behavioral model 

   __{Synth_Tool}__
   - Optional variable for synthesis tool
     - dc (default) 
     - genus 

   __{Metal_Track}__
   - Optional variable for metal track 


1. Run the test script from `pll-gen` folder to ensure the generator tool and the model tool are correctly setup
    ```bash
   make pll_gen_beta65      # for tsmc65lp

   make pll_gen_beta12      # for gf12lp
    ```

1. Running the model generator in standalone mode. Run this in 'pll-gen/tsmc65lp'
   Ensure you have the correct `fasoc/config/platform_config.json` file and run the following commands
   The pre-layout model and post-layout are generated separately.
    ```bash
   # for tsmc65lp
   make modeling65 

   # for gf12lp
   make modeling12 
    ```

1. Remove the generated files for new run. 
    ```bash
   make bleach_all 
    ```

# Known bugs 
1. Current pll controller has potential metastability issue in retiming due to reference cycle latency in the procedure of retiming edge selection. Verilog simulation with sdf annotation doesn't give correct result due to this metastability issue. Controller and testbench will be updated to address the problems in the Beta release.

# Supported Spec ranges
1. Below are the spec ranges that the pll supports. If the user gives certain nominal frequency, the generator will provide other specs within the below spec ranges. Beta release will include phase noise, jitter in addition.
    ```bash
	1. tsmc65lp
		Maximum Frequency	: 449 MHz ~ 3.02 GHz
		Minimum Frequency	: 6.4 MHz ~ 2.09 GHz 
		Nominal Frequency	: 262 MHz ~ 2.53 GHz
		Frequency Resolution	: 0.28 KHz ~ 126 KHz
		Frequency Cover Ratio	: 0.15 ~ 48 
		DCO Power Consumption   : 9.0mW ~ 17.7mW
		PLL inband phase noise	: -90.2 dBc/Hz ~ -63.3 dBc/Hz
		Area			: 4460um^2 ~ 76416um^2
	2. gf12lp
		on progress	
    ```
