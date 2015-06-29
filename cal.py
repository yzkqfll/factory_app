# -*- coding:utf-8 -*-
#!/usr/bin/python

import time
import re
import math

import config

MODULE = '[calibration]'

AT_CMD = 'AT'
AT_MODE = 'AT+MODE='
AT_MODE_Q = 'AT+MODE'
AT_LDO = 'AT+LDO='
AT_LDO_Q = 'AT+LDO'
AT_ADC0 = 'AT+ADC0'
AT_ADC1 = 'AT+ADC1'
AT_HWADC0 = 'AT+HWADC0'
AT_HWADC1 = 'AT+HWADC1'
AT_CH0RT = 'AT+CH0RT'
AT_CH1RT = 'AT+CH1RT'
AT_TEMP0 = 'AT+CH0TEMP'
AT_TEMP1 = 'AT+CH1TEMP'

AT_ADC0_DELTA = 'AT+ADC0DELTA='
AT_ADC0_DELTA_Q = 'AT+ADC0DELTA'

AT_B_DELTA = 'AT+BDELTA='
AT_B_DELTA_Q = 'AT+BDELTA'
AT_R25_DELTA = 'AT+R25_DELTA='
AT_R25_DELTA_Q = 'AT+R25_DELTA'

class Cal:

	def __init__(self, log, uart_dut, ui):
		self.log = log
		self.uart_dut = uart_dut
		self.ui = ui
		self.sys_config = config.Config(self.log)

		self.adc0_standard = int(self.sys_config.get('zero_cal_adc0_standard'))

	def __exit__(self):
		pass

	def wait_resp(self, cnt):
		try:
			time.sleep(cnt)
		except:
			pass

	def remove_duplicated_cr(self, data):
		if data.endswith('\n\r\n'):
			return data[:-2]
		elif data.endswith('\n\n'):
			return data[:-1]
		elif data.endswith('\n'):
			return data
		else:
			return data

	def remove_cr(self, data):
		if data.endswith('\n\n'):
			return data[:-2]
		elif data.endswith('\n'):
			return data[:-1]
		else:
			return data

	def get_Rt_by_ch0(self, adc):
		return 56.0 / (1.0 / (float(adc) / 40960.0 + 56.0 / (56.0 + 76.8)) - 1)

	def get_temp_by_Rt(self, Rt, B_delta, R25_delta):
		print Rt
		B = 3950 + B_delta
		R25 = 100.0 + R25_delta

		temp = 1.0 / (1.0 / (25.0 + 273.15) - math.log(R25 / Rt) / B) - 273.15
		return temp

	def send_cmd(self, cmd):
		self.uart_dut.send(cmd)

	def dut_send_and_get_resp(self, cmd):
		self.dut_resp = ''
		self.send_cmd(cmd)
		self.ui.ui_append_dialog('local', cmd)

		self.wait_resp(0.1)
		return self.remove_cr(self.dut_resp)

	def get_dut_resp(self, data):
		self.dut_resp = self.remove_duplicated_cr(data)

	def start_zero_cal(self):
		cmd = AT_MODE  + '1' + '\n'
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = AT_HWADC0  + '\n'
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+HWADC0:(\d+)$', resp)
		if s:
			hw_adc0 = int(s.group(1))
		else:
			return False

		delta = self.adc0_standard - hw_adc0

		cmd = AT_ADC0_DELTA  + str(delta) + '\n'
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False
		else:
			return True

	def read_zero_cal(self):
		cmd = AT_MODE  + '1' + '\n'
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = AT_HWADC0  + '\n'
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+HWADC0:(\d+)$', resp)
		if s:
			hw_adc0 = int(s.group(1))
		else:
			return False

		cmd = AT_ADC0_DELTA_Q  + '\n'
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0 ADC DELTA:(-?\d+)$', resp)
		if s:
			adc0_delta = int(s.group(1))
		else:
			return False

		adc0_before_cal = hw_adc0
		Rt_before_cal = self.get_Rt_by_ch0(adc0_before_cal)
		temp_before_cal = self.get_temp_by_Rt(Rt_before_cal, 0, 0)

		adc0_after_cal = hw_adc0 + adc0_delta
		Rt_after_cal = self.get_Rt_by_ch0(adc0_after_cal)
		temp_after_cal = self.get_temp_by_Rt(Rt_after_cal, 0, 0)

		return {'hw_adc0_before_cal' : hw_adc0,
				'adc0_delta_before_cal' : 0,
				'adc0_before_cal' : adc0_before_cal,
				'Rt_before_cal' : '%.4f' %Rt_before_cal,
				'temp_before_cal' : '%.4f' %temp_before_cal,

				'hw_adc0_after_cal' : hw_adc0,
				'adc0_delta_after_cal' : adc0_delta,
				'adc0_after_cal' : adc0_after_cal,
				'Rt_after_cal' : '%.4f' %Rt_after_cal,
				'temp_after_cal' : '%.4f' %temp_after_cal,
				}

	def clear_zero_cal(self):
		cmd = AT_ADC0_DELTA + '0' + '\n'
		resp = self.dut_send_and_get_resp(cmd)

		return resp == 'OK'

	def set_adc0_standard(self, val):
		self.adc0_standard = int(val)