# -*- coding:utf-8 -*-
#!/usr/bin/python

import sys
import time
import re
import thread
import serial

MODULE = '[UART]'

class Uart():

	def __init__(self, log, name, recv_hook, status_change_hook):
		self.log = log
		self.log.write('%s init uart for %s', MODULE, name)

		self.name = name

		self.uart_handle = serial.Serial()
		self.recv_hook = recv_hook
		self.status_chagne_hook = status_change_hook

		self.connected = False

		# self.uart_check_thread = thread.start_new_thread(self.uart_check, (None, ))
		self.uart_recv_thread = thread.start_new_thread(self.auto_recv, (None, ))

	def __exit__(self):
		self.uart_handle.close()

	def open(self, port, baudrate, bytesize, parity, stopbits, timeout):
		# pattern = re.compile(r'^COM\d')
		# pattern.search(port)

		if self.uart_handle.isOpen():
			self.uart_handle.close()

		self.log.write('%s open uart port %s: %d, %d, %s, %d, readtimeout %d sec',
					   MODULE, port, baudrate, bytesize, parity, stopbits, timeout)
		self.uart_handle.port = port
		self.uart_handle.baudrate = baudrate
		self.uart_handle.bytesize = bytesize
		self.uart_handle.parity = parity
		self.uart_handle.stopbits = stopbits
		# self.uart_handle.timeout = timeout

		try:
			self.uart_handle.open()
			time.sleep(0.1)
		except:
			self.log.write('%s can not open uart port %s', MODULE, port)
			self.status_chagne_hook(self.name, 'DISCONNECT')
			self.connected = False
			return

		# self.uart_handle.flushInput()
		self.uart_handle.flushOutput()
		self.log.write('%s open uart port %s: OK', MODULE, port)
		self.status_chagne_hook(self.name, 'CONNECT')
		self.connected = True

	def close(self):
		if self.uart_handle.isOpen():
			self.uart_handle.close()
			self.log.write('%s close uart port %s: OK', MODULE, self.uart_handle.port)
			self.status_chagne_hook(self.name, 'DISCONNECT')
			self.connected = False

	def auto_recv(self, x):
		while True:

			# print self.uart_handle.isOpen()
			if self.uart_handle.isOpen():
				try:
					data = self.uart_handle.readline()
					# print 'get data<' + data + '>'
					# print len(data)
					if data:
						self.recv_hook(data)
				except:
					pass

	def send(self, data):
		if self.uart_handle.isOpen():
			# self.uart_handle.writelines(data)
			# print 'send data<' + data + '>'
			# print len(data)
			# self.uart_handle.write(data)
			try:
				self.uart_handle.writelines(data)
			except:
				pass
		else:
			return False

	def uart_check(self, x):
		while True:
			# if self.connected and (not self.uart_handle.isOpen()):
			# 	self.status_chagne_hook(self.name, 'DISCONNECT')

			if self.connected:
				try:
					self.uart_handle.writelines('AT+ALIVE\n')
				except:
					self.status_chagne_hook(self.name, 'DISCONNECT')
					self.connected = False

			try:
				time.sleep(1)
			except:
				pass



if __name__ == '__main__':
	pass



