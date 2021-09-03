# Correct-by-construction SoC design

## Running the tool
These are steps for running correct-by-construction SoC design:
* `cd soc`

* Refer to each of [generators](https://github.com/idea-fasoc/fasoc/tree/master/generators) to see instructions for providing aux_lib, calibreRuleFiles, model, SRAM_2KB directories. Please write these directoriers in `fasoc/config/platform_config.json` based on the technology node. Here is an example of platform_config.json for tsmc65lp:

![](docs/platform_config.png)

* Providing a design in json format. These are elements of such a design:
    * **"constrains":** The total power and area budget of the desired SoC
    * **"modules":** Different generators with different specfications that are desired to be included in the SoC
      *  **"module_name":** The design should have unique name for each module
      *  **"instance_name":** The name of each instances of the module. It should be noted even if one of the specifications of two modules are different, this means different modules not different instances. Instances are used if multiple instances from a module is needed.
      *  **"generator":** The generator name of the module. It should be one of the generators that is listed [here](https://github.com/idea-fasoc/fasoc/tree/master/generators).
      *  **"specifications":** Specifications of each module. Please refer to each [generator](https://github.com/idea-fasoc/fasoc/tree/master/generators) to find these specifications.  
    * There are several sample designs [here](https://github.com/idea-fasoc/fasoc/tree/master/tests) that it can be refered to.

* `soc.py --design {design_dir} --mode {design_mode} --database {add_remove}`
    * **{design_dir}:** The directory of the design.json file
    * **{design_mode}:** There are three modes for generating the SoC.
        * **"verilog":** Do not need access to the PDK or the CADRE flow and generates only the verilog description of the design.
        * **"macro":** Needs access to PDK/CADRE flow and generates the netlist and gds files along with the verilog description.
        * **"full":** Does a full post-pex extraction of the design netlist and layout files and runs a complete post-pex spice simulation.
    * **{add_remove}:**
        * **add**: Add the design and generated modules to the database
        * **remove**: Do not add the design and generated modules to the database

## Flow
The below figure shows the steps of coorect-by-construction SoC design:

![](docs/flow.jpg)

* **Parsing expet user design:** The tool parses the design.json file and passes the specifications and constraints to the searh engine of the database.
* **Database:** A MongoDB platform has been set up to record results of the previous runs individually for each generator. When a new design is processed, the tool first checks to find the modules in the database. If it finds a similar one, it passes and in this regard lot of time is saved. Otherwise, the tool asks generators to make the requested module and then it adds it to the database.
* **Constraints satisfication:** When all the modules have been either generated or pulled from the database, the total power and area of them are calculated and compared with the budget which is determined in the design.json. If it is satisfied, it goes to the last step of generating IP-XACT. Otherwise, using an ML model, predicts the most close design with the requested one that satisfies the constrains.
* **IP-XACT++ generator:** It first automatically connects the module to the appropriate bus ports using crossbar as it is described [here](https://github.com/idea-fasoc/fasoc/blob/master/doc/SoC%20Integrator%20Walkthrough.pdf). Then it creates IP-XACT++ of the whole design and passes to the Socrates. Please refer to [here](https://fasoc.engin.umich.edu/extended-ip-xact/) for more information about IP-XACT++.
* **Socrates:** Stiches the modules together using the provided IP-XACT++ and generates the Verilog file which can be passes to an APR tool for generating GDS-II.
 
For more information about how SoC Integration works you can go to [here](https://github.com/idea-fasoc/fasoc/blob/master/doc/SoC%20Integrator%20Walkthrough.pdf)
