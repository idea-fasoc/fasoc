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
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/src/*
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/blocks	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/checkDesign	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/checkPoints
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/logs
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*dclib
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/vpath
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*.log
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/query_results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/reports
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/export
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*_dclib
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/tool_versions.txt			
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*.lef			
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/src/*
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/blocks	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/checkDesign	
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/checkPoints
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/logs
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/*dclib
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/vpath
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/*.log
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/query_results
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/reports
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/export
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/*_dclib
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/flow_ffdco/tool_versions.txt			
	rm -rf ./../../../private/generators/pll-gen/tsmc65lp/extraction/run/svdb
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/extraction/run/*	
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/extraction/sch/*	
	rm -f  ./../../../private/generators/pll-gen/tsmc65lp/extraction/layout/*	

