__author__ = 'Kasper Fast'

import requests
import json
import socket
import sys


def printUsage():
    print "Usage:"+" (1)<API ip or host>"+" (2)<new object name>"+" (3)<username for API>"+" (4)<password for API>"
    exit(1)


def checkArgs():

    allowedArgs = 5
    argLength = len(sys.argv)

    if argLength > allowedArgs or argLength < allowedArgs:
        printUsage()

checkArgs()


# remote OP5 API stuff: ip, user and pass
uriHost = socket.gethostbyname(sys.argv[1])
username = sys.argv[3]
password = sys.argv[4]
hostName = sys.argv[2]


# check if the host object already exists
def ifAlreadyExists():

    getHostName = requests.get("https://"+uriHost+"/api/status/host?name="+hostName,
                               auth=(username, password), verify=False)

    jsonFormat = getHostName.json()

    if jsonFormat:
        print "host object " + hostName + " already exists, exiting..."
        exit(1)

ifAlreadyExists()

# variable for hostData object
ipAddress = "127.0.0.1"  # host object IP addr
hostGroups = "HS-Prod-Service" # which hostgroup should the new host belong in
hostData = {
    "host_name": hostName,
    "alias": hostName,
    "address": ipAddress,
    "hostgroups": hostGroups,
    "parents": "monitor",
    "template": "default-host-template",
    "register": "1",
    "file_id": "etc/hosts.cfg",
    "check_command": "check-host-alive",
    "max_check_attempts": "3"
}  # json data for the host object


# variables used in serviceData object
hostAlias = ""  # not required
checkCMD = "check_nrpe"

# below objects only works for "check_nrpe"
cmdArgsDesc = {
    "root_disk": "Disk Usage /",
    "check_varlv": "Disk Usage /var",
    "check_homelv": "Disk Usage /home",
    "check_arenalv": "Disk Usage /arena",
    "check_pages_in": "Check Swapping In Pages",
    "check_pages_out": "Check Swapping Out Pages",
    "check_ucpool": "Arena Connection Errors",
    "check_last_puppetrun": "last puppetrun",
    "check_linux_mem": "memory",
    "swap": "Swap Usage",
    "load": "load",
    "check_zombie_procs": "Zombie processes",

}  # add new nagios entries here, item = check_args, key = service description

cmdCustomArgs = {
    "PING": ["check_ping", "100,20%!500,60%"],
    "IF 2_ eno16777984 Traffic": ["check_snmpif_traffic_v2", "'axiell'!2!10000mbit!70!90"],
    "IF 2_ eno16777984 Status": ["check_snmpif_status_v2", "'axiell'!2!c"],
    "IF 2_ eno16777984 Errors": ["check_snmpif_errors_v2", "'axiell'!2!1.5!2.5"],
    "SSH Server": ["check_ssh", "5"],
}


def postServiceObjects(svc):

    dump = svc
    requests.post("https://"+uriHost+"/api/config/service/", data=json.dumps(dump),
                  auth=(username, password), headers={'content-type': 'application/json'}, verify=False)


def createServiceObject(args):

    objectSplit = args.items()

    # below is checks that hosting don't want to get
    arenaChecks = ['check_ucpool', 'check_pages_in', 'check_pages_out']

    hostingCon = ["AddPro", "hosting-services-prod"]  # contact groups for hosting services
    contactGroups = None

    for checkArgs, checkDesc in objectSplit:

        for i in arenaChecks:
            if checkArgs != i:
                contactGroups = hostingCon
            else:
                contactGroups = ""
                break

        # json data for the service object
        serviceData = {
            "host_name": hostName,
            "service_description": checkDesc,
            "check_command": "check_nrpe",
            "check_command_args": checkArgs,
            "template": "default-service",
            "check_interval": "5",
            "file_id": "etc/services.cfg",
            "retry_interval": "1",
            "max_check_attempts": "3",
            "servicegroups": ["Arena Application - Services", "HS Services Prod"],
            "contact_groups": contactGroups,
        }

        # jsonData = json.dumps(serviceData)
        # print jsonData

        postServiceObjects(serviceData)


def createCustomServiceObject(args):

    hostingCon = ["AddPro", "hosting-services-prod"]  # contact groups for hosting services

    for checkDesc, checkName in args.iteritems():
        checkCmd = checkName[0]
        checkArgs = checkName[1]

        # json data for the service object
        serviceData = {
            "host_name": hostName,
            "service_description": checkDesc,
            "check_command": checkCmd,
            "check_command_args": checkArgs,
            "template": "default-service",
            "check_interval": "5",
            "file_id": "etc/services.cfg",
            "retry_interval": "1",
            "max_check_attempts": "3",
            "servicegroups": ["Arena Application - Services", "HS Services Prod"],
            "contact_groups": hostingCon,
        }

        # jsondump = json.dumps(serviceData)
        # print jsondump

        postServiceObjects(serviceData)


def createHostObject(newhost):

    requests.post("https://"+uriHost+"/api/config/host/", data=json.dumps(newhost),
                  auth=(username, password), headers={'content-type': 'application/json'}, verify=False)
    # print host.text


def saveAllChanges():

    requests.post("https://"+uriHost+"/api/config/change", auth=(username, password),
                  headers={'content-type': 'application/json'}, verify=False)

    # print saveChanges.text


createHostObject(hostData)  # create host object, this won't create any check services

createServiceObject(cmdArgsDesc)  # create all service checks for the host

createCustomServiceObject(cmdCustomArgs)

saveAllChanges()  # finally, save all of the changes
