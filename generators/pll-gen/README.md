
# PLL-GEN: All Digital Phase-Locked Loop Generation
This is a fully autonomous tool to generate an all digital phase-locked loop circuit from user specification to GDSII enabling autonomous power mangement in SoC design.
See more at https://fasoc.engin.umich.edu/ad-pll/

# Version Details
```
Version : Alpha-1.0                                                             
Date    : May 12, 2019 
```

# Environment Setup
1. Ensure that your machine has all of the required tools setup and have access to the technology PDK. More instructions on this step can be found at https://github.com/idea-fasoc/fasoc/blob/master/README.md. "pll-gen" specific tools are "irun","ncverilog" only if you want to run verilog simulation by setting "--run_vsim 1" in pll_gen option

1. Directory tree: below are the explanation about the directory tree of pll-gen
    ```bash
	1. pll-gen dir: 'fasoc/generators/pll-gen/'
		Role: The top directory of pll-gen that contains generally used python functions and tools for different technologies( Alpha release has only tsmc65lp)
	2. General python function dir: 'fasoc/generators/pll-gen/pymodules/'
		Role: Directory that contains the general purposed python functions for pll-gen 
	3. Design dir: 'fasoc/generators/pll-gen/tsmc65lp/'
		Role: Directory where the design for tsmc65lp takes place. User should run the make commands in this directory. We're planning to support tsmc16 in the future.
    ```

1. Add the Auxiliary library and Model directory paths to the `fasoc/config/platform_config.json` file under the corresponding technology node (currently only supports tsmc65lp node). PLL has two aux cells: "dco_CC", "dco_FC". In side the "aux_lib", it has to contain "dco_CC/export/", "dco_FC/export/", and all the files should be under "/export/". An example of the platform_config is shown below. Example model file is in "/pll-gen/tsmc65lp/model/".
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
1. Prepare an input spec "Input_Spec_File.json" file similar to below. Alpha version supports only nominal frequency range as an input spec. More specs (Phase noise, Jitter, power, area, frequency range) will be added in the future release. 
    ```bash
	{
	"generator": "pll-gen",
	"module_name": "test_synth_pll",
	"specifications": 
	   {
	"Fnom_min":8.40e8,	<= lower limit of nominal frequency range (this is NOT the minimum frequency of pll) 
	"Fnom_max":8.60e8,	<= upper limit of nominal frequency range (this is NOT the maximum frequency of pll)	
	   }
	}
    ```

1. Running the PLL generator. 
   To run the PLL generator, execute the below command from any location.
    ```bash
    .{Path_to_Generator_Folder}/tsmc65lp/tools/PLL_GEN.py --specfile {Input_Spec_File.json} --output {Output_Folder} --platform {Technology_Node} [--mode {Run_Mode}] [--run_vsim {Verilog_sim}]
    ```
   All the options specified in square brackets [] are optional. When `--clean` option is provided, the tool exits after a cleanup of the workspace. Each of the command line variables are described below in detail.
   
   __{Input_Spec_File.json}__
   - This file is similar to `test.json` file and contains the input specifications of the LDO module.
   
   __{Output_Folder}__
   - This variable specifies the directory where the final outputs of the tool are saved.
   
   __{Technology_Node}__
   - This variable must be either "tsmc65lp" or "gfbicmos8hp" as of now.
   
   __{Run_Mode}__
   - This must be either "verilog", "macro" or "full". Default mode used is "verilog" if this option is not specified. 
     - "verilog" mode do not need access to the PDK or the CADRE flow and generates only the verilog description of the design. 
     - "macro" mode needs access to PDK/CADRE flow and generates the netlist and gds files along with the verilog description. 
     - "full" mode does a full post-pex extraction of the design netlist and layout files and runs a complete post-pex spice simulation.

   __{Verilog_sim}__
   - This must be either "0", "1" 
     - "0" mode do not run the verilog simulation (default) 
     - "1" mode runs the verilog simulation with dco  behavioral model 


1. Run the test script from `pll-gen/tsmc65lp/` folder to ensure the generator tool and the model tool are correctly setup
    ```bash
   make pll_gen 
    ```

1. Running the model generator in standalone mode. Run this in 'pll-gen/tsmc65lp'
   Ensure you have the correct `fasoc/config/platform_config.json` file and run the following commands
   The pre-layout model and post-layout are generated separately.
    ```bash
   make modeling 
   make pex_modeling 
    ```

1. Remove the generated files for new run. 
    ```bash
   make bleach_all 
    ```

# Known bugs 
1. Current pll controller has potential metastability issue in retiming due to reference cycle latency in the procedure of retiming edge selection. Verilog simulation with sdf annotation doesn't give correct result due to this metastability issue. Controller and testbench will be updated to address the problems in the Beta release.

# Supported Spec ranges
1. Alpha version supports only nominal frequency for user input, but provides generated design's specs of frequency resolution of DCO, power consumption, area. Below are the spec ranges that the pll supports. If the user gives certain nominal frequency, the generator will provide other specs within the below spec ranges. Beta release will include phase noise, jitter in addition.
    ```bash
	Nominal Frequency   : 240 MHz ~ 840 MHz
	Frequency Resolution: 3.15K Hz ~ 54.5KHz
	Power Consumption   : 9.0mW ~ 17.7mW
	Area                : 4460um^2 ~ 16416um^2
    ```
