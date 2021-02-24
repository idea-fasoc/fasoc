soc1:
	../../soc/python/soc.py --design ./design_ldo.json --mode verilog --database add
soc2:
	../../soc/python/soc.py --design ./design_ldo_pll.json --mode verilog --database add
soc3:
	../../soc/python/soc.py --design ./design_ldo_pll_mem.json --mode verilog --database add
soc4:
	../../soc/python/soc.py --design ./design_ldo.json --mode macro --database add
soc_macro:
	../../soc/python/soc.py --design ./design.json --mode macro --database add
soc_full:
	../../soc/python/soc.py --design ./design.json --mode full --database add
clean1:
	../../soc/python/clean.py --design ./design_ldo.json --connection remove --database remove
clean2:
	../../soc/python/clean.py --design ./design_ldo_pll.json --connection remove --database remove
clean3:
	../../soc/python/clean.py --design ./design_ldo_pll_mem.json --connection remove --database remove
clean4:
	../../soc/python/clean.py --design ./design_ldo.json --connection remove --database remove