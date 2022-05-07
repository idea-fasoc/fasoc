
# LDO-GEN: Low Dropout Regulator Generation
This is a fully autonomous tool to generate a low drop out regulator circuit from user specification to GDSII enabling autonomous power mangement in SoC design.
See more at https://fasoc.engin.umich.edu/digital-ldo/

# Version Details
```
Version : Beta-2.0                                                             
Date    : May 6, 2022
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
1. Setup the tools and pdk information (see the following variables) in the [`fasoc/config/platform_config.json`](https://github.com/idea-fasoc/fasoc/blob/master/config/platform_config.json) file.
    ```bash
    "synthTool": <Synthesis tool to be used. We only support 'dc' and 'genus' currently. 'genus' options is only available for 'gf12lp' platform.>,
    "simTool": <Simulation tool to be used. We only support 'hspice' and 'finesim' currently.>,
    "extractionTool": "calibre",
    "netlistTool": "calibredrv",
    ```

1. Add the Auxiliary library and Model directory paths to the [`fasoc/config/platform_config.json`](https://github.com/idea-fasoc/fasoc/blob/master/config/platform_config.json) file under the corresponding technology node. `ldo-gen` currently supports tsmc65lp, gfbicmos8hp and gf12lp nodes. An example of the platform config with the variable descriptions is provided below.
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
    - Folder path containing the `ldoModel.json` file.
    
    __sram_2kb_lib__
    - This parameter is not required for ldo-gen tool.
    
    __calibreRules__
    - Folder path containing the calibre pex rule files.
    
    __hspiceModels__
    - Folder path containing the spice models of the technology node.
   
1. There are three modes of LDO-GEN tool, and the function of each mode is described in "Running the tools" section. Run the following commands as a validation for the LDO-GEN tool setup.
  
    __To ensure the "verilog" mode is correctly setup, run the below test command from `ldo-gen` folder.__
    - The ldo gen "verilog" mode is successfully setup if the the build generates `generators/ldo-gen/work/*.v` files at the end of the run.
    ```bash
    make gen_65lp (for TSMC65lp) or
    make gen_8hp  (for GFBICMOS8HP) or
    make gen_12lp (for GF12LP)
    ``` 
     
    __To ensure the "macro" mode is correctly setup, run the below test command from `ldo-gen` folder.__
    - The ldo gen "macro" mode is successfully setup if the the build generates `generators/ldo-gen/work/*.gds.gz` files at the end of the run. 
    ```bash
    make gen_65lp_macro (for TSMC65lp) or
    make gen_8hp_macro  (for GFBICMOS8HP) or
    make gen_12lp_macro (for GF12LP)
    ``` 
    
    
    __To ensure the "full" mode is correctly setup, run the below test command from `ldo-gen` folder.__
    - The ldo gen "full" mode is successfully setup if the the build generate `generators/ldo-gen/work/*.gds.gz` files and completes the run without any errors. 
    ```bash
    make gen_65lp_full (for TSMC65lp) or
    make gen_8hp_full  (for GFBICMOS8HP) or
    make gen_12lp_full (for GF12LP) --> use calibre version "2019.3_39.25" or higher for 12LP technology.
    ``` 
    

# Running the tools
1. Prepare an input spec "Input_Spec_File.json" file similar to `fasoc/generators/ldo-gen/test.json`. An example of the input spec file with variable descriptions is provided below.
    ```bash
    {
      "module_name": "ldoInst",
      "generator": "ldo-gen",
      "specifications": {
        "vin": 0.8,
        "imax": "1e-03",
        "dropout": 0.05
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
      - Input Voltage of the LDO in Volts. 
      - `vin` values from the set [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3] are supported for TSMC65lp & GFBiCMOS8HP PDKs.
      - `vin` values from the set [0.6, 0.7, 0.8, 0.9] are supported for GF12LP PDK.
    - _imax_
      - Maximum Output Load Current in Amperes. 
      - `imax` values in the range [0.5e-03, 25e-03] are supported for TSMC65lp & GFBiCMOS8HP PDKs.
      - `imax` values in the range [0.5e-03, 16e-03] are supported for GF12LP PDK.
    - _dropout_
      - Dropout betweein input and output (vin - vout) in Volts.
      - `dropout` values of 0.05 and 0.1 are currently supported for GF12LP PDK.
      - `dropout` value of 0.05 is currently supported for TSMC65lp & GFBiCMOS8HP PDKs.

1. Running the LDO generator. 
   To run the LDO generator, execute the below command from any location.
    ```bash
    .{Path_to_Generator_Folder}/tools/ldo_gen.py --specfile {Input_Spec_File.json} --output {Output_Folder} --platform {Technology_Node} [--mode {Run_Mode}] [--gf12lpTrack {GF12LP_Standard_Cell_Track}] [--useDefaultModel] [--clean]
    ```
   All the options specified in square brackets [] are optional. 
   
   When `--useDefaultModel` option is provided, the tool skips the modeling process and uses the model file downloaded from github instead of using the model file specified in [`platform_config.json`](https://github.com/idea-fasoc/fasoc/blob/master/config/platform_config.json) file.
   When `--clean` option is provided, the tool exits after a cleanup of the workspace. Each of the command line variables are described below in detail.
   
   __{Input_Spec_File.json}__
   - This file is similar to `test.json` file and contains the input specifications of the LDO module.
   
   __{Output_Folder}__
   - This variable specifies the directory where the final outputs of the tool are saved. "Output folder" is automatically cleaned by the tool, so make sure the "Output folder" is different from the default repo folders.
   
   __{Technology_Node}__
   - This variable must be either "tsmc65lp" or "gfbicmos8hp" as of now.
   
   __{Run_Mode}__
   - This must be either be "verilog", "macro" or "full". Default mode used is "verilog" if this option is not specified. 
     - "verilog" mode do not need access to the PDK or the CADRE flow and generates only the verilog description of the design. 
     - "macro" mode needs access to PDK/CADRE flow and generates the netlist and gds files along with the verilog description. 
     - "full" mode does a full post-pex extraction of the design netlist and layout files and runs a complete post-pex spice simulation.
   
   __{GF12LP_Standard_Cell_Track}__
   - This variable specifies the standard cell row height to be used for `gf12lp` technology must be either be "10P5T" or "9T". Default option used is "10P5T" if this option is not specified. 
     - "10P5T" : Standard Cell Height = 10.5 * track_height.
     - "9T"    : Standard Cell Height =  9.0 * track_height.
   
1. Running the model generator in standalone mode. 
   Ensure you have the correct `fasoc/config/platform_config.json` file and run the following commands
    ```bash
    .{Path_to_Generator_Folder}/tools/ldo_model.py --platform {Technology_Node}  [--gf12lpTrack {GF12LP_Standard_Cell_Track}]
    ```
   `Technology_Node` must be either be "tsmc65lp" or "gfbicmos8hp" or "gf12lp" as of now.
   `GF12LP_Standard_Cell_Track` must either be "10P5T" or "9T" as of now.
    
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
