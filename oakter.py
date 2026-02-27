'''
Only ESP Oakter devices are tried and tested with this code
Currently doesnt have support for multiple Oakremotes connected together
'''

import requests
import json
import questionary

json_path = "oakter.json"

with open(json_path,"r") as o:
    content = json.load(o)
    SID = content["SID"]
    username = content["Username"]
    token = content["Token"]

def fetchSID():
    header = {
        "OS": "abc",
        "OS_Version": "0",
        "Version": "5.3", # This must be updated with time or you will get an error
        "App_Version": "0.0.0",
        "Brand": "OAKTER",
        "User": {
            "Token": token
        },
        "Username": username
    }

    login = requests.post("http://live.oakter.com:8899/OakterRestService.svc/Login", json=header)
    
    login.encoding = 'utf-8-sig'
    session_id = login.json()["LoginResult"]["SessionId"]
    return session_id

def fetch_devices():
    global SID
    SID = fetchSID()

    header = {
    "SessionId": SID,
    "Username": username,
    "OS": "abc",
    "OS_Version": "0",
    "Version": "5.3", # This must be updated with time or you will get an error
    "App_Version": "0.0.0",
    "Brand": "OAKTER",
    "User": {
        "Token": token
    }}

    post_req = requests.post("http://live.oakter.com:8899/OakterRestService.svc/RenewSession", json=header)
    post_req.encoding = 'utf-8-sig'
    post_req = post_req.json()
    statuscode = post_req["RenewSessionResult"]["StatusCode"]
    if statuscode != 0:
        print(f"Something went wrong! Status code - {statuscode}")
        exit()
    esp_devices = post_req["RenewSessionResult"]["ESPDevices"]
    devices = []
    for i in esp_devices:
        devices.append((i["ID"], i["Alias"], i["Connected"]))
    return devices

devices = fetch_devices()
for i in devices:
    print(f"Name: {i[1]}, Connected: {i[2]}")
print(f"Using the first device by default {devices[0][1]}")
OakRemoteID = devices[0][0]

def fetch_remotes(OakRemoteID=OakRemoteID):
    header = {
    "Header": {
        "SessionId": SID,
        "Username": username,
        "OS": "abc",
        "OS_Version": "0",
        "Version": "5.3", # This must be updated with time or you will get an error
        "App_Version": "0.0.0",
        "Brand": "OAKTER"
    },
    "OakRemoteId": OakRemoteID
    }
    response = requests.post("http://oakter.co:64807/api/ir/remotes/v2",json=header).json()["Response"]
    remotes = {}
    for i in response:
        cmds = {}
        for j in i["CommandList"]:
            cmds[f"{j["Name"]} ({j["Id"]})"] = j["Id"]
        remotes[f"{i["Name"]} ({i["Id"]})"] = cmds
    return remotes

def run_command(cmdID,deviceID,OakRemoteID=OakRemoteID):
    header = {
        "Header": {
        "SessionId": SID,
        "Username": username,
        "OS": "abc",
        "OS_Version": "0",
        "Version": "5.3", # This must be updated with time or you will get an error
        "App_Version": "0.0.0",
        "Brand": "OAKTER"
        },
        "OakRemoteId": OakRemoteID,
        "RemoteId": deviceID,
        "CommandId": cmdID
    }
  
    post_req = requests.post("http://oakter.co:64807/api/ir/send",json=header).json()
    print(post_req["Response"])
    if post_req["Response"] in ["Invalid SessionId for User","SessionId Missing"]:
        with open(json_path,"r+") as o:
            content = json.load(o)
            content["SID"] = fetchSID()
            o.seek(0)
            o.truncate()
            json.dump(content, o, indent=4)
        print("New SID fetched")
        run_command(cmdID,deviceID,OakRemoteID)
    elif post_req["Status"] == True:
        pass
    else:
        print(f"Response: {post_req["Response"]}")

remotes = fetch_remotes(OakRemoteID)
custom_style = questionary.Style([
    ('question', 'bold'),                # question text
    ('answer', 'fg:#00BFFF bold'),       # selected answer
    ('pointer', 'fg:#00BFFF bold'),      # the >> pointer
    ('highlighted', 'fg:#00BFFF bold'),  # highlighted choice
])

while 1:
    selected_device = questionary.select(
        "Select a device:",
        choices=list(remotes.keys()),
        qmark="⚡",
        pointer="→ ",
        style=custom_style
    ).ask()

    selected_command = questionary.select(
        "Select a command:",
        choices=list(remotes[selected_device].keys()),
        qmark="⚡",
        pointer="→ ",
        style=custom_style
    ).ask()

    deviceID = selected_device.split()[-1].strip('()')
    cmdID = selected_command.split()[-1].strip('()')
    run_command(cmdID,deviceID)
