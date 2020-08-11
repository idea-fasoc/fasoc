
# DCDC-GEN: Switched Capacitor DC-DC Converter Generation
This is a fully autonomous tool to generate a switched capacitor DC-DC converter circuit from user specification to GDSII enabling autonomous power mangement in SoC design.
See more at https://fasoc.engin.umich.edu/dc-dc-converter/

# Version Details
```
Version : Alpha-1.0
Date    : June 11, 2020
```

# What's in the release
- First version of the tool. 
- Generates the DC-DC macro and its associated views (GDS, LEF, LIB, DB and CDL) for the given user specs.
- This release includes:
  - Synthesizable DC-DC verilog generation.
  - Synthesis and PNR of the DC-DC.
  - Performing the physical verification (PV) check.
  - Generating the associated views.

# Environment Setup
Ensure that your machine has all of the required tools setup and have access to the technology PDK. More instructions on this step can be found at https://github.com/idea-fasoc/fasoc/blob/master/README.md


# Tool Setup
1. Add the Auxiliary library and Model directory paths to the [`fasoc/config/platform_config.json`](https://github.com/idea-fasoc/fasoc/blob/master/config/platform_config.json) file under the corresponding technology node. `dcdc-gen` currently supports gf12lp nodes.
   
1. Run the test script from `dcdc-gen` folder to ensure the generator tool and the model tool are correctly setup
    ```bash
    make gen_12lp_macro
    ``` 
    The dcdc gen tool is successfully setup if the the builds generates `generators/dcdc-gen/work/*.v` at the end of the run. 


# Running the tools
1. Prepare an input spec "Input_Spec_File.json" file similar to `fasoc/generators/dcdc-gen/test.json`. An example of the input spec file with variable descriptions is provided below.
    ```bash
    {
       "module_name": "DCDC_TOP_0p74V_0p1mA",
       "generator": "dcdc-gen",
       "specifications": {
          "Iload (mA)": 0.1,
          "Output voltage (V)": 0.74,
          "Area (mm^2)" : 0.1,
          "Efficiency (%)" : 80,
          "Clock frequency (kHz)" : 10000
       }
    }
 
    ```
 
# Tool Directory Structure
```bash
    dcdc-gen
    |--- tools
    |--- Makefile
    |--- README.md
    |--- test.json
```
   __tools__
   - Folder with source scripts of the tool that encapsulates the DCDC macro generation process. 

   __Makefile__
   - Makefile to perform a test run of the DCDC generator.

   __Readme.md__
   - Read me file with the instructions for running the tool.

   __test.json__
   - Sample DCDC input specification file in json format. Makefile uses this file to perform a test run. 
