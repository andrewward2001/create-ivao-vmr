# This script creates a VMR file from the IVAO MTL model matching library.
# Run this script from the root folder of the MTL library "Packages/Community/IVAO_MTL"
# The output file is titled "ivaomtl.vmr" and is placed in this directory.
# Script by github.com/andrewward2001

import configparser
import getopt
import os
from pathlib import Path
import sys
from collections import defaultdict

verbose = False
models_directory = "./SimObjects/Airplanes"
output_directory = Path.home() / "Documents" / "vPilot Files"
output_file = "ivaomtl.vmr"
lib = "ivao"
# excluded_types = ["A4", "B1", "B2", "BE12", "BE35", "BE36", "BE40", "BE60", "C152", "C172", "C207"]

errored_files = []
model_list_len = 0
texture_len = 0
airlines_len = 0
rules_len = 0

argsList = sys.argv[1:]
options = "d:o:vl:p:"
long_options = ['directory=', 'output=', 'verbose', 'library=', 'output-directory=']

try:
    arguments, values = getopt.getopt(argsList, options, long_options)

    for currentArgument, currentValue in arguments:
        if currentArgument in ("-d", "--directory"):
            models_directory = currentValue
            print("Reading from " + currentValue)
        elif currentArgument in ("-l", "--library"):
            if currentValue == "ivao":
                lib = "ivao"
            elif currentValue == "aig":
                lib = "aig"
                output_file = "aig.vmr"
            else:
                print("Error! Library can only be either \"ivao\" or \"aig\"")
                exit()
        elif currentArgument in ("-o", "--output"):
            output_file = currentValue
        elif currentArgument in ("-v", "--verbose"):
            verbose = True
        elif currentArgument in ("-p", "--output-directory"):
            output_directory = Path(currentValue)
    
    print("Output to: " + Path(output_directory / output_file).as_posix())
except getopt.error as err:
    print(err)

# Creates the string that will be output on each new line of the VMR to act as a Rule.
# callsign: String referring to the 3-letter ICAO identifier used in a callsign (ex. AAL, DAL, UAL, BAW, etc.)
# type: String referring to the ICAO aircraft type identifier (ex. B738, A320, B77W)
# modeltitle: String referring to which model vPilot should load. This string must match the "title" entry under [fltsim.n] in the aircraft.cfg file
def build_rule(callsign, type, modeltitle):
    # <ModelMatchRule CallsignPrefix="BAW" TypeCode="B733" ModelName="F1UT2_733.BA.BA" />
    out = "<ModelMatchRule"

    # If the callsign is blank, "def" (default), or ZZZZ, then the rule isn't associated with an airline. By leaving out the "CallsignPrefix" vPilot will only match against the aircraft type and not the callsign.
    # The if statement is written this way because I am bad at python and this is the only way I could get it to work.
    if callsign == "" or callsign == "def" or type == "ZZZZ":
        # do nothing
        out = out + ""
    else:
        out = out + " CallsignPrefix=\"" + callsign + "\""
    out = out + " TypeCode=\"" + type + "\" ModelName=\"" + modeltitle + "\" /> \n"
    return out

# Ensures that callsign entries are 3-letter airline identifiers. Otherwise, leave this blank.
def determine_callsign_prefix(entry):
    global lib
    if lib == "aig":
        try:
            return entry["icao_airline"]
        except:
            return ""
    if lib == "ivao":
        if "\"" not in entry["texture"][1:4]:
            return entry["texture"][1:4]
        else:
            return ""
        
# Depending on if we are creating a VMR from the IVAO MTL or the AIG models, the aircraft type is located at a different part of the aircraft.cfg.
def determine_aircraft_type(config, section):
    global lib
    if lib == "aig":
        for mSection in config.sections():
            try:
                if "general" in mSection:
                    return config["general"]["icao_type_designator"][1:-1]
                elif "General" in mSection:
                    return config["General"]["icao_type_designator"][1:-1]
                elif "GENERAL" in mSection:
                    return config["GENERAL"]["icao_type_designator"][1:-1]
            except:
                return ""
        return ""
    else:
        return config[section]["ui_type"][1:5]
    

# Reads all the aircraft.cfg files from the directory models_directory.
# Assemble all the aircraft.cfg entries into a dictionary with format: model_list[CallsignPrefix][TypeCode][ModelName]
def create_model_list():
    model_list = defaultdict(dict)

    for model in os.listdir(models_directory):
        global model_list_len
        model_list_len = model_list_len + 1
        file_to_read = models_directory + "/" + model + "/aircraft.cfg"
        config = configparser.ConfigParser()
        try:
            if verbose: print("Reading " + file_to_read + "...")
            config.read(file_to_read)
        except configparser.ParsingError as err:
            print(err)
            errored_files.append(file_to_read)
            pass
        except UnicodeDecodeError as err:
            # print (err)
            errored_files.append(file_to_read)
            pass
        for section in config.sections():
            if "fltsim" in section:
                global texture_len
                texture_len = texture_len + 1
                acf_type = determine_aircraft_type(config, section)

                # TypeCode cannot be blank.
                if acf_type == "":
                    print(acf_type)
                    print(file_to_read + " was malformed, skipping.")
                    errored_files.append(file_to_read)
                    continue

                texture_title = config[section]["title"]
                if "\"" in texture_title: texture_title = texture_title[1:-1].encode('utf-8')
                global lib
                if lib == "ivao": texture_title = texture_title.decode('utf-8')
                try:
                    model_list[determine_callsign_prefix(config[section])][acf_type].append(texture_title)
                except:
                    model_list[determine_callsign_prefix(config[section])][acf_type] = [texture_title]

    return model_list

# Goes through the models_list and writes the rules to the output file.
# Some airlines have multiple available textures for a single type. These are combined into one entry and the ModelNames are separated with "//"
def write_rules(model_list, output):
    for airline in model_list:
        global airlines_len
        airlines_len = airlines_len + 1

        for type in model_list[airline]:
            variant_string = ""
            for variant in model_list[airline][type]:
                if "&" in variant: continue
                variant_string += variant
                if variant != model_list[airline][type][-1]:
                    variant_string += "//"
            
            if(type.endswith("\"")):
                type = type[:-1]
            output.write(build_rule(airline, type, variant_string))
            if verbose: print("Created rule for airline " + airline + " type " + type)
            global rules_len
            rules_len = rules_len + 1

print("Building VMR for library: " + lib)
output = open(output_directory / output_file, "w")
output.write("<?xml version=\"1.0\" encoding=\"utf-8\"?> \n")
output.write("<ModelMatchRuleSet> \n")
write_rules(create_model_list(), output)
output.write("</ModelMatchRuleSet> \n")
output.write("<!-- VMR created by create-ivao-vmr https://github.com/andrewward2001/create-ivao-vmr -->")
output.close()
print("\n\nDone!")
print("Processed: " + str(model_list_len) + " models.")
print("Processed: " + str(texture_len) + " textures.")
print("Processed: " + str(airlines_len) + " airlines.")
print("Processed: " + str(rules_len) + " rules.")
print("VMR created: " + output_file)
if(len(errored_files) != 0):
    print("\n\nSome files had errors and were not included in the VMR:")
    for file in errored_files:
        print(file)
    print("Usually this is because of an error where the file says [VERSION]. See GitHub for more details.")
    print("The VMR was still created but aircraft of this type will not show up unless the problem is fixed and the script is run again.")