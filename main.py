# -*- coding:utf-8 -*-
#!/usr/bin/python

import time

import ui
import log
import uart
import config
import cal

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
		if not self.sys_config.get('uart_dut_port'):
			self.sys_config.set('uart_dut_port', 'com?')
		if not self.sys_config.get('uart_std_port'):
			self.sys_config.set('uart_std_port', 'com?')
		self.uart_dut_port = self.sys_config.get('uart_dut_port')
		self.uart_std_port = self.sys_config.get('uart_std_port')

		# UART
		self.uart_dut = uart.Uart(self.log, 'dut', self.uart_dut_recv, self.uart_status_change)
		self.uart_dut_hijack = False
		# self.uart_std = uart.Uart(self.log, 'std', self.uart_std_recv, self.uart_status_change)

		# Calibration
		self.cal = cal.Cal(self.log, self.uart_dut, self.ui)

	def start(self):
		self.ui.update_ui('uart_dut_port', self.uart_dut_port, None)
		# self.ui.update_ui('uart_std_port', self.uart_std_port, None)

		if self.uart_dut_port:
			self.uart_dut.open(self.uart_dut_port, 115200, 8, 'N', 1, timeout=1)
		# if self.uart_std_port:
		# 	self.uart_std.open(self.uart_std_port, 115200, 8, 'N', 1)

	def uart_status_change(self, type, status):
		self.ui.update_ui('uart_' + type + '_status', status, None)

	# get data from DUT UART
	def uart_dut_recv(self, data):
		# show it in UI
		# print ">>>" + data,
		self.ui.ui_append_dialog('board', data)
		if self.uart_dut_hijack:
			self.cal.get_dut_resp(data)

	# get data from STD UART, handle it
	def uart_std_recv(self, data):
		pass

	def get_data_from_ui(self, type, data):
		if type == 'send_to_dut':
			self.uart_dut.send(data)

		elif type == 'uart_dut_port_connect':
			self.uart_dut_port = data
			self.sys_config.set('uart_dut_port', self.uart_dut_port)

			self.uart_dut.open(self.uart_dut_port, 115200, 8, 'N', 1, timeout = 1)

		elif type == 'uart_dut_port_disconnect':
			self.uart_dut_port = data
			self.uart_dut.close()

		elif type == 'zero_cal_adc0_standard':
			self.cal.set_adc0_standard(data)

		elif type == 'start_zero_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  start zero cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.start_zero_cal()
			self.uart_dut_hijack = False
			if ret:
				self.ui.ui_append_dialog('local', '\n')
				self.uart_dut_hijack = True
				result = self.cal.read_zero_cal()
				self.uart_dut_hijack = False
				if result:
					self.ui.update_ui('zero_cal_result', result, None)

				self.ui.update_ui('message_box_info', '零点校准', '成功')
			else:
				self.ui.update_ui('message_box_err', '零点校准', '失败')

		elif type == 'read_zero_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  read zero cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.read_zero_cal()
			self.uart_dut_hijack = False
			if ret:
				self.ui.update_ui('zero_cal_result', ret, None)
			else:
				self.ui.update_ui('message_box_err', '读取零点校准', '失败')

		elif type == 'clear_zero_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  clear zero cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.clear_zero_cal()
			self.uart_dut_hijack = False

			if ret:
				self.ui.ui_append_dialog('local', '\n')
				self.uart_dut_hijack = True
				result = self.cal.read_zero_cal()
				self.uart_dut_hijack = False
				if result:
					self.ui.update_ui('zero_cal_result', result, None)

				self.ui.update_ui('message_box_info', '清除零点校准', '成功')
			else:
				self.ui.update_ui('message_box_err', '清除零点校准', '失败')

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
		
	
	
	
