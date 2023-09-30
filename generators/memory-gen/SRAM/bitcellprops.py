#!/usr/bin/env python3.7.3
from collections import namedtuple

from .cellprops import CellProps


class BitCellProps(CellProps):
    """
    Common attributes of all the auxcells are abstracted thourgh the CellProps Class.
    """

    def __init__(self):
        super().__init__()

    def update_orientations(self, orientations=[]):
        self.orientations = orientations

    def update_energy(self, energy=[0,0,0,0,0]):
        self.read_energy = energy[0]
        self.read_leakage_energy = energy[1]
        self.write_energy = energy[2]
        self.write_leakage_energy = energy[3]
        self.hold_energy = energy[4] #-> hold energy itself is leakage energy

    def update_delay(self, delay=[0, 0]):
        self.read_delay = delay[0]
        self.write_delay = delay[1]

    def get_read_energy(self):
        return self.read_energy

    def get_write_energy(self):
        return self.write_energy

    def get_hold_energy(self):
        return self.hold_energy

    def get_read_leakage_energy(self):
        return self.read_leakage_energy

    def get_write_leakage_energy(self):
        return self.read_energy

    def get_read_delay(self):
        return self.delay

    def get_write_delay(self):
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
