#!/usr/bin/env python3
import subprocess
import optparse
import re
import random

options = None

def gen_rand_addr():
  output = hex(random.randrange(0, 0x10))[2] + "26ae"[random.randrange(0,4)]
  for i in range(5):
    output += ":" + (hex(random.randrange(0, 0x100)) + "00")[2:4]
  return output

def get_orig_addr(interface):
  ethtool_result = subprocess.check_output(["ethtool", "-P", interface])
  mac_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ethtool_result))
  if mac_result:
    return mac_result.group(0)
  else:
    print("[-] Could not read original MAC result.")

def parse_args():
  parser = optparse.OptionParser(
    """
    This software is provided \"AS IS\", without warranty of any kind.\n
    'mac_changer' is a tool used to change your (Media Access Control) address.
    This can be helpful for staying anonymous, impersonating other
    devices, or bypassing filters.

    run with: '{Python Path} mac_changer.py [options]'
    Required flags: --interface and address specification (-a, -r, or -p)\n\n
    Tool created by: Elgin Ciani
    """,
    version="%prog 2.6")

  #Available command line arguments
  parser.add_option("-i", "--interface", dest="interface", help="Interface to change MAC address. e.g: eth0, wlan0")
  parser.add_option("-a", "--address", dest="address", help="New MAC address in the form 11:22:33:44:55:66")
  parser.add_option("-r", "--random", action="store_true", default=False, help="Generates a random new hexadecimal MAC address.")
  parser.add_option("-R", "--restore-permanent-address", dest="restore", action="store_true", default=False, help="Restores original MAC address for given interface.")
  parser.add_option("-P", "--print-permanent-address", dest="printorig", action="store_true", default=False, help="Prints original MAC address for given interface.")
  parser.add_option("-p", "--print-current-address", dest="printcurr", action="store_true", default=False, help="Prints current MAC address for given interface.")
  parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Print ifconfig info for given interface before and after changing address.")
  parser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=False, help="Enable this flag to turn off any print logging.")
  
  global options
  (options, arguments) = parser.parse_args()

  #Throw error if user does not specify required parameters
  if not options.interface:
    parser.error("[-] Please specify an interface. See --help for more info.")
  elif not options.address and not options.random and not options.restore and not options.printorig and not options.printcurr:
    parser.error("[-] Specify a new mac address (or use --random or -p). See --help for more info.")
  elif options.address and (options.random or options.restore):
    parser.error("[-] Do not specify address and set -r or -p flags simultaneously.")
  elif options.random and options.restore:
    parser.error("[-] Do not set -r and -R flags simultaneously.")
  elif options.quiet and options.verbose:
    parser.error("[-] Do not set --quiet and --verbose flags simultaneously.")
  ## End: Error scenarios ##
  elif options.printcurr:
    currmac = get_curr_mac(options.interface)
    print("Current MAC address:", currmac)
    exit()
  elif options.printorig:
    origmac = get_orig_addr(options.interface)
    print("Permanent MAC address:", origmac)
    exit()
  elif not options.address and not options.restore and options.random: #Random MAC in place of specified address
    options.address = gen_rand_addr()
  elif not options.address and not options.random and options.restore: #Restore original MAC address
    options.address = get_orig_addr(options.interface)
  return options

def change_mac(interface, newmac):
  if not options.quiet:
    print("[+] Changing MAC address for", interface, "to", newmac)
  subprocess.call(["ifconfig", interface, "down"])
  subprocess.call(["ifconfig", interface, "hw", "ether", newmac])
  subprocess.call(["ifconfig", interface, "up"])

def print_info(interface):
  subprocess.call(["ifconfig", options.interface])

def get_curr_mac(interface):
  ifconfig_result = subprocess.check_output(["ifconfig", options.interface])
  mac_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig_result))
  if mac_result:
    return mac_result.group(0)
  else:
    print("[-] Could not read MAC result.")


########## MAIN ##########
options = parse_args() #Option parser

currmac = get_curr_mac(options.interface)

if not options.quiet and not options.verbose:
  print("Current MAC = " + str(currmac))

if options.verbose:
  print("*"*20, "Before Update Info", "*"*20)
  print()
  print_info(options.interface)

change_mac(options.interface, options.address) #Change mac address
currmac = get_curr_mac(options.interface) #Update current mac address

if options.verbose:
  print("*"*20, "After Update Info", "*"*20)
  print()
  print_info(options.interface)

if not options.quiet:
  if currmac == options.address:
    print("[+] MAC address changed successfully.")
  else:
    print("[-] MAC address change failed.")
########## END MAIN ##########
