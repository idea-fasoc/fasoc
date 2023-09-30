import os
import sys
import re
import logging

global log
log = logging.getLogger(__name__)


def lef_parser(lef=None, cell=None):
    """ Parses the LEF file and returns all the required cell information.
    """

    from globals.global_utils import returnfileasstring

    lefstring = returnfileasstring(lef)
    # Can strip comments of the lef file if present.
    leflines = lefstring.split("\n")
    pCounter = 0
    lLine = leflines[pCounter].strip(" ;")
    cell_info = {}  # Will have Direction, Usage, and the co-ordinates. Bus is considered as individual
    try:
        while pCounter < len(leflines):
            lLine = leflines[pCounter].strip(" ;")
            if re.search("^MACRO\s+(\S+)", lLine):
                moduleName = re.search("^MACRO\s+(\S+)", lLine).group(1)
                cell_info['cell_name'] = moduleName
                cell_info['pin_info'] = {}
                pin_info = {}
                cell_info['pin_info']["input_pins"] = {}
                cell_info['pin_info']["output_pins"] = {}
                cell_info['pin_info']["power_pins"] = {}
                cell_info['pin_info']["ground_pins"] = {}
                input_pins = []
                output_pins = []
                power_pins = []
                ground_pins = []
                pCounter += 1
                lLine = leflines[pCounter].strip(" ;")
                while not re.search("^END\s+%s" % moduleName, lLine):
                    if re.search("\s*(PIN)\s+(\S+)", lLine):
                        pinName = re.search("(PIN)\s+(\S+)", lLine).group(2)  # Need to handle the busbitchars
                        pin_info[pinName] = {}
                        pCounter += 1
                        lLine = leflines[pCounter].strip(" ;")
                        pinName_sb = re.sub("\[", "\[", re.sub("\]", "\]", pinName))  # Adding the escape characters for
                        # pin bus bit characters to pass the re.search in while condition below.
                        while not re.search("\s*END\s+%s" % pinName_sb, lLine):
                            if re.search("\s*USE", lLine):
                                pinuse = re.search("\s*USE\s+(\S+)", lLine).group(1)
                                if pinuse.upper() == "POWER":
                                    pin_info[pinName]["USE"] = pinuse.upper()
                                    power_pins.append(pinName)
                                elif pinuse.upper() == "GROUND":
                                    pin_info[pinName]["USE"] = pinuse.upper()
                                    ground_pins.append(pinName)
                                else:
                                    pin_info[pinName]["USE"] = "SIGNAL"
                                pCounter += 1
                            elif re.search("^DIRECTION\s+(\S+)", lLine):
                                pindir = re.search("^DIRECTION\s+(\S+)", lLine).group(1)
                                pin_info[pinName]["DIRECTION"] = pindir.upper()
                                if pindir.upper() == 'INPUT':
                                    input_pins.append(pinName)
                                elif pindir.upper() == 'OUTPUT':
                                    output_pins.append(pinName)
                                pCounter += 1
                            elif re.search("\s*PORT$", lLine):
                                pin_info[pinName]['port'] = {}
                                pCounter += 1
                                lLine = leflines[pCounter].strip(" ;")
                                while not re.search("^\s*END$", lLine):
                                    if re.search("^\s*(LAYER)\s+[^VJ](\S+)", lLine):  # Excludes the VIA layers
                                        layerID = re.search("^(LAYER)\s+[^VJ](\S+)", lLine).group(2)
                                        pin_info[pinName]['port']["LAYER %s" % layerID] = []
                                        pCounter += 1
                                        lLine = leflines[pCounter].strip(" ;")
                                        while not (re.search("^\s*(LAYER)\s+(\S+)", lLine) or
                                                   re.search("^\s*END$", lLine)):  # port END
                                            match = re.search("\s*RECT(\s+(MASK \d)\s+|\s+)(.*)", lLine)
                                            shape_cord = match.group(3)
                                            shape_mask = match.group(2)
                                            pin_info[pinName]['port']["LAYER %s" % layerID].append(
                                                shape_cord.split(" "))
                                            pCounter += 1
                                            lLine = leflines[pCounter].strip(" ;")
                                    else:
                                        pCounter += 1
                                    lLine = leflines[pCounter].strip(" ;")
                                pCounter += 1  # for the while not END Pinname loop
                            else:
                                pCounter += 1
                            lLine = leflines[pCounter].strip(" ;")
                        cell_info['pin_info']["input_pins"] = {pin: pin_info[pin] for pin in input_pins}
                        cell_info['pin_info']["output_pins"] = {pin: pin_info[pin] for pin in output_pins}
                        cell_info['pin_info']["power_pins"] = {pin: pin_info[pin] for pin in power_pins}
                        cell_info['pin_info']["ground_pins"] = {pin: pin_info[pin] for pin in ground_pins}
                    elif re.search("\s*(CLASS)\s+(\S+)", lLine):
                        class_name = re.search("\s*(CLASS)\s+(\S+)", lLine).group(2)
                        cell_info['class'] = class_name
                        pCounter += 1
                    elif re.search("\s*(SIZE)\s+(\S+)", lLine):
                        size = re.search("\s*(SIZE)\s+(\S+)\s+BY\s+(\S+)", lLine)
                        size_x = size.group(2)
                        size_y = size.group(3)
                        cell_info['size'] = [size_x, size_y]
                        pCounter += 1
                    elif re.search("\s*(SYMMETRY)\s+(\S+)", lLine):
                        symmetry = re.search("\s*(SYMMETRY)\s+(.+)", lLine).group(2)
                        cell_info['symmetry'] = symmetry.split(" ")
                        pCounter += 1
                    else:
                        pCounter += 1
                    lLine = leflines[pCounter].strip(" ;")
                pCounter += 1  # For outside while loop
            elif re.search("\s*END\s+LIBRARY", lLine):
                break
            else:
                pCounter += 1

        return cell_info
    except Exception as ex_error:
        print("Exception while parsing LEF, near line - %s: %s" % (pCounter + 1, lLine), ex_error)


if __name__ == '__main__':
    lef = 'SRAM_2KB_128X128Core.lef'
    cell_info = lef_parser(lef)
    print(cell_info)