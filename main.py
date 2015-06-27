# -*- coding:utf-8 -*-
#!/usr/bin/python

import time

import ui
import log
import uart
import config

MODULE = '[ibaby]'

class Ibaby:

	def __init__(self):
		# LOG
		self.log = log.Log()

		# UI
		self.ui = ui.Ui(self.log, self.get_data_from_ui)
		if self.ui.is_window_ok() == False:
			try:
				time.sleep(0.1)
			except:
				pass
		try:
			time.sleep(0.1)
		except:
			pass

		# Config
		self.sys_config = config.Config(self.log)
		self.uart_dut_port = self.sys_config.get('uart_dut_port')
		self.uart_std_port = self.sys_config.get('uart_std_port')

		# UART
		self.uart_dut = uart.Uart(self.log, 'dut', self.uart_dut_recv, self.uart_status_change)
		# self.uart_std = uart.Uart(self.log, 'std', self.uart_std_recv, self.uart_status_change)

	def start(self):
		self.ui.update_ui('uart_dut_port', self.uart_dut_port)
		# self.ui.update_ui('uart_std_port', self.uart_std_port)

		if self.uart_dut_port:
			self.uart_dut.open(self.uart_dut_port, 115200, 8, 'N', 1)
		# if self.uart_std_port:
		# 	self.uart_std.open(self.uart_std_port, 115200, 8, 'N', 1)

	def uart_status_change(self, type, status):
		if status == 'open_ok':
			data = '连接'
		elif status == 'open_fail':
			data = '断开'
		elif status == 'close_ok':
			data = '断开'

		self.ui.update_ui('uart_' + type + '_status', data)

	# get data from DUT UART
	def uart_dut_recv(self, data):
		# show it in UI
		# print ">>>" + data,
		self.ui.ui_append_dialog('board', data)
		pass

	# get data from STD UART, handle it
	def uart_std_recv(self, data):
		pass

	def get_data_from_ui(self, type, data):
		if type == 'send_to_dut':
			self.uart_dut.send(data)

		elif type == 'uart_dut_port_connect':
			self.uart_dut_port = data
			self.sys_config.set('uart_dut_port', self.uart_dut_port)

			self.uart_dut.open(self.uart_dut_port, 115200, 8, 'N', 1)

		elif type == 'uart_dut_port_disconnect':
			self.uart_dut_port = data
			self.uart_dut.close()

		elif type == 'zero_calibration':
			pass
		elif type == 'low_temp_calibration':
			pass
		elif type == 'high_temp_calibration':
			pass
		else:
			print 'unknown type' + type

	def run(self):
		try:
			while True:			
				time.sleep(0.5)
				if not self.ui.is_window_ok():
					self.log.write('%s ui closed\n', MODULE)
					break						
		except:
			pass
			
		self.ui.exit()
		
if __name__ == '__main__':
	ibaby = Ibaby()
	ibaby.start()
	ibaby.run()
		
	
	
	
