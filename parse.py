import itertools as it
import os, re, json, glob

def parseAllConf():
    #Define Regular Expressions
    reg_int = re.compile(r"interface\s(FastEthernet|GigabitEthernet)\d{1,2}\/\d{1,2}\/\d{1,2}")
    reg_acc = re.compile(r"switchport\smode\saccess")
    reg_dot1x = re.compile(r"dot1x\spae\sauthenticator")
    reg_open_mode = re.compile(r"authentication\sopen")

    #Define Interface Dictionary
    interface_dictionary = {}

    #Define the Current Path and the Sub-directory containing configs
    cur_path = os.path.dirname(__file__)+"/customer_configs/"

    for txt_file in glob.glob(os.path.join(cur_path,'*.txt')):
        #Filename will eventually be used in saving the output. 
        filename = txt_file

        #Open the text file as read only using "with open" so file auto-closes
        with open(txt_file,'r') as f:
            #####################
            # The KEY will be matched against reg_int regular expression, checking for phrase 'interface FastEthernet/GigabitEthernetX/Y/Z
            # Using a lambda function which returns a match obj if the line matches reg_int regex.
            # Lambda returns into groupby() itertools function, which will group items into group obj using the delimiter returned from the lambda fnc.
            #####################
            for key,group in it.groupby(f, lambda line: re.match(reg_int,line)):
                # If the key is defined (has a match against reg_int regex)
                if key:
                    #We get the phrase that was matched from the match obj
                    # For example, this will return "interface GigabitEthernet1/0/1"
                    # If in future iterations we learn this interface is set to access mode, we will need the interface name, so we save it for later use. 
                    last_key = key.group(0)
                #If the "key" is not defined
                if not key:
                    #We are assuming these are false unless we learn they are true
                    access_port=False
                    dot1x_enabled=False
                    open_mode=False
                    #For each line in the group generated by groupby()
                    for line in group:
                        #If it matches an access switchport
                        if re.match(reg_acc,line):
                            #Set access port to true
                            access_port = True
                            # Add the interface to the interface_dictionary.
                            # We add this at this point in the script because we only want to find access switchports
                            # Whether they are dot1x enabled will be determined soon
                            interface_dictionary.update({
                                last_key: {
                                    'interface_name':last_key,
                                    'dot1x_configured':False,
                                    'dot1x_mode':None
                                }
                            })
                            print(last_key+"\n"+line)
                        #If we previously confirmed this is an access switchport, and we find that "dot1x pae authenticator" exists on the interface
                        if re.match(reg_dot1x,line) and access_port:
                            #Set dot1x enabled to true
                            dot1x_enabled = True
                            #Update the dictionary to set dot1x enabled to True
                            interface_dictionary[last_key]['dot1x_configured'] = True
                        # If we see the command "authentication open" via the reg_open_mode command, and its an access switchport
                        if re.match(reg_open_mode,line) and access_port:
                            # Set open mode to true
                            open_mode = True
                            # set the dot1x mode to open in the dictionary
                            interface_dictionary[last_key]['dot1x_mode'] = "open"
                        #If open mode is was not found, and the interface is an access switchport and dot1x is enabled
                        # Set dot1x mode to closed. 
                        if not open_mode and access_port and dot1x_enabled:
                            interface_dictionary[last_key]['dot1x_mode'] = "closed"       

        # Use json.dump() to format the dictionary as a JSON, and write it to a JSON file. 
        with open(f"{filename}-parsed.json","w") as f:
            json.dump(interface_dictionary,f,indent=4)
        
        #Empty the dictionary because it will get all new data from the next text file. 
        interface_dictionary.clear()

if __name__ == "__main__":
    parseAllConf()