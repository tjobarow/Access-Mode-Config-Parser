import itertools as it
import os, re, json

cur_path = os.path.dirname(__file__)

print(cur_path)

hostname = "ict-cas1-271af2-206-c"

new_path = cur_path+f'/customer_configs/{hostname}.txt'

print(new_path)

reg_int = re.compile(r"interface\s(FastEthernet|GigabitEthernet)\d{1,2}\/\d{1,2}\/\d{1,2}")
reg_acc = re.compile(r"switchport\smode\saccess")
reg_dot1x = re.compile(r"dot1x\spae\sauthenticator")
reg_open_mode = re.compile(r"authentication\sopen")

interface_dictionary = {}

with open(new_path,'r') as f:
    for key,group in it.groupby(f, lambda line: re.match(reg_int,line)):
        if key:
            last_key = key.group(0)
            interface_dictionary.update({
                                last_key: {
                                    'interface_name':last_key,
                                    'dot1x_configured':False,
                                    'dot1x_mode':None
                                }
                            })
        if not key:
            access_port=False
            dot1x_enabled=False
            open_mode=False
            for line in group:
                if re.match(reg_acc,line):
                    access_port = True
                    print(last_key+"\n"+line)
                if re.match(reg_dot1x,line) and access_port:
                    dot1x_enabled = True
                    interface_dictionary[last_key]['dot1x_configured'] = True
                if re.match(reg_open_mode,line) and access_port:
                    open_mode = True
                    interface_dictionary[last_key]['dot1x_mode'] = "open"
                if not open_mode and access_port and dot1x_enabled:
                     interface_dictionary[last_key]['dot1x_mode'] = "closed"       

with open(f"{hostname}-parsed.json","w") as f:
    json.dump(interface_dictionary,f,indent=4)

for key,value in interface_dictionary.items():
    print(json.dumps(value,indent=4))