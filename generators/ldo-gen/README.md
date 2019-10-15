
# LDO-GEN: Low Dropout Regulator Generation
This is a fully autonomous tool to generate a low drop out regulator circuit from user specification to GDSII enabling autonomous power mangement in SoC design.
See more at https://fasoc.engin.umich.edu/digital-ldo/

# Version Details
```
Version : Alpha-1.0                                                             
Date    : May 12, 2019 
```

# What's in the release
- First version of the tool. 
- Generates the LDO macro and its associated views (GDS, LEF, LIB, DB and CDL) for given user specs.
- This release includes:
  - Synthesizable LDO verilog generation.
  - Synthesis and PNR of the LDO.
  - Performing the physical verification (PV) check.
  - Generating the associated views.
  

# Environment Setup
Ensure that your machine has all of the required tools setup and have access to the technology PDK. More instructions on this step can be found at https://github.com/idea-fasoc/fasoc/blob/master/README.md


# Tool Setup
1. Add the Auxiliary library and Model directory paths to the [`fasoc/config/platform_config.json`](https://github.com/idea-fasoc/fasoc/blob/master/config/platform_config.json) file under the corresponding technology node. `ldo-gen` currently supports tsmc65lp and gfbicmos8hp nodes. An example of the platform config with the variable descriptions is provided below.
    ```bash
    "tsmc65lp": {
      "nominal_voltage": 1.2,
      "aux_lib": "<PATH_TO_AUX_LIB>",
      "model_lib": "<PATH_TO_MODEL_LIB>",
      "sram_2kb_lib": "This is not necessary for LDO-GEN",
      "calibreRules": "<PATH_TO_PDK_CALIBRE_RULES>",
      "hspiceModels": "<PATH_TO_PDK_SPICE_MODELS>"
    }
    ```
    __nominal_voltage__
    - Core Voltage of the LDO.
    
    __aux_lib__
    - Folder path containing the "PT_UNIT_CELL" auxiliary cell folder. Auxiliary Cell Folder structure should be as given below:
    ```bash
        aux_lib/PT_UNIT_CELL
        |--- cdl/PT_UNIT_CELL.cdl
        |--- db/PT_UNIT_CELL.db
        |--- gds/PT_UNIT_CELL.gds
        |--- lef/PT_UNIT_CELL.lef
        |--- lib/PT_UNIT_CELL.lib
    ```
    
    __model_lib__
    - Folder path containing the `ldo.model` file.
    
    __sram_2kb_lib__
    - This parameter is not required for ldo-gen tool.
    
    __calibreRules__
    - Folder path containing the calibre pex rule files.
    
    __hspiceModels__
    - Folder path containing the hspice models of the technology node.
   
1. Run the test script from `ldo-gen` folder to ensure the generator tool and the model tool are correctly setup
    ```bash
    make gen_65lp (for TSMC65lp) or
    make gen_8hp  (for GFBICMOS8HP)
    ``` 
    The ldo gen tool is successfully setup if the the builds generates `generators/ldo-gen/work/*.gds.gz` at the end of the run. 


# Running the tools
1. Prepare an input spec "Input_Spec_File.json" file similar to `fasoc/generators/ldo-gen/test.json`. An example of the input spec file with variable descriptions is provided below.
    ```bash
    {
      "module_name": "ldoInst",
      "generator": "ldo-gen",
      "specifications": {
        "vin": 0.7,
        "imax": "1e-03"
      }
    }
    ```
   Each of the input spec file variables are described below:
   
    __module_name__
    - Name of the LDO design.
    
    __generator__
    - This variable must be `ldo-gen`. This variable is added as a pre-check condition to catch interfacing mistakes between the SoC-Synthesis tool and the LDO generator.
    
    __specifications__
    - _vin_
      - Input Voltage of the LDO. 
      - `vin` values from the set [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3] are supported for TSMC65lp PDK 
      - `vin` values from the set [0.6, 0.7, 0.8, 0.9, 1.0] are supported for GFBiCMOS8HP PDK.
    - _imax_
      - Maximum Output Load Current. 
      - `imax` values in the range [0.5e-03, 25e-03] are supported for TSMC65lp PDK.
      - `imax` values in the range [0.5e-03, 1.5e-03] are supported for GFBiCMOS8HP PDK.

1. Running the LDO generator. 
   To run the LDO generator, execute the below command from any location.
    ```bash
    .{Path_to_Generator_Folder}/tools/ldo_gen.py --specfile {Input_Spec_File.json} --output {Output_Folder} --platform {Technology_Node} [--mode {Run_Mode}] [--clean]
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
   
1. Running the model generator in standalone mode. 
   Ensure you have the correct `fasoc/config/platform_config.json` file and run the following commands
    ```bash
    .{Path_to_Generator_Folder}/tools/ldo_model.py --platform {Technology_Node}
    ```
   `Technology_Node` must be either "tsmc65lp" or "gfbicmos8hp" as of now.
    
# Tool Directory Structure
```bash
    ldo-gen
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
   - Folder with source scripts of the tool that encapsulates the LDO macro generation process. 

   __Makefile__
   - Makefile to perform a test run of the LDO generator.

   __Readme.md__
   - Read me file with the instructions for running the tool.

   __test.json__
   - Sample LDO input specification file in json format. Makefile uses this file to perform a test run of the tool. 
