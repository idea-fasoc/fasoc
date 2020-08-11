# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

def getIDEA_VE(design_element, options = {}) # :nodoc:
  # Checks
  de_received = defined?(design_element) ? design_element : :none
  arguments_received = defined?(options) ? options : nil
  supported_element_types = []
  valid_options = [:VE]
  design_element, element_type, error_messages = commonChecks(de_received, arguments_received, supported_element_types, valid_options)

  defaults = {:VE => "all"}
  options = defaults.merge(options) 

  ve_name = options[:VE]
  
  if ve_name.nil?
    error_messages << ":name argument missing"
  end
  if !(error_messages.empty?)
    raiseError(__method__, design_element, arguments_received, error_messages)
  end
  # Body
  ve_value = "Component: #{design_element.get("Name")}\n"
  if !(design_element.element("VendorExtensions").nil?)
    vendor_extensions = design_element.element("VendorExtensions").elements("VEElement")
    #prints general VEs
    if ve_name == "all" or ve_name == "general"
      vendor_extensions.each do |vendor_extension|
        # get the correct index for instance VEs
        for ind0 in 0..vendor_extension.elements("VEElement").length-1
          if vendor_extension.elements("VEElement")[ind0].get("VEName") == design_element.get("Name")
            # get the correct index for general VEs
            for ind1 in 0..vendor_extension.elements("VEElement")[ind0].elements("VEElement").length-1
              if vendor_extension.elements("VEElement")[ind0].elements("VEElement")[ind1].get("VEName") == "general"
                ve_ind0 = ind0
                ve_ind1 = ind1
                break
                break
              end
            end
          end
        end
        ve_value = ve_value + "\nGENERAL VEs\n\n"
        for ind2 in 0..vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement").length-1
          ve_value5 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].get("VEName")
          ve_value = ve_value + "#{ve_value5}\n"
          for ind3 in 0..vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement").length-1
            ve_name6 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement")[ind3].get("VEName")
            ve_value6 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement")[ind3].get("VEValue")
            ve_value = ve_value + "#{ve_name6} : #{ve_value6}\n"
          end
        end
      end
    end
    #prints specific VEs
    if ve_name == "all" or ve_name == "specific"
      vendor_extensions.each do |vendor_extension|
        # get the correct index for instance VEs
        for ind0 in 0..vendor_extension.elements("VEElement").length-1
          if vendor_extension.elements("VEElement")[ind0].get("VEName") == design_element.get("Name")
            # get the correct index for specific VEs
            for ind1 in 0..vendor_extension.elements("VEElement")[ind0].elements("VEElement").length-1
              if vendor_extension.elements("VEElement")[ind0].elements("VEElement")[ind1].get("VEName") == "specific"
                ve_ind0 = ind0
                ve_ind1 = ind1
                break
                break
              end
            end
          end
        end
        ve_value = ve_value + "\nSPECIFIC VEs\n\n"
        for ind2 in 0..vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement").length-1
          ve_value5 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].get("VEName")
          ve_value = ve_value + "#{ve_value5}\n"
          for ind3 in 0..vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement").length-1
            ve_name6 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement")[ind3].get("VEName")
            ve_value6 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement")[ind3].get("VEValue")
            ve_value = ve_value + "#{ve_name6} : #{ve_value6}\n"
          end
        end
      end

    #prints an individual VE (from general list)
    elsif ve_name == "power" or ve_name == "area" or ve_name == "platform" or ve_name == "vin" or ve_name == "aspect_ratio"
      ve_value = ve_value + "\nGENERAL VE\n\n"
      vendor_extensions.each do |vendor_extension|
        for ind0 in 0..vendor_extension.elements("VEElement").length-1
          if vendor_extension.elements("VEElement")[ind0].get("VEName") == design_element.get("Name")
            # get the correct index for general VEs
            for ind1 in 0..vendor_extension.elements("VEElement")[ind0].elements("VEElement").length-1
              if vendor_extension.elements("VEElement")[ind0].elements("VEElement")[ind1].get("VEName") == "general"
                ve_ind0 = ind0
                ve_ind1 = ind1
                break
                break
              end
            end
          end
        end

        for ind2 in 0..vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement").length-1
          ve_value5 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].get("VEName")
          if ve_value5 == ve_name
            ve_value = ve_value + "#{ve_value5}\n"
            for ind3 in 0..vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement").length-1
              ve_name6 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement")[ind3].get("VEName")
              ve_value6 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement")[ind3].get("VEValue")
              ve_value = ve_value + "#{ve_name6} : #{ve_value6}\n"
            end
            break
          end
        end
      end

    #prints an individual VE (from specific list)
    elsif ve_name != "all" and ve_name != "general" and ve_name != "specific"
      ve_value = ve_value + "\nSPECIFIC VE\n\n"
      vendor_extensions.each do |vendor_extension|
        for ind0 in 0..vendor_extension.elements("VEElement").length-1
          if vendor_extension.elements("VEElement")[ind0].get("VEName") == design_element.get("Name")
            # get the correct index for specific VEs
            for ind1 in 0..vendor_extension.elements("VEElement")[ind0].elements("VEElement").length-1
              if vendor_extension.elements("VEElement")[ind0].elements("VEElement")[ind1].get("VEName") == "specific"
                ve_ind0 = ind0
                ve_ind1 = ind1
                break
                break
              end
            end
          end
        end

        for ind2 in 0..vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement").length-1
          ve_value5 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].get("VEName")
          if ve_value5 == ve_name
            ve_value = ve_value + "#{ve_value5}\n"
            for ind3 in 0..vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement").length-1
              ve_name6 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement")[ind3].get("VEName")
              ve_value6 = vendor_extension.elements("VEElement")[ve_ind0].elements("VEElement")[ve_ind1].elements("VEElement")[ind2].elements("VEElement")[ind3].get("VEValue")
              ve_value = ve_value + "#{ve_name6} : #{ve_value6}\n"
            end
            break
          end
        end
      end
    end
  end

  ve_value = ve_value + "\n\n"
  return ve_value
end
