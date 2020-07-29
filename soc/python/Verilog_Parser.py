#!/usr/bin/env python3
#MIT License

#Copyright (c) 2018 The University of Michigan

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
import re

def Verilog_Parser (path):
    

    with open(path) as f:
        lines=f.readlines()

    output_string=r'\s*output\s+\S+\s*'
    input_string=r'\s*input\s+\S+\s*'
    inout_string=r'\s*inout\s+\S+\s*'
    parenthese=r'\s*\);\s*'
    whitespace=r'\s*'
    comments=r'\s*//'
    ports=[]

    for line in lines:
        if not (re.match(comments,line) or re.fullmatch(whitespace,line)):
            port_segments=re.findall(r'(\S+)',line)#It will output all port names, port length, etc
            if re.match(output_string,line):
                ports.append(Verilog_cleaner(port_segments,'output','out',path)) 
            elif re.match(input_string,line):
                ports.append(Verilog_cleaner(port_segments,'input','in',path))
            elif re.match(inout_string,line):
                ports.append(Verilog_cleaner(port_segments,'inout','inout',path))
    return ports

def Verilog_cleaner (port_segments,input_output,inout,path):
    port={}
    operators = ['+','-','*','/']
    forbidden = [';',',',')']
    f=open(path)
    for port_segment in port_segments:

        if port_segment== input_output:
            pass
        elif port_segment == 'logic' or port_segment == 'wire':
            pass
        elif port_segment == ',':
            pass
        elif port_segment == ';':
            finish_tag = True
            pass
        elif '//' in port_segment:
            if port_segment == '//':
                port_segments = port_segments[0:(port_segments.index('//'))]
            else:
                port_segment_index = port_segments.index(port_segment)
                port_segment_new = (port_segment.split('//'))[0]
                port_segments = port_segments[0:port_segment_index]
                port_segments.append(port_segment_new)
            break
        elif '[' in port_segment:
            normal=r'\[\s*\d+\s*:\s*\d+\s*\]'
            un_normal_large=r'\[\s*(\S+)\s*:'

            if re.fullmatch(normal,port_segment):
                large_text=r'(\d+):'
                small_text=r':(\d+)'
                large=(re.findall(large_text,port_segment))[0]
                small=(re.findall(small_text,port_segment))[0]
            else:
                parameter=re.findall(un_normal_large,port_segment)
                if '/' in parameter[0]:
                    parameter_operand = parameter[0].split('/')
                elif '-' in parameter[0]:
                    parameter_operand = parameter[0].split('-')
                elif '+' in parameter[0]:
                    parameter_operand = parameter[0].split('+')
                elif '*' in parameter[0]:
                    parameter_operand = parameter[0].split('*')

                rest_parameter = parameter[0].split(parameter_operand[0])
                parameter_string=r'(?:parameter|localparam)\s+'+re.escape(parameter_operand[0])+r'\s*=\s*(\d+)'
                parameter_value=re.findall(parameter_string,f.read())
                large = eval(parameter_value[0]+rest_parameter[-1])
                small= '0'
            
            width = int(large)-int(small)+1
            port["width"] = width

    port["direction"] = inout
    port_name = port_segments[-1]
    if port_segments[-1] != ',':
        port_name = port_segments[-1]
    else:
        port_name = port_segments[-2]
    for character in forbidden:
        port_name = (port_name.split(character))[0]
    port["name"] = port_name
    port["type"] = "signal"
               
    return (port)   