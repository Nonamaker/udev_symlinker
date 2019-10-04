#!/usr/bin/python
#
#  register_device.py
#
#  Adds a SymLink as specified by caller to a new device
#
# ############################################
import os
import re
import sys
import time
import subprocess

def add_device(name):
	raw_input('''Ensure the Agilent is NOT connected to any serial port.''')
	rule_file = "/etc/udev/rules.d/99-usb-serial.rules"
	rule_fh = open(rule_file, "a+")

	### Create list of existing idProduct, idVendor, iSerial
	try:
		iSerial = subprocess.check_output(['''sudo lsusb -v | grep iSerial | grep "[A-Z0-9]\{8\}" '''], shell=True).split("\n")
	except:
		iSerial = []
	try:
		idProduct = subprocess.check_output(['''sudo lsusb -v | grep idProduct | grep "0x[a-z0-9]\{4\}" '''], shell=True).split("\n")
	except:
		idProduct = []
	try:
		idVendor = subprocess.check_output(['''sudo lsusb -v | grep idVendor | grep "0x[a-z0-9]\{4\}" '''], shell=True).split("\n")
	except:
		idVendor = []
	
	old_iSerial = []
	old_idProduct = []
	old_idVendor = []
	
	for i, value in enumerate(iSerial):
		try:
			old_iSerial.append(re.search(r'(\w{8})',value).group(1))
		except:
			continue	
	for i, value in enumerate(idProduct):
		try:
			old_idProduct.append(re.search(r'0x(\w{4})',value).group(1))
		except:
			continue
	
	for i, value in enumerate(idVendor):
		try:
			old_idVendor.append(re.search(r'0x(\w{4})',value).group(1))
		except:
			continue
	
	raw_input('''Connect the Agilent now.''')
	
	try:
		iSerial = subprocess.check_output(['''sudo lsusb -v | grep iSerial | grep "[A-Z0-9]\{8\}" '''], shell=True).split("\n")
	except:
		iSerial = []
	try:
		idProduct = subprocess.check_output(['''sudo lsusb -v | grep idProduct | grep "0x[a-z0-9]\{4\}" '''], shell=True).split("\n")
	except:
		idProduct = []
	try:
		idVendor = subprocess.check_output(['''sudo lsusb -v | grep idVendor | grep "0x[a-z0-9]\{4\}" '''], shell=True).split("\n")
	except:
		idVendor = []
	
	all_iSerial = []
	all_idProduct = []
	all_idVendor = []
	
	for i, value in enumerate(iSerial):
		try:
			all_iSerial.append(re.search(r'(\w{8})',value).group(1))
		except:
			continue	
	for i, value in enumerate(idProduct):
		try:
			all_idProduct.append(re.search(r'0x(\w{4})',value).group(1))
		except:
			continue
	for i, value in enumerate(idVendor):
		try:
			all_idVendor.append(re.search(r'0x(\w{4})',value).group(1))
		except:
			continue
	
	new_iSerial, new_idProduct, new_idVendor = "","",""
	
	for value in all_iSerial:
		if value not in old_iSerial:
			new_iSerial = value
	for value in all_idProduct:
		if value not in old_idProduct:
			new_idProduct = value
	for value in all_idVendor:
		if value not in old_idVendor:
			new_idVendor = value
	
	if new_iSerial == "" or new_idProduct == "" or new_idVendor == "":
		print("No new device was connected.\nAborting...")
		sys.exit()
	
	rule = '''SUBSYSTEM=="tty", ATTRS{{idVendor}}=="{}", ATTRS{{idProduct}}=="{}", ATTRS{{serial}}=="{}", SYMLINK+="{}"'''.format(new_idVendor, new_idProduct, new_iSerial, name)
	print(rule)
	
	if rule not in rule_fh.read():
		rule_fh.write(rule)
		rule_fh.close()
		os.system("sudo udevadm control --reload-rules")
		os.system("sudo udevadm trigger")
		print("Added Agilent to USb rules")
	else:
		rule_fh.close()
		print("This Agilent device already exists")			
