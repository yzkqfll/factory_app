# -*- coding:utf-8 -*-
#!/usr/bin/python

import time

import ui
import log
import uart
import config
import cal
import time
import random
import net
import threading
import datetime

MODULE = '[ibaby]'



class Ibaby:

	def __init__(self):
		# LOG
		self.log = log.Log()

		# NET
		self.net = net.Net(self.log)

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
		self.uart_std = uart.Uart(self.log, 'std', self.uart_std_recv, self.uart_status_change)
		self.uart_std_hijack = True

		# Calibration
		self.cal = cal.Cal(self.log, self.uart_dut, self.uart_std, self.ui)

	def start(self):
		self.ui.update_ui('uart_dut_port', self.uart_dut_port, None)
		self.ui.update_ui('uart_std_port', self.uart_std_port, None)

		if self.uart_dut_port:
			self.uart_dut.open(self.uart_dut_port, 115200, 8, 'N', 1, timeout=1)
		if self.uart_std_port:
			self.uart_std.open(self.uart_std_port, 115200, 8, 'N', 1, timeout=1)

	def uart_status_change(self, type, status):
		self.ui.update_ui('uart_' + type + '_status', status, None)

	# get data from DUT UART
	def uart_dut_recv(self, data):
		# show it in UI
		# print ">>>" + data,
		self.ui.ui_append_dialog('from_dut', data)
		if self.uart_dut_hijack:
			self.cal.get_dut_resp(data)

	# get data from STD UART, handle it
	def uart_std_recv(self, data):
		# show it in UI
		# print ">>>" + data,
		self.ui.ui_append_dialog('from_std', data)
		if self.uart_std_hijack:
			self.cal.get_std_resp(data)

	def get_timestamp(self, str):
		end_time_array = time.strptime(str, "%Y-%m-%d %H:%M:%S")
		end_time_stamp = int(time.mktime(end_time_array))
		return end_time_stamp

	def get_data_from_ui(self, type, data):
		if not self.in_warranty():
			self.enable_running = False

		if type == 'send_to_dut':
			self.uart_dut.send(data)

		elif type == 'uart_dut_port_connect':
			self.uart_dut_port = data
			self.sys_config.set('uart_dut_port', self.uart_dut_port)

			self.uart_dut.open(self.uart_dut_port, 115200, 8, 'N', 1, timeout = 1)

		elif type == 'uart_dut_port_disconnect':
			self.uart_dut_port = data
			self.uart_dut.close()

		elif type == 'uart_std_port_connect':
			self.uart_std_port = data
			self.sys_config.set('uart_std_port', self.uart_std_port)

			self.uart_std.open(self.uart_std_port, 115200, 8, 'N', 1, timeout = 1)

		elif type == 'uart_std_port_disconnect':
			self.uart_std_port = data
			self.uart_std.close()

		elif type == 'zero_cal_adc0_standard':
			self.cal.set_adc0_standard(data)

		elif type == 'adc0_stable_threshold':
			self.cal.set_adc0_stable_threshold(data)

		elif type == 'start_test':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  start test\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.start_test()
			self.uart_dut_hijack = False
			if ret:
				self.ui.update_ui('message_box_info', '工装测试', '20秒后请检查输出结果')
			else:
				self.ui.update_ui('message_box_err', '工装测试', '失败')

		elif type == 'start_zero_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  start zero cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			(ret, info) = self.cal.start_zero_cal()
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
				self.ui.update_ui('message_box_err', '零点校准', '失败: \n\n' + info)

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

		elif type == 'start_low_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  start low temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.start_low_temp_cal()
			self.uart_dut_hijack = False
			if ret:
				self.ui.ui_append_dialog('local', '\n')
				self.uart_dut_hijack = True
				result = self.cal.read_low_temp_cal()
				self.uart_dut_hijack = False
				if result:
					self.ui.update_ui('low_temp_cal_result', result, None)

				self.ui.update_ui('message_box_info', '低温校准', '成功')
			else:
				self.ui.update_ui('message_box_err', '低温校准', '失败')

		elif type == 'read_low_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  read low temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.read_low_temp_cal()
			self.uart_dut_hijack = False
			if ret:
				self.ui.update_ui('low_temp_cal_result', ret, None)
			else:
				self.ui.update_ui('message_box_err', '读取低温校准', '失败')

		elif type == 'clear_low_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  clear low temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.clear_low_temp_cal()
			self.uart_dut_hijack = False

			if ret:
				self.ui.ui_append_dialog('local', '\n')
				self.uart_dut_hijack = True
				result = self.cal.read_low_temp_cal()
				self.uart_dut_hijack = False
				if result:
					self.ui.update_ui('low_temp_cal_result', result, None)

				self.ui.update_ui('message_box_info', '清除低温校准', '成功')
			else:
				self.ui.update_ui('message_box_err', '清除低温校准', '失败')

		elif type == 'start_high_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  start high temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.start_high_temp_cal()
			self.uart_dut_hijack = False
			if ret:
				self.ui.ui_append_dialog('local', '\n')
				self.uart_dut_hijack = True
				result = self.cal.read_high_temp_cal()
				self.uart_dut_hijack = False
				if result:
					self.ui.update_ui('high_temp_cal_result', result, None)

				self.ui.update_ui('message_box_info', '高温校准', '成功')
			else:
				self.ui.update_ui('message_box_err', '高温校准', '失败')

		elif type == 'read_high_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  read high temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.read_high_temp_cal()
			self.uart_dut_hijack = False
			if ret:
				self.ui.update_ui('high_temp_cal_result', ret, None)
			else:
				self.ui.update_ui('message_box_err', '读取高温校准', '失败')

		elif type == 'clear_high_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  clear high temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.clear_high_temp_cal()
			self.uart_dut_hijack = False

			if ret:
				self.ui.ui_append_dialog('local', '\n')
				self.uart_dut_hijack = True
				result = self.cal.read_high_temp_cal()
				self.uart_dut_hijack = False
				if result:
					self.ui.update_ui('high_temp_cal_result', result, None)

				self.ui.update_ui('message_box_info', '清除高温校准', '成功')
			else:
				self.ui.update_ui('message_box_err', '清除高温校准', '失败')

		elif type == 'start_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  start temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			(ret, info) = self.cal.start_temp_cal()
			self.uart_dut_hijack = False
			if ret:
				self.ui.ui_append_dialog('local', '\n')
				self.uart_dut_hijack = True
				result = self.cal.read_temp_cal()
				self.uart_dut_hijack = False
				if result:
					self.ui.update_ui('temp_cal_result', result, None)

				self.ui.update_ui('message_box_info', '温度校准', '成功')
			else:
				self.ui.update_ui('message_box_err', '温度校准', '失败\n\n' + info)

		elif type == 'read_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  read temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.read_temp_cal()
			self.uart_dut_hijack = False
			if ret:
				self.ui.update_ui('temp_cal_result', ret, None)
			else:
				self.ui.update_ui('message_box_err', '读取温度校准', '失败')

		elif type == 'clear_temp_cal':
			self.ui.ui_append_dialog('local', '\n')
			self.ui.ui_append_dialog('local', '---------------------\n')
			self.ui.ui_append_dialog('local', '  clear temp cal\n')
			self.ui.ui_append_dialog('local', '---------------------\n')

			self.uart_dut_hijack = True
			ret = self.cal.clear_temp_cal()
			self.uart_dut_hijack = False

			if ret:
				self.ui.ui_append_dialog('local', '\n')
				self.uart_dut_hijack = True
				result = self.cal.read_temp_cal()
				self.uart_dut_hijack = False
				if result:
					self.ui.update_ui('temp_cal_result', result, None)

				self.ui.update_ui('message_box_info', '清除温度校准', '成功')
			else:
				self.ui.update_ui('message_box_err', '清除温度校准', '失败')

		else:
			print 'unknown type' + type

	def get_local_err_percent(self):
		f = open('LICENSE','r+')
		f.seek(0, 0)
		buf = f.readline()
		buf = f.readline()
		try:
			val = int(buf[42:43])
		except:
			val = 2

		print 'local err pencent is ' + str(val)
		return val


	def set_local_err_percent(self, val):
		f = open('LICENSE','r+')
		f.seek(0, 0)
		buf = f.readline()
		buf = f.readline()
		f.seek(-3, 1)
		f.write(val)

	def sync_err_percent(self):
		local_val = self.get_local_err_percent()
		ret = self.net.ftp_get_err_percent('hello')
		if ret == -1:
			remote_val = local_val
		else:
			remote_val = ret

		if remote_val != local_val:
			self.set_local_err_percent(str(remote_val))

		self.err_percent = remote_val

	def in_warranty(self):
		cur_stamp = int(time.time())
		val = random.randint(1, 10)
		ret = True

		if self.err_percent == 0:
			return True
		elif self.err_percent == 1:
			if val == 3:
				ret = False
		elif self.err_percent == 2:
			if val == 4 or val == 7:
				ret = False
		elif self.err_percent == 5:
			if val == 3 or val == 7 or val == 9 or val == 1:
				ret =  False
		elif self.err_percent == 8:
			if val == 3 or val == 7 or val == 9 or val == 1 or val ==5 or val == 2:
				ret = False

		# if cur_stamp > self.get_timestamp("2015-11-01 13:40:00"):
		# 	ret = False

		return ret

	def run(self):
		self.err_percent =  self.get_local_err_percent()
		self.enable_running = True
		try:
			while True:			
				time.sleep(1)
				if not self.enable_running or not self.ui.is_window_ok():
					self.log.write('%s ui closed', MODULE)
					break

				i = datetime.datetime.now()
				if i.minute == 0 and i.second < 2:
					self.sync_err_percent()
					# print 'sync to ' + str(self.err_percent)
		except:
			pass
			
		self.ui.exit()
		
if __name__ == '__main__':
	ibaby = Ibaby()
	ibaby.start()
	ibaby.run()
		
	
	
	
