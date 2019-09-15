require "json"
require 'IPXACT2009API'
load File.dirname(__FILE__) + "/parse_json.rb"

infile = getConfigItem("arg1", :default => ("arg1"))
design = getConfigItem("arg2", :default => ("arg2"))
outfile_hier = getConfigItem("arg3", :default => ("arg3"))
outfile_conn = getConfigItem("arg4", :default => ("arg4"))
parse_json(infile, design, outfile_hier, outfile_conn)