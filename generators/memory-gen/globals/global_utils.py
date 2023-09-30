import os, sys
import math
import re
import logging

global log
log = logging.getLogger(__name__)


def add(x, y):
    """
    Adds the number x and y and converts the result to a binary number.
    """
    maxlen = max(len(x), len(y))
    # Normalize lengths
    x = x.zfill(maxlen)
    y = y.zfill(maxlen)
    result = ''
    carry = 0
    for i in range(maxlen - 1, -1, -1):
        r = carry
        r += 1 if x[i] == '1' else 0
        r += 1 if y[i] == '1' else 0
        # r can be 0,1,2,3 (carry + x[i] + y[i])
        # and among these, for r==1 and r==3 you will have result bit = 1
        # for r==2 and r==3 you will have carry = 1
        result = ('1' if r % 2 == 1 else '0') + result
        carry = 0 if r < 2 else 1
    if carry != 0: result = '1' + result
    return result.zfill(maxlen)


def get_cell_size(lef):
    """ Parses the lef files and returns the pin info"""
    from collections import namedtuple

    pttrn = re.compile('\s+SIZE.+')
    with open(lef) as f:
        size = re.search(pttrn, f.read()).group(0)
    size_list = re.split(r'\s+', size)
    size_x = round(float(size_list[2]), 3)
    size_y = round(float(size_list[4]), 3)
    get_cell_size = namedtuple("get_cell_size", ["size_x", "size_y"])
    return get_cell_size(size_x, size_y)


def returnfileasstring(file):
    """ Opens the file, read all the lines and return it as a string"""
    with open(file) as f:
        file_str = f.read()
    return file_str


def json_config_parser(config_file):
    """ Parses the config file and returns a dict the list of the cells and connection"""
    import json
    try:
        with open(config_file) as fh:
            json_config_dic = json.load(fh)
    except ValueError as ex_err:
        print("Exception while loading the config file %s" % config_file, ex_err)
        sys.exit(1)

    return json_config_dic


def yaml_config_parser(config_file) -> dict:
    """ Parses the config file and returns a dict the list of the cells and connection
    :rtype: object
    """
    import yaml

    try:
        with open(config_file) as fh:
            yaml_config_dic = yaml.safe_load(fh)
    except yaml.YAMLError as err:
        print("Exception while loading the config file %s" % config_file, err)
        sys.exit(1)

    return yaml_config_dic


def pareto(data_set):
    import numpy as np
    pareto_pts = np.ones(data_set.shape[0], dtype=bool)
    for i, c in enumerate(data_set):
        if pareto_pts[i]:
            pareto_pts[pareto_pts] = np.any(data_set[pareto_pts] < c, axis=1)  # Keep any point with a lower cost
            pareto_pts[i] = True  # And keep self
    return pareto_pts


def str_class(classname):
    return getattr(sys.modules[classname], classname)


def graph(graph_elements):
    pass
# Create the multi-module, multi-class logger.
