#!/usr/bin/env python3.7.3
from collections import namedtuple


class CellProps:
    """
    Common attributes of all the auxcells are abstracted thourgh the CellProps Class.
    """
    def __init__(self):
        self.input_pins  = []
        self.output_pins = []
        self.inout_pins = []
        self.power_pins  = []
        self.ground_pins = []
        self.layer_props = {}
        self.size_x = 0
        self.size_y = 0

    def update_cellname(self, name=None):
        self.name = name

    def update_pininfo(self, pin_map=None):
        self.pininfo = pin_map
        for keys, values in self.pininfo.items():
            if values[1] == 'input':
                self.input_pins.append(keys)
            elif values[1] == 'output':
                self.output_pins.append(keys)
            elif values[1] == 'inout':
                self.inout_pins.append(keys)
            elif values[1] == 'power':
                self.power_pins.append(keys)
            elif values[1] == 'ground':
                self.ground_pins.append(keys)

    def update_layout_props(self, is_layout_only=False, mirror_x=True, mirror_y=True):

        self.layer_props["is_layout_only"] = is_layout_only
        self.layer_props["mirror_x"] = mirror_x
        self.layer_props["mirror_y"] = mirror_y

    def update_orientations(self, orientations=[]):
        self.orientations = orientations

    def update_active_power(self, active_power=0):
        self.active_power = active_power

    def update_leak_power(self, leak_power=0):
        self.leak_power = leak_power

    def update_delay(self, delay=0):
        self.delay = delay

    def update_column_muxing(self, column_muxing):
        self.column_muxing = column_muxing

    def update_size(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y

    def get_cellname(self):
        return self.name

    def get_pininfo(self):
        return self.pininfo

    def get_input_pins(self):
        return self.input_pins

    def get_output_pins(self):
        return self.output_pins

    def get_inout_pins(self):
        return self.inout_pins

    def get_power_pins(self):
        return self.power_pins

    def get_ground_pins(self):
        return self.ground_pins

    def get_active_power(self):
        return self.active_power

    def get_leak_power(self):
        return self.leak_power

    def get_delay(self):
        return self.delay

    def get_layout_props(self):
        return self.layer_props

    def get_size(self):
        _get_size = namedtuple("get_size", ["size_x", "size_y"])
        return _get_size(self.size_x, self.size_y)

    def get_orientations(self):
        return self.orientations

    def is_column_muxed(self):
        return self.column_muxing


