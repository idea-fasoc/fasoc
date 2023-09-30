#!/usr/bin/env python3.7.3

def sram_6t_ed_model(auxcells, word_size, no_banks, no_rows, no_cols) -> list:
    ##################################################
    # ############## Bank Leakage Model ############ #
    ##################################################

    # Leakage during read operation per bank.
    read_bank_leakage = auxcells['Bitcell_read_leakage'].get_energy() * (no_rows - 1) * no_cols \
                        + auxcells["RowDecoder"].get_energy() * (no_rows - 1) \
                        + auxcells["WriteDriver"].get_energy() * word_size

    # Leakage during Write operation per bank.
    write_bank_leakage = auxcells['Bitcell_write_leakage'].get_energy() * (no_rows - 1) * word_size \
                         + auxcells['Bitcell_read_leakage'].get_energy() * (no_rows - 1) * (no_cols - word_size) \
                         + auxcells["RowDecoder"].get_energy() * (no_rows - 1) \
                         + auxcells["SenseAmp_VLSA"].get_energy() * word_size

    # Leakage during Hold mode operation per bank.
    hold_bank_leakage = auxcells['Bitcell_hold_leakage'].get_energy() * no_rows * no_cols \
                        + auxcells["ColDecoder"].get_energy() \
                        + auxcells["RowDecoder"].get_energy() \
                        + auxcells["PreCharge"].get_energy() * no_cols \
                        + auxcells["Read_Tcrit"].get_energy() * no_cols \
                        + auxcells["SenseAmp_VLSA"].get_energy() * word_size

    # Operation based Multi-bank Leakage calculation.
    read_op_leakage = hold_bank_leakage * (no_banks - 1) + read_bank_leakage
    write_op_leakage = hold_bank_leakage * (no_banks - 1) + write_bank_leakage

    # Total read energy
    read_energy = auxcells["multi_bank_input"].get_energy() \
                  + auxcells["timer"].get_energy() \
                  + auxcells["wl_driver"].get_energy() \
                  + auxcells["pre_charge"].get_energy() * no_cols \
                  + auxcells["bitcell"].get_energy() * no_cols \
                  + auxcells["sense_amp"].get_energy() * word_size \
                  + auxcells["output_driver"].get_energy() * word_size \
                  + auxcells["multi_bank_output"].get_energy() + \
                  + read_op_leakage

    # Total write energy
    write_energy = auxcells["multi_bank_input"].get_energy() \
                   + auxcells["timer"].get_energy() \
                   + auxcells["wl_driver"].get_energy() \
                   + auxcells["pre_charge"].get_energy() * no_cols \
                   + auxcells["bitcell"].get_energy() * no_cols \
                   + auxcells["write_driver"].get_energy() * word_size \
                   + write_op_leakage

    # Total read delay
    read_delay = auxcells["multi_bank_input"].get_delay \
                 + max(auxcells["timer"].get_delay(), auxcells["PreCharge"].get_delay()) \
                 + auxcells["wl_driver"].get_delay() \
                 + auxcells["bitcell"].get_delay() \
                 + auxcells["sense_amp"].get_delay() \
                 + auxcells["output_driver"].get_delay() \
                 + auxcells["multi_bank_output"].get_delay()

    # Total write delay
    write_delay = auxcells["multi_bank_input"].get_delay \
                  + max(auxcells["timer"].get_delay(), auxcells["pre_charge"].get_delay()) \
                  + auxcells["write_driver"].get_delay() \
                  + auxcells["wl_driver"].get_delay() \
                  + auxcells["bitcell"].get_delay()

    sram_ed = [max(read_delay, write_delay), (write_energy + read_energy) / 2.0]

    return sram_ed
