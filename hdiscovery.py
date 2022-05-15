#!/usr/bin/env python3

### Author: Bryan Muñoz aka s4rgaz 

import threading
from queue import Queue
from colorama import init,Fore
from ipaddress import IPv4Network
from scapy.all import *
import logging
import signal
import argparse

# Define command line arguments
parser = argparse.ArgumentParser(description="Host Discovery")
parser.add_argument("-r", metavar="RANGE", required=True, help="Exm: 192.168.1.0/24")
parser.add_argument("-t", metavar="THREADS", type=int, default=20, help="Def: 20")
args=parser.parse_args()

ip = args.r
n_threads = args.t

net = IPv4Network(ip)

# Set colors to variables
init()
green = Fore.GREEN
yellow = Fore.YELLOW
reset = Fore.RESET


hosts = []

print_lock = threading.Lock()
q = Queue()

# Avoid scapy errors
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# Define the print color function 
def setColor(a):
    print(f"{green}{a:15}{reset} =>{yellow} up{reset}")


# Set signal handling to ctrl+c
def handler(signum, frame):
    print(end='\r')
    res = input("Do you really want to exit? [y/n] ")
    if res == 'y':
        exit(1)
 
signal.signal(signal.SIGINT, handler)


# Define the function to perform a ping scan
def pingScan(host):
    ans = sr1(IP(dst=str(host))/ICMP(), timeout=2, verbose=0)

    if ans:
        with print_lock:
            if ans.src not in hosts:
                hosts.append(ans.src)
                setColor(ans.src)


def threader():
    while True:
        worker = q.get()
        pingScan(worker)
        q.task_done()


for w in range(n_threads):
    t = threading.Thread(target=threader, daemon=True)
    t.start()


for addr in net.hosts():
    q.put(addr)

q.join()
    
