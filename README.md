

# FASoC: Fully-Autonomous SoC Synthesis using Customizable Cell-Based Synthesizable Analog Circuits
The FASoC Program is focused on developing a complete system-on-chip (SoC) synthesis tool from user specification to GDSII.
See more at https://fasoc.engin.umich.edu/

FASoC tool can be operated in three modes, "Verilog", "Macro" and "Full" modes.

## Verilog Generation Mode
The provided generators can generate fully synthesizable verilog products using the user input specification file. The generated verilog will be derived from pre-characterized modules. Future releases of the tool will also generate a human readable constraint guidance that will aid in maximizing post layout design performance.

### Setup instructions
1. Ensure your machine has the correct python version and all of the python modules required to run through the FASoC flow. 
    - Requirements: Python 3.6/3.7 (packages getopt, math, numpy, os, re, shutil, subprocess, sys, smtplib, datetime, logging, matplotlib). Python 3 is not supported.

## Macro/Full Generation Mode
The macro generation mode will generate hard macros in addition to the verilog. These hard macros are synthesized and implemented versions of the verilog output using recommended constraints and physical guidance. This mode will require the commercial tools, access to the standard/cells, PDK and other tools. It will also require an automated flow (cadre flow) as well as several private files that are restricted due to NDA requirements.

### Setup instructions
1. Additional tool requirements:
    - Cadre Flow:
      - Synopsys Design Compiler (2016.03-SP2)
      - Cadence Innovus (v15.21-s080_1)
      - Synopsys Primetime (2016.06)
      - Mentor Graphics Calibre (2016.1_23.16)
    - Synopsys HSPICE (2017.03-SP1)
    - Cadence Liberate (16.1.1.132)
    - Cadence Spectre (15.1.0)

    Newer versions of the tools are expected, but not guaranteed to work.

1. Run the environment checker script to ensure all the tools are setup
    ```bash
    make check_env
    ```

1. Ensure you have access to the required private repository for FASoC. Please contact ajayi@umich.edu if you need access

1. Ensure you have ssh keys setup for github

1. Clone the FASoC repository
    ```bash
    git clone git@github.com:idea-fasoc/fasoc.git
    ```

1. Initialize the submodules
    ```bash
    cd fasoc
    git submodule update --init --recursive
    ```

1. Setup the cadre flow to for your specific location. The "Macro/Full" modes currently requires TSMC65LP PDK and ARM standard cells. More instructions on how to setup this particular platform can be found in the [Cadre Flow Guide](doc/Cadre%20Flow%20Guide.pdf)


1. Change directory to the generator of interest and follow instructions in the readme
