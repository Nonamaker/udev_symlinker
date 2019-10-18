#!/usr/bin/python3
#
#  register_device.py
#
#  Adds a SymLink as specified by caller to a new device
#    Returns True on success, False otherwise
#
#############################################
import os
import re
import sys
import time
import subprocess

def abort(message="ERROR"):
	print('''{}\n{}'''.format(message, "Aborting..."))
	sys.exit()

def add_device(name):
	input('''Ensure the {} is NOT connected to any serial port.'''.format(name))
	rule_file = "/etc/udev/rules.d/99-usb-serial.rules"
	try:
		rule_fh = open(rule_file, "a+") # TODO Ensure file was opened/created
	except:
		abort('''Could not open file: {}'''.format(rule_file))

	try:
		old_lsusb = subprocess.check_output(['''sudo lsusb'''], shell=True).decode().split("\n")
		del old_lsusb[-1]
	except:
		print("Not working")
		old_lsusb = []
	### Create list of existing idProduct, idVendor, iSerial
	try:
		iSerial = subprocess.check_output(['''sudo lsusb -v | grep iSerial | grep "[A-Z0-9]\{8\}" '''], shell=True).decode().split("\n")
	except:
		iSerial = []
	try:
		idProduct = subprocess.check_output(['''sudo lsusb -v | grep idProduct | grep "0x[a-z0-9]\{4\}" '''], shell=True).decode().split("\n")
	except:
		idProduct = []
	try:
		idVendor = subprocess.check_output(['''sudo lsusb -v | grep idVendor | grep "0x[a-z0-9]\{4\}" '''], shell=True).decode().split("\n")
	except:
		idVendor = []
	
	old_iSerial, old_idProduct, old_idVendor = [], [], []
	
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
	
	input('''Connect the {} now.'''.format(name))
	
	try:
		iSerial = subprocess.check_output(['''sudo lsusb -v | grep iSerial | grep "[A-Z0-9]\{8\}" '''], shell=True).decode().split("\n")
	except:
		iSerial = []
	try:
		idProduct = subprocess.check_output(['''sudo lsusb -v | grep idProduct | grep "0x[a-z0-9]\{4\}" '''], shell=True).decode().split("\n")
	except:
		idProduct = []
	try:
		idVendor = subprocess.check_output(['''sudo lsusb -v | grep idVendor | grep "0x[a-z0-9]\{4\}" '''], shell=True).decode().split("\n")
	except:
		idVendor = []
	
	all_iSerial, all_idProduct, all_idVendor = [], [], []
	
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
	
	new_iSerial, new_idProduct, new_idVendor = None, None, None
	
	for value in all_iSerial:
		if value not in old_iSerial:
			new_iSerial = value
	for value in all_idProduct:
		if value not in old_idProduct:
			new_idProduct = value
	for value in all_idVendor:
		if value not in old_idVendor:
			new_idVendor = value
	#####     Manual Selection     #####	
	if (
	  new_iSerial is None
	  or new_idProduct is None
	  or new_idVendor is None
	):
		print("Could not detect new device information.")
		manual_select = None
		while True:
			manual_select = input("Would you like to select a device manually? [Y,N]\n").lower()
			if 'y' in manual_select or 'n' in manual_select:
				break
		if manual_select == "n":
			abort("User terminated process")
		else:
			print('''-----\nOld devices:\n''')
			for i, device in enumerate(old_lsusb):
				print('''{}'''.format(device))
			try:
				new_lsusb = subprocess.check_output(['''sudo lsusb'''], shell=True).decode().split("\n")
				del new_lsusb[-1]	
			except:
				new_lsusb = []
			print('''-----\nNew devices:\n''')
			for i, device in enumerate(new_lsusb):
				print('''[{}]:  {}'''.format(i, device))
			selection = None
			while True:
				selection = input("Enter number of device to add.\n")
				if selection.isdigit():
					selection = int(selection)
					if selection <= len(new_lsusb) - 1:
						break
			try:
				devices = subprocess.check_output(['''sudo lsusb -v'''], shell=True).decode().split("\n\n")
			except:
				abort("Could not read output of lsusb -v")
			try:
				new_idVendor = re.search(r'idVendor.*0x(\w{4}).*\n',devices[selection]).group(1)
			except:
				print("ALERT -- No idVendor found!")
				new_idVendor = None
			try:
				new_idProduct = re.search(r'idProduct.*0x(\w{4}).*?\n',devices[selection]).group(1)
			except:
				print("ALERT -- No idProduct found!")
				new_idProduct = None
			try:
				new_iSerial = re.search(r'iSerial.*(\w{8}).*\n',devices[selection]).group(1)
			except:
				print("ALERT -- No iSerial found!")
				new_iSerial = None
			print('''The device info:\n  idVendor  :: {}\n  idProduct :: {}\n  iSerial   :: {}'''.format(new_idVendor, new_idProduct, new_iSerial))

			if new_idVendor == "" or new_idProduct == "" or new_iSerial == "":
				print('''ALERT -- This device lacks a unique identifier. Adding it may cause conflicts with existing or future devices!''')
				while True:
					selection = input("Are you sure you want to add this device? [Y,N]\n").lower()
					if 'y' in selection or 'n' in selection:
						break
				if selection == "n":
					abort("User terminated process")
			# Build abbreviated UDEV rule
			rule = '''\nSUBSYSTEM=="tty"'''
			if new_idVendor is not None:
				rule = '''{}, ATTRS{{idVendor}}=="{}"'''.format(rule, new_idVendor)
			if new_idProduct is not None:
				rule = '''{}, ATTRS{{idProduct}}=="{}"'''.format(rule, new_idProduct)
			if new_iSerial is not None:
				rule = '''{}, ATTRS{{serial}}=="{}"'''.format(rule, new_iSerial)
			rule = '''{}, SYMLINK+="{}"'''.format(rule, name)

	else:	
		rule = '''\nSUBSYSTEM=="tty", ATTRS{{idVendor}}=="{}", ATTRS{{idProduct}}=="{}", ATTRS{{serial}}=="{}", SYMLINK+="{}"'''.format(new_idVendor, new_idProduct, new_iSerial, name)
	print(rule)
	
	if rule not in rule_fh.read():
		rule_fh.write(rule)
		rule_fh.close()
		os.system("sudo udevadm control --reload-rules")
		os.system("sudo udevadm trigger")
		print('''Added Agilent to USb rules'''.format(name))
	else:
		rule_fh.close()
		print('''This {} device already exists'''.format(name))
