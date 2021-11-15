
# SCPA-GEN: Switched-Capacitor Power Amplifier Generation
This is a fully autonomous tool to generate a switched-capacitor power amplifier from user specification to GDSII in SoC design.
See more at https://fasoc.engin.umich.edu/TODO

# Version Details
```
Version : Beta-1.0                                                             
Date    : Nov 15, 2021
```

# What's in the release
- First version of the tool. 
- Generates the SCPA macro and its associated views (GDS, LEF, LIB, DB and CDL) for given specs. (fixed for now)
- This release includes:
  - Synthesizable SCPA verilog.
  - Synthesis and APR of the SCPA.
  - Generating the associated views.
  

# Environment Setup
Ensure that your machine has all of the required tools setup and have access to the technology PDK. More instructions on this step can be found at https://github.com/idea-fasoc/fasoc/blob/master/README.md


# Tool Setup
1. Add the Auxiliary library and Model directory paths to the [`fasoc/config/platform_config.json`](https://github.com/idea-fasoc/fasoc/blob/master/config/platform_config.json) file under the corresponding technology node. `scpa-gen` currently supports gf12lp node. An example of the platform config with the variable descriptions is provided below.
    ```bash
    "gf12lp": {
      "nominal_voltage": 0.8,
      "aux_lib": "<PATH_TO_AUX_LIB>",
      "model_lib": "<PATH_TO_MODEL_LIB>",
      "sram_2kb_lib": "This is not necessary for SCPA-GEN",
      "calibreRules": "<PATH_TO_PDK_CALIBRE_RULES>",
      "hspiceModels": "<PATH_TO_PDK_SPICE_MODELS>"
    }
    ```
    __nominal_voltage__
    - Core Voltage of the SCPA.
    
    __aux_lib__
    - Folder path containing the "SCPA_MIMCAP_new" auxiliary cell folder. Auxiliary Cell Folder structure should be as given below:
    ```bash
        aux_lib/PT_UNIT_CELL
        |--- cdl/PT_UNIT_CELL.cdl
        |--- db/PT_UNIT_CELL.db
        |--- gds/PT_UNIT_CELL.gds
        |--- lef/PT_UNIT_CELL.lef
        |--- lib/PT_UNIT_CELL.lib
    ```
    
    __model_lib__
    - Folder path containing the `scpaModel.json` file.(TODO)
    
    __sram_2kb_lib__
    - This parameter is not required for scpa-gen tool.
    
    __calibreRules__
    - Folder path containing the calibre pex rule files.
    
    __hspiceModels__
    - Folder path containing the spice models of the technology node.
   
1. There are three modes of SCPA-GEN tool, and the function of each mode is described in "Running the tools" section. Run the following commands as a validation for the SCPA-GEN tool setup.
  
    __To ensure the "verilog" mode is correctly setup, run the below test command from `scpa-gen` folder.__
    - The scpa gen "verilog" mode is successfully setup if the the build generates `generators/scpa-gen/work/*.v` files at the end of the run.
    ```bash
    make gen_12lp (for GF12LP)
    ``` 
     
    __To ensure the "macro" mode is correctly setup, run the below test command from `scpa-gen` folder.__
    - The scpa gen "macro" mode is successfully setup if the the build generates `generators/scpa-gen/work/*.gds.gz` files at the end of the run. 
    ```bash
    make gen_12lp_macro (for GF12LP)
    ``` 
    
    
    __To ensure the "full" mode is correctly setup, run the below test command from `scpa-gen` folder.__
    - The scpa gen "full" mode is successfully setup if the the build generate `generators/scpa-gen/work/*.gds.gz` files and completes the run without any errors.(TODO) 
    ```bash
    make gen_12lp_full (for GF12LP) --> use calibre version "2019.3_39.25" or higher for 12LP technology.
    ``` 
    

# Running the tools
1. Prepare an input spec "Input_Spec_File.json" file similar to `fasoc/generators/scpa-gen/test.json`. An example of the input spec file with variable descriptions is provided below.
    ```bash
    {
      "module_name": "scpaInst",
      "generator": "scpa-gen",
      "specifications": {
	(TODO)
      }
    }
    ```
   Each of the input spec file variables are described below:
   
    __module_name__
    - Name of the SCPA design.
    
    __generator__
    - This variable must be `scpa-gen`. This variable is added as a pre-check condition to catch interfacing mistakes between the SoC-Synthesis tool and the SCPA generator.
    
    __specifications__
    - _TODO_

1. Running the SCPA generator. 
   To run the SCPA generator, execute the below command from any location.
    ```bash
    .{Path_to_Generator_Folder}/tools/scpa_gen.py --specfile {Input_Spec_File.json} --output {Output_Folder} --platform {Technology_Node} [--mode {Run_Mode}] [--clean]
    ```
   All the options specified in square brackets [] are optional. When `--clean` option is provided, the tool exits after a cleanup of the workspace. Each of the command line variables are described below in detail.
   
   __{Input_Spec_File.json}__
   - This file is similar to `test.json` file and contains the input specifications of the SCPA module.
   
   __{Output_Folder}__
   - This variable specifies the directory where the final outputs of the tool are saved. "Output folder" is automatically cleaned by the tool, so make sure the "Output folder" is different from the default repo folders.
   
   __{Technology_Node}__
   - This variable must be "gf12lp" as of now.
   
   __{Run_Mode}__
   - This must be either "verilog", "macro" or "full". Default mode used is "verilog" if this option is not specified. 
     - "verilog" mode do not need access to the PDK or the CADRE flow and generates only the verilog description of the design. 
     - "macro" mode needs access to PDK/CADRE flow and generates the netlist and gds files along with the verilog description. 
     - "full" mode does a full post-pex extraction of the design netlist and layout files and runs a complete post-pex spice simulation.
   
1. Running the model generator in standalone mode. 
   Ensure you have the correct `fasoc/config/platform_config.json` file and run the following commands
    ```bash
    .{Path_to_Generator_Folder}/tools/scpa_model.py --platform {Technology_Node}
    ```
   `Technology_Node` must be "gf12lp" as of now.
    
# Tool Directory Structure
```bash
    scpa-gen
    |--- extraction
    |--- flow
    |--- hspice   
    |--- tools
    |--- Makefile
    |--- README.md
    |--- test.json
```
   __extraction__
   - Folder with PEX config files to extract parasitics of the final desgin.
  
   __flow__
   - Folder with the synthesis and APR scripts that runs the CADRE flow.  
  
   __hspice__
   - Folder with model simulation files to run post-pex simulations.

   __tools__
   - Folder with source scripts of the tool that encapsulates the SCPA macro generation process. 

   __Makefile__
   - Makefile to perform a test run of the SCPA generator.

   __Readme.md__
   - Read me file with the instructions for running the tool.

   __test.json__
   - Sample SCPA input specification file in json format. Makefile uses this file to perform a test run of the tool. 
