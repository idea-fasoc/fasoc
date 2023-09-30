# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 12:14:17 2019
@author: SumanthKamineni
"""
import os
# import matplotlib.pyplot as plt
from optparse import OptionParser
# import numpy as np
from globals import global_utils


def mem_arch_config_parser(mem_arch_config):
    """
        Parsers the input spec file and creates the necessary variables.
    """
    from globals import global_utils

    arch_config_dic = global_utils.yaml_config_parser(mem_arch_config)

    return arch_config_dic


def main():
    parser = OptionParser()
    parser.add_option('-s', '--specfile',
                      type='string',
                      dest='Spec',
                      help='''Configuration file in Json format with Specifications of the memory to be generated.
                         Ex: -c sram_config.json or --Config= sram_config.json ''',
                      default='')

    (options, argv) = parser.parse_args()
    global p_options
    p_options = {}
    p_options['SpecFile'] = options.Spec
    global rundir
    rundir = os.getcwd()
    sram_comps, no_words, word_size, voltage, frequency, BC_6T, min_colspb, max_rowspb, max_colspb = mem_arch_config_parser(
        p_options['Specfile']);  # Parses the spec file to grab the SRAM specs

if __name__ == '__main__':
    main()
