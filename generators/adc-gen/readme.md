
# ADC-GEN: SAR ADC generator
This is a fully autonomous tool to generate a successive-approximation ADC circuit from user specification to GDSII in SoC design.
See more at https://fasoc.engin.umich.edu


# Environment Setup
1. Ensure that your machine has all of the required tools setup and have access to the technology PDK. More instructions on this step can be found at https://github.com/idea-fasoc/fasoc/blob/master/README.md

2. Add the Auxiliary library and Model directory paths to the `fasoc/config/platform_config.json` file under the corresponding technology node. An example of the platform_config is shown below
     ```bash
   "tsmc65lp": {
      "nominal_voltage": 1.2,
      "aux_lib": "<PATH_TO_AUX_LIB>",
      "model_lib": "<PATH_TO_MODEL_LIB>",
      "sram_2kb_lib": "This is not necessary for ADC-GEN",
      "calibreRules": "<PATH_TO_PDK_CALIBRE_RULES>",
      "hspiceModels": "<PATH_TO_PDK_SPICE_MODELS>"
    } 
    ```  


3. Run the test script to ensure the generator tool and the model tool are correctly setup
    ```bash
    make gen
    ```

    The adc gen tool is successfully setup if the the builds generates `generators/adc-gen/work/*.gds.gz` at the end of the run. 

# Running the tools
1. Prepare an input spec "Input_Spec_File.json" file similar to `fasoc/generators/adc-gen/test.json`

2. Running the adc-gen generator. 
   "--ouptut" specifies the directory to store the final output directory of the tool
     ```bash
     .{Path_to_Generator_Folder}/tools/adc-gen.py --specfile {Input_Spec_File.json} --output {Output_Folder} --platform {Technology_Node} [--mode {Run_Mode}] [--clean]
    ```

3. Running the model generator in standalone mode. 
   Ensure you have the correct `fasoc/config/platform_config.json` file and run the following commands
    ```bash
    python tools/adc-gen.py --platform tsmc65lp
    ```

# Tool Directory Structure
```bash
private/adc-gen
|--- extraction
|--- flow
|--- hspice 
```
   __extraction__
   - Folder with PEX config files to extract parasitics of the final desgin.
  
   __flow__
   - Folder with the synthesis and APR scripts that runs the CADRE flow.  
  
   __hspice__
   - Folder with model simulation files to run post-pex simulations.

```bash
adc-gen   
|--- tools
|--- Makefile
|--- README.md
|--- test.json
```
   __tools__
   - Folder with source scripts of the tool that encapsulates the SAR ADC macro generation process. 

   __Makefile__
   - Makefile to perform a test run of the SAR ADC generator.

   __Readme.md__
   - Read me file with the instructions for running the tool.

   __test.json__
   - Sample adc-gen input specification file in json format. Makefile uses this file to perform a test run of the tool. 

