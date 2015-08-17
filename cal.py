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

AT_MAC_Q = 'AT+MAC'

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

AT_LOW_TEMP_CAL = 'AT+LOWTEMPCAL='
AT_LOW_TEMP_CAL_Q = 'AT+LOWTEMPCAL'
AT_HIGH_TEMP_CAL = 'AT+HIGHTEMPCAL='
AT_HIGH_TEMP_CAL_Q = 'AT+HIGHTEMPCAL'
AT_TEMP_CAL = 'AT+TEMPCAL='
AT_TEMP_CAL_Q = 'AT+TEMPCAL'

AT_STEST = 'AT+STEST'

class Cal:

	def __init__(self, log, uart_dut, uart_std, ui):
		self.log = log
		self.uart_dut = uart_dut
		self.uart_std = uart_std
		self.ui = ui
		self.sys_config = config.Config(self.log)

		self.adc0_standard = int(self.sys_config.get('zero_cal_adc0_standard'))
		self.adc0_stable_threshold = int(self.sys_config.get('adc0_stable_threshold'))

	def __exit__(self):
		pass

	def wait_sec(self, cnt):
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

	def send_dut_cmd(self, cmd):
		self.uart_dut.send(cmd)

	def send_std_cmd(self, cmd):
		self.uart_std.send(cmd)

	def dut_send_and_get_resp(self, cmd):
		self.dut_resp = ''
		self.send_dut_cmd(cmd)
		self.ui.ui_append_dialog('to_dut', cmd)

		self.wait_sec(0.1)
		return self.remove_cr(self.dut_resp)

	def std_send_and_get_resp(self, cmd):
		self.std_resp = ''
		self.send_std_cmd(cmd)
		self.ui.ui_append_dialog('to_std', cmd)

		self.wait_sec(0.1)
		return self.remove_cr(self.std_resp)

	def get_dut_resp(self, data):
		self.dut_resp = self.remove_duplicated_cr(data)

	def get_std_resp(self, data):
		self.std_resp = self.remove_duplicated_cr(data)

	def check_adc_stable(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = '%s\n' %AT_ADC0
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+ADC0:(\d+)$', resp)
		if s:
			pre_adc0 = int(s.group(1))
		else:
			return False

		i = 0
		while True:
			cmd = '%s\n' %AT_ADC0
			resp = self.dut_send_and_get_resp(cmd)
			s = re.search(r'^\+ADC0:(\d+)$', resp)
			if s:
				adc0 = int(s.group(1))
			else:
				return False

			if abs(adc0 - pre_adc0) < self.adc0_stable_threshold:
				return True

			i += 1
			if i > 10:
				return False
			else:
				self.wait_sec(1)

	def start_test(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = '%s\n' %AT_STEST
		self.dut_send_and_get_resp(cmd)

		return True
		# cnt = 0
		# while True:
		# 	self.wait_sec(1)
		# 	resp = self.remove_cr(self.dut_resp)
		# 	s = re.match(r'^OK$', resp)
		# 	if s:
		# 		return True
        #
		# 	s = re.match(r'^ERROR$', resp)
		# 	if s:
		# 		print resp
		# 		return False
        #
		# 	cnt += 1
		# 	if cnt > 30:
		# 		print cnt
		# 		return False

	def start_zero_cal(self):
		cmd = '%s\n' %AT_MAC_Q
		resp = self.dut_send_and_get_resp(cmd)
		mac = re.match(r'^([a-f0-9A-F]{2}:){3}[a-f0-9A-F]{2}$', resp)
		if not mac:
			return (False, "获取MAC失败")

		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return (False, "切换到校准模式失败")

		cmd = '%s\n' %AT_HWADC0
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+HWADC0:(\d+)$', resp)
		if s:
			hw_adc0 = int(s.group(1))
		else:
			return (False, '读取HWADC0失败')

		delta = self.adc0_standard - hw_adc0
		if abs(delta) > 100:
			return (False, '偏差超出正常范围')

		cmd = AT_ADC0_DELTA  + str(delta) + '\n'
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return (False, '设置ADC0 DELTA失败')
		else:
			return (True,
					{
						'TYPE' : 'ZEROCAL',
						'MAC' : mac,
						'HWADC' : hw_adc0,
						'delta' : delta,
					})

	def read_zero_cal(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = '%s\n' %AT_HWADC0
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+HWADC0:(\d+)$', resp)
		if s:
			hw_adc0 = int(s.group(1))
		else:
			return False

		cmd = '%s\n' %AT_ADC0_DELTA_Q
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
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = '%s0\n' %AT_ADC0_DELTA
		resp = self.dut_send_and_get_resp(cmd)

		return resp == 'OK'

	def start_low_temp_cal(self):
		if not self.check_adc_stable():
			return False

		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		# get R_low
		cmd = '%s\n' %AT_CH0RT
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0RT:(\d+.\d+)$', resp)
		if s:
			R_low = float(s.group(1))
		else:
			return False

		# get t_low from std board
		cmd = '%s\n' %AT_TEMP0
		resp = self.std_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0TEMP:(\d+.\d+)$', resp)
		if s:
			t_low = float(s.group(1))
		else:
			return False

		# write to board
		cmd = '%s%.4f,%.4f\n' %(AT_LOW_TEMP_CAL, R_low, t_low)
		# print 'sendcmd' + cmd
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False
		else:
			return True

	def read_low_temp_cal(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = '%s\n' %AT_ADC0
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+ADC0:(\d+)$', resp)
		if s:
			adc0 = int(s.group(1))
		else:
			return False

		cmd = '%s\n' %AT_LOW_TEMP_CAL_Q
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+LOWTEMPCAL:(\d+.\d+),(\d+.\d+)$', resp)
		if s:
			R_low = float(s.group(1))
			t_low = float(s.group(2))
		else:
			return False

		# get t_std from std board
		cmd = '%s\n' %AT_TEMP0
		resp = self.std_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0TEMP:(\d+.\d+)$', resp)
		if s:
			t_std = float(s.group(1))
		else:
			t_std = 0

		t_delta = t_low - t_std

		return {'adc0'  : adc0,
				'R_low' : '%.4f' %R_low,
				't_low' : '%.4f' %t_low,
				't_std' : '%.4f' %t_std,
				't_delta' : '%.4f' %t_delta,
				}

	def clear_low_temp_cal(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		# write to board
		cmd = '%s%.4f,%.4f\n' %(AT_LOW_TEMP_CAL, 0, 0)
		# print 'sendcmd' + cmd
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False
		else:
			return True

	def start_high_temp_cal(self):
		if not self.check_adc_stable():
			return False

		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		# get R_high
		cmd = '%s\n' %AT_CH0RT
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0RT:(\d+.\d+)$', resp)
		if s:
			R_high = float(s.group(1))
		else:
			return False

		# get t_high from std board
		cmd = '%s\n' %AT_TEMP0
		resp = self.std_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0TEMP:(\d+.\d+)$', resp)
		if s:
			t_high = float(s.group(1))
		else:
			# print resp
			return False

		# write to board
		cmd = '%s%.4f,%.4f\n' %(AT_HIGH_TEMP_CAL, R_high, t_high)
		# print 'sendcmd' + cmd
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False
		else:
			return True

	def read_high_temp_cal(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = AT_ADC0  + '\n'
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+ADC0:(\d+)$', resp)
		if s:
			adc0 = int(s.group(1))
		else:
			return False

		cmd = '%s\n' %AT_HIGH_TEMP_CAL_Q
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+HIGHTEMPCAL:(\d+.\d+),(\d+.\d+)$', resp)
		if s:
			R_high = float(s.group(1))
			t_high = float(s.group(2))
		else:
			return False

		# get t_std from std board
		cmd = '%s\n' %AT_TEMP0
		resp = self.std_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0TEMP:(\d+.\d+)$', resp)
		if s:
			t_std = float(s.group(1))
		else:
			t_std = 0

		t_delta = t_high - t_std

		return {'adc0'  : adc0,
				'R_high' : '%.4f' %R_high,
				't_high' : '%.4f' %t_high,
				't_std' : '%.4f' %t_std,
				't_delta' : '%.4f' %t_delta,
				}

	def clear_high_temp_cal(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		# write to board
		cmd = '%s%.4f,%.4f\n' %(AT_HIGH_TEMP_CAL, 0, 0)
		# print 'sendcmd' + cmd
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False
		else:
			return True

	# R25 = R1*(R1/R2)^[(A-B)/(B-C)]
	# B(25/50)=[1/(B-C)]*ln(R1/R2)
	# A=1/298.15,   B =1/(T1+273.15),   C =1/(T2+273.15)
	def cal_temp_delta(self, R_low, t_low, R_high, t_high):
		A = 1.0 / (25 + 273.15)
		B = 1.0 / (t_low + 273.15)
		C = 1.0 / (t_high + 273.15)

		R25 = R_low * math.pow(R_low / R_high, (A - B) / (B - C))

		B25_50 = (1.0 / (B - C)) * math.log(R_low / R_high)

		return (B25_50 - 3950, R25 - 100.0)

	def start_temp_cal(self):
		# check whether low temp cal completed
		cmd = '%s\n' %AT_LOW_TEMP_CAL_Q
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+LOWTEMPCAL:(\d+.\d+),(\d+.\d+)$', resp)
		if not s:
			return (False, '读取低温校准信息失败')
		if not cmp(s.group(1), '0.000000') or not cmp(s.group(2), '0.000000'):
			return (False, '低温校准信息格式不正确: %s', resp)

		R_low = float(s.group(1))
		t_low = float(s.group(2))

		# check whether high temp cal completed
		cmd = '%s\n' %AT_HIGH_TEMP_CAL_Q
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+HIGHTEMPCAL:(\d+.\d+),(\d+.\d+)$', resp)
		if not s:
			return (False, '读取高温校准信息失败')
		if not cmp(s.group(1), '0.000000') or not cmp(s.group(2), '0.000000'):
			return (False, '高温校准信息格式不正确: %s', resp)

		R_high = float(s.group(1))
		t_high = float(s.group(2))

		(B_delta, R25_delta) = self.cal_temp_delta(R_low, t_low, R_high, t_high)
		if abs(B_delta) > 100 or abs(R25_delta) > 2:
			return (False, 'B_delta %f 或 R25_delta %f 超出范围' %(B_delta, R25_delta))

		cmd = '%s%.4f,%.4f\n' %(AT_TEMP_CAL, B_delta, R25_delta)
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return (False, '设置B_delta&R25_delta 失败')
		else:
			return (True, 'OK')

	def read_temp_cal(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		cmd = '%s\n' %AT_ADC0
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+ADC0:(\d+)$', resp)
		if s:
			adc0 = int(s.group(1))
		else:
			return False

		cmd = '%s\n' %AT_TEMP_CAL_Q
		resp = self.dut_send_and_get_resp(cmd)
		# print resp
		s = re.search(r'^\+TEMPCAL:(-?\d+.\d+),(-?\d+.\d+)$', resp)
		if s:
			B_delta = float(s.group(1))
			R25_delta = float(s.group(2))
		else:
			return False

		# get temp
		cmd = '%s\n' %AT_TEMP0
		resp = self.dut_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0TEMP:(\d+.\d+)$', resp)
		if s:
			temp = float(s.group(1))
		else:
			return False

		# get t_std from std board
		cmd = '%s\n' %AT_TEMP0
		resp = self.std_send_and_get_resp(cmd)
		s = re.search(r'^\+CH0TEMP:(\d+.\d+)$', resp)
		if s:
			t_std = float(s.group(1))
		else:
			t_std = 0

		t_delta = temp - t_std

		return {'adc0'  : adc0,
				'B_delta' : '%.4f' %B_delta,
				'R25_delta' : '%.4f' %R25_delta,
				'temp' : '%.4f' %temp,
				't_std' : '%.4f' %t_std,
				't_delta' : '%.4f' %t_delta,
				}

	def clear_temp_cal(self):
		cmd = '%s1\n' %AT_MODE
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False

		# write to board
		cmd = '%s%.4f,%.4f\n' %(AT_TEMP_CAL, 0, 0)
		# print 'sendcmd' + cmd
		resp = self.dut_send_and_get_resp(cmd)
		s = re.match(r'^OK$', resp)
		if not s:
			return False
		else:
			return True

	def set_adc0_standard(self, val):
		self.adc0_standard = int(val)

	def set_adc0_stable_threshold(self, val):
		self.adc0_stable_threshold = int(val)