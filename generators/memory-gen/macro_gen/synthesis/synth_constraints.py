def constraints_gen(fh):
    from private.apr_pymodules.constraints import *
    fh.write(set_donot_touch('dc', '*'))
