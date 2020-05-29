# bleaching generated files in pll-gen 


# Attempts to only bleach one mw library target
bleach_pll:
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/blocks	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/checkDesign	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/checkPoints
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/logs
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/src/*
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*dclib
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/vpath
	rm -f ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*.log
	rm -f ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/query_results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/reports
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/export
	rm -f ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/tool_versions.txt			
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/blocks	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/checkDesign	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/checkPoints
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/logs
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/src/*
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/*dclib
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/vpath
	rm -f ./../../private/generators/pll-gen/gf12lp/flow_pdpll/*.log
	rm -f ./../../private/generators/pll-gen/gf12lp/flow_pdpll/query_results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/reports
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/export
	rm -f ./../../private/generators/pll-gen/gf12lp/flow_pdpll/tool_versions.txt			

bleach_dco:
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/blocks	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/checkDesign	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/checkPoints
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/logs
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/*dclib
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/vpath
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_dco/*.log
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_dco/query_results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/reports
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/export
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_dco/tool_versions.txt			
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_dco/*.lef			
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/blocks	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/checkDesign	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/checkPoints
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/logs
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/*dclib
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/vpath
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_dco/*.log
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_dco/query_results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/reports
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/export
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_dco/tool_versions.txt			
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_dco/*.lef			

bleach_outbuff_div:
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/blocks	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/checkDesign	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/checkPoints
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/logs
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/*dclib
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/vpath
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/*.log
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/query_results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/reports
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/export
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/tool_versions.txt			
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/*.lef			
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/blocks	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/checkDesign	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/checkPoints
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/logs
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/*dclib
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/vpath
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/*.log
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/query_results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/reports
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/export
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/tool_versions.txt			
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_outbuff_div/*.lef			

bleach_work:
	rm -f work/*
	
bleach_flows:
	rm -f work/*
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_dco/*.lef			
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/blocks	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/checkDesign	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/checkPoints
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/logs
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/*dclib
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/vpath
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_dco/*.log
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_dco/query_results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/reports
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_dco/export
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_dco/tool_versions.txt			
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/src/*
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/blocks	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/checkDesign	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/checkPoints
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/logs
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*dclib
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/vpath
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*.log
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/query_results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/reports
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/export
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*_dclib
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/tool_versions.txt			
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_pdpll/*.lef			
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/extraction/run/svdb
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/extraction/run/*	
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/extraction/sch/*	
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/extraction/layout/*	
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_dco/*.lef			
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/blocks	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/checkDesign	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/checkPoints
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/logs
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/*dclib
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/vpath
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_dco/*.log
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_dco/query_results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/reports
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_dco/export
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_dco/tool_versions.txt			
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/src/*
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/blocks	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/checkDesign	
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/checkPoints
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/logs
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/*dclib
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/vpath
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_pdpll/*.log
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_pdpll/query_results
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/reports
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/export
	rm -rf ./../../private/generators/pll-gen/gf12lp/flow_pdpll/*_dclib
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_pdpll/tool_versions.txt			
	rm -f  ./../../private/generators/pll-gen/gf12lp/flow_pdpll/*.lef			
	rm -rf ./../../private/generators/pll-gen/gf12lp/extraction/run/svdb
	rm -f  ./../../private/generators/pll-gen/gf12lp/extraction/run/*	
	rm -f  ./../../private/generators/pll-gen/gf12lp/extraction/sch/*	
	rm -f  ./../../private/generators/pll-gen/gf12lp/extraction/layout/*	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/blocks	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/checkDesign	
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/checkPoints
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/logs
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/*dclib
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/vpath
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/*.log
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/query_results
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/reports
	rm -rf ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/export
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/tool_versions.txt			
	rm -f  ./../../private/generators/pll-gen/tsmc65lp/flow_outbuff_div/*.lef			

bleach_all:
	rm -rf ./../../private/generators/pll-gen/tsmc65lp
	rm -rf ./../../private/generators/pll-gen/gf12lp
	rm -rf ./work/*


