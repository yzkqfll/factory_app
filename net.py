# -*- coding:utf-8 -*-
#!/usr/bin/python

import sys
import time
import re
import thread
import serial
import ftplib
import os
import socket

MODULE = '[NET]'

REMOTE_IP = '120.26.199.188'

contry = {
	'Turkey': 0,
	'Djibouti': 1,
	'Korea': 2,
	'Latvia': 5,
	'Vietnam': 8,
}

class Net():
	def __init__(self, log):
		self.log = log
		self.ftp = ftplib.FTP()

	def __exit__(self):
		pass

	def del_file(self, name):
		try:
			os.remove(name)
		except:
			pass

	def ftp_get_err_percent(self, name):
		try:
			self.ftp.connect(REMOTE_IP, 21)
			self.ftp.login('fac', 'fac')

			f = open(name,'w')
			self.ftp.retrbinary('RETR ' + name, f.write)
			f.close()
			self.ftp.quit()

			f = open(name,'r+')
			f.seek(0, 0)
			buf = f.read()
			buf = buf.strip()
			val = contry[buf]
			f.close()
			self.del_file(name)

			print 'remote err percent is ' + str(val)
			return val

		except:
			self.del_file(name)
			return -1

	def send_udp_to_server(self, server, port, data):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		to = (server, port)

		try:
			sock.sendto(data, to)
		except:
			pass
		finally:
			sock.close()

