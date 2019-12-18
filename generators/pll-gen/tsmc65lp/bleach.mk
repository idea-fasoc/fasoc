# bleaching generated files in pll-gen 


# Attempts to only bleach one mw library target
bleach_pll:
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/blocks	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/checkDesign	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/checkPoints
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/logs
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/src/*
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/*dclib
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/vpath
	rm -f ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/*.log
	rm -f ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/query_results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/reports
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/export
	rm -f ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/tool_versions.txt			

bleach_dco:
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/blocks	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/checkDesign	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/checkPoints
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/logs
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/*dclib
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/vpath
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/*.log
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/query_results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/reports
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/export
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/tool_versions.txt			

bleach_extraction:
	rm -rf extraction/run/svdb
	rm -f extraction/run/*	
	rm -f extraction/sch/*	
	rm -f extraction/layout/*	

bleach_dcoPex:
	rm -f HSPICE/pex_NETLIST/*
	rm -f HSPICE/pex_TB/*

bleach_work:
	rm -f work/*
	
bleach_all:
	rm -f work/*
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/src/*
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/blocks	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/checkDesign	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/checkPoints
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/logs
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/*dclib
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/vpath
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/*.log
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/query_results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/reports
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/export
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_pll/tool_versions.txt			
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/blocks	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/checkDesign	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/checkPoints
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/logs
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/*dclib
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/vpath
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/*.log
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/query_results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/reports
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/export
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_dco/tool_versions.txt			
	rm -rf extraction/run/svdb
	rm -f  extraction/run/*	
	rm -f  extraction/sch/*	
	rm -f  extraction/layout/*	

