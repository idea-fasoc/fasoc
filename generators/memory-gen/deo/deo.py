#!/usr/bin/env python3

from datetime import time
from decimal import Decimal
from deo.sram_char import SRAMChar
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class DEO(SRAMChar):
    """ Explores the design space, optimizes the design through sensitivity analysis and picks the components that
    satisfy the user specifications"""
    ppo_arch_options: list

    def __init__(self):
        super(DEO, self).__init__()
        self._config_options = []
        self.fh_sramed = self.get_sram_ed_handler()
        self.auxcells = []

    def get_mem_config_options(self, no_words, word_size, col_mux_range):
        """
        Determines the possible memory architecture options for the specs specified in the input spec file based on
        the sram_arch_config.yaml file.
        """

        # Grab the mem_architecture configuration file from Global configurations.
        gen_dir = os.path.abspath(__file__)
        globals_dir = os.path.join(gen_dir, "globals")
        mem_config_spec = os.path.join(globals_dir, "configs", "mem_cofig.yaml")

        # Obtain the architecture ranges.
        from globals import mem_arch_config_parser
        # noinspection PyAttributeOutsideInit
        self.config_dic = mem_arch_config_parser(mem_config_spec)

        min_words_prow_pbank = self.config_dic["min_words_prow_pbank"]
        min_words_pcol_pbank = self.config_dic["min_words_pcol_pbank"]

        min_rows_pbank = min_words_prow_pbank * word_size
        min_cols_pbank = min_words_pcol_pbank * word_size
        max_rows_pbank = self.config_dic["max_rows_pbank"]
        max_cols_pbank = self.config_dic["max_cols_pbank"]

        # Obtain the technology specific Col Mux range from tech file.
        min_col_mux = int(min_cols_pbank / word_size)
        max_col_mux = int(max_cols_pbank / word_size)

        # Use the Col-mux range from the technology file to limit the no-cols.
        # Reason: Limitation comes from the availability of the auxcell layouts corresponding to the column mux range.
        tech_colmux_range = col_mux_range
        if not min_col_mux in tech_colmux_range:
            min_col_mux = min(tech_colmux_range)
        if not max_col_mux in tech_colmux_range:
            max_col_mux = max(tech_colmux_range)

        min_cols_pbank = min_col_mux * word_size
        max_cols_pbank = max_col_mux * word_size

        # Check the min and maximum words per bank
        min_wordspb: int = int(min_rows_pbank * min_cols_pbank / word_size)
        max_wordspb: int = int(max_rows_pbank * max_cols_pbank / word_size)
        # Initialize the max and min banks
        max_banks = 0
        min_banks = 0
        if no_words < min_wordspb:
            max_banks = 1
            min_banks = 1
        elif no_words >= max_wordspb:
            max_banks = int(no_words / min_wordspb)
            min_banks = int(no_words / max_wordspb)

        # Get the possible banks options.
        banks_array = [min_banks]
        banks_count = min_banks
        while banks_count < max_banks:
            banks_count = banks_count * 2
            banks_array.append(banks_count)
        print(banks_array)

        for nob in banks_array:
            rows_array = []
            cols_array = []
            row = min_rows_pbank
            words_pbank = no_words / nob
            print("words_pbank %f" % words_pbank)
            while row <= max_rows_pbank:
                column = int((word_size * words_pbank) / row)

                if row <= max_rows_pbank and max_cols_pbank >= column >= min_cols_pbank:
                    rows_array.append(row)
                    cols_array.append(column)
                row = row * 2
            self._config_options.append([nob, rows_array, cols_array])

        return self._config_options

    def get_sram_pareto(self, tech_config_dic, sram_config_options, sram_bank_arch, sram_specs):

        self.sram_config_options = sram_config_options # List of [#b, #r, #c]
        self.sram_bank_arch = sram_bank_arch # Dictionary with row_periphery, col_periphery, and bitcellarray.
        self.sram_specs = sram_specs # Dic.

        sram_ed_output_file = f"SRAM_ED_{self.sram_specs['no_words']:d}_{self.sram_specs['word_size']:d}" \
                              f"_{self.sram_specs['target_vdd']:f}_{self.sram_specs['target_delay']:f}.txt"
        self.fh_sramed = self.get_sram_ed_handler(sram_ed_output_file) # which dir?

        start = time.time()

        # For each arch option, pass the auxcells, mem_specs to the sram_char and the get the SRAM ED.

        for sram_config in self.sram_config_options:
            # Annotation used:
            # sram_config: [bank, no_rows, no_cols]
            # sram_specs: ({sram_specs["sram_name"] = sram_name
            #         sram_specs["no_words"] = no_words
            #         sram_specs["word_size"] =word_size
            #         sram_specs["target_vdd"] = opreating_voltage
            #         sram_specs["target_freq"] = target_frequency
            #         sram_specs["process_info"] = process_info

            # Get the SRAM Energy and delay values for the given architecture and the memory specifications.
            sram_ed = self.get_sram_ed(tech_config_dic, sram_config, self.sram_bank_arch, self.sram_specs)
            self.fh_sramed.write(
                f"{self.sram_specs['no_words']:d}, {self.sram_specs['word_size']:d}, {sram_config[0]:d}, {sram_config[1]:d}, "
                f"{sram_config[2]:d}, {self.sram_specs['target_vdd']:f}, {self.sram_specs['target_delay']:f}, "
                f"{Decimal(sram_ed[0] * 1e9):f}, {Decimal(sram_ed[1] * 1e12):f}\n")

        self.fh_sramed.close()
        end = time.time()
        print(f"Runtime of the pareto generation is {end - start}")

        # Obtain the SRAM pareto points.
        df = pd.read_table(sram_ed_output_file, sep=', ')
        energy_pts = df['SRAM_Energy(pJ)']
        delay_pts = df['SRAM_Delay(ns)']
        ed_pair = np.zeros((len(df.index), 2))
        for i in df.index:
            ed_pair[i][0] = delay_pts[i]
            ed_pair[i][1] = energy_pts[i]

        self.pareto_bool_indexes = self.get_pareto(ed_pair)
        self.ppo_sram_ed = ed_pair[self.pareto_bool_indexes] # ppo --> pareto points only

        # self.plot_pareto(SRAM_ED_Paretos)

        # Write the pareto points (ed values and the arch options) to an output file.
        sram_ed_ppo_output_file = f"sram_ed_ppo_output_{self.sram_specs['no_words']:d}_{self.sram_specs['word_size']:d}" \
                                     f"_{self.sram_specs['target_vdd']:f}_{self.sram_specs['target_delay']:f}.txt"
        pareto_df = df[self.pareto_bool_indexes] # data frame with pareto only points.
        # Write the pareto only points including the arch options to an output file.
        pareto_df.to_csv(sram_ed_ppo_output_file, sep=',', index=False)

        # Update the all architecture options to pareto architecture points only and the perform the optimization.
        sram_config_options_array = np.array(self.sram_config_options)
        self.ppo_sram_config_options = sram_config_options_array[self.pareto_bool_indexes]

        return self.ppo_sram_ed, self.ppo_sram_config_options

    @staticmethod
    def check_pareto_points(sram_specs, sram_paretos):
        """ Determines if any of pareto points staisfy the user specifications"""
        target_delay = sram_specs['target_delay']
        spec_stisfied_points = np.ones(sram_paretos.shape[0], dtype=bool)
        for i, c in enumerate(sram_paretos):
            if sram_paretos[i][1] <= target_delay:  # Keep any point with a lower delay to pick for min energy
                spec_stisfied_points[i] = True
            else:
                spec_stisfied_points[i] = False

        return spec_stisfied_points # List with Bool values

    def optimization(self):
        """ For given set of pareto points, perform the sensitivity analysis and obtain the sram components that
        meets the sram specifications.
        :returns : New auxcells updated SRAM arch, the ED values, and the bank config.
        """
        # Automation in-progress.
        pass

    def get_pareto(self, data_set):

        pareto_pts = np.ones(data_set.shape[0], dtype=bool)
        for i, c in enumerate(data_set):
            if pareto_pts[i]:
                pareto_pts[pareto_pts] = np.any(data_set[pareto_pts] < c, axis=1)  # Keep any point with a lower cost
                pareto_pts[i] = True  # And keep self
        return pareto_pts

    @staticmethod
    def plot_pareto(ed_total_points, ed_pareto_points):

        # Get energy and delay value in SRAM_ED dict
        energy_pts = ed_total_points['SRAM_Energy(pJ)']
        delay_pts = ed_total_points['SRAM_Delay(ns)']

        plt.scatter(delay_pts, energy_pts)
        plt.plot(ed_pareto_points[:, 0], ed_pareto_points[:, 1], color='r')
        plt.xlabel('Delay (ns)')
        plt.ylabel('Energy(pJ)')
        plt.grid()
        plt.legend()
        plt.savefig('fig.svg')
        plt.clf()

    @property
    def get_sram_ed_handler(self, file_name):
        fh = open(file_name, 'w')
        fh.write("No_Words, Word_Size, No_Banks, No_Rows, No_Cols, Voltage, Frequency, SRAM_Delay(ns), SRAM_Energy("
                 "pJ)\n")
        return fh

if __name__ == '__main__':
    deo_inst = DEO()
