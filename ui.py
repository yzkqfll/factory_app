# -*- coding:utf-8 -*-
#!/usr/bin/python

import ConfigParser
import string
import thread
import time
import re

import tkFont
from Tkinter import *
#from tkMessageBox import *
import tkMessageBox

import config

MODULE = '[UI]'

SOFTWARE_NAME = 'ibaby校准软件'
VERSION = 'v0.2'

class Ui:

	def __init__(self, log, handle_data_from_ui):
		self.window_ok = False

		self.log = log

		self.handle_data_from_ui = handle_data_from_ui

		# configs
		self.sys_config = config.Config(self.log)

		if not self.sys_config.get('mode'):
			self.sys_config.set('mode', 'all')
		self.mode = self.sys_config.get('mode')

		if not self.sys_config.get('zero_cal_adc0_standard'):
			self.sys_config.set('zero_cal_adc0_standard', 3207)

		if not self.sys_config.get('adc0_stable_threshold'):
			self.sys_config.set('adc0_stable_threshold', 20)

		# launch UI
		self.ui_mainloop_thread = thread.start_new_thread(self.lanuch_ui, (None, ))


	def lanuch_ui(self, x):
		self.log.write('%s launch ui', MODULE)

		# create main window
		self.main_win = main_win = Tk()
		main_win.title(SOFTWARE_NAME + VERSION)
		self.set_win_geometry(main_win, 1000, 730, 6)

		# font
		self.font_dialog = tkFont.Font(family = '宋体', size = 10, weight = "bold")
		self.font_input = tkFont.Font(family = '宋体', size = 11, weight = "bold")

		# String var
		self.mode_var = StringVar()
		self.mode_var.set(self.sys_config.get('mode'))

		self.zero_cal_adc0_standard = StringVar()
		self.zero_cal_adc0_standard.set(self.sys_config.get('zero_cal_adc0_standard'))

		self.adc0_stable_threshold = StringVar()
		self.adc0_stable_threshold.set(self.sys_config.get('adc0_stable_threshold'))

		self.indicating_bar_var = StringVar()

		self.uart_dut_port_var = StringVar()
		self.uart_dut_status_var = StringVar()
		self.uart_std_port_var = StringVar()
		self.uart_std_status_var = StringVar()

		self.hw_adc0_before_cal_var = StringVar()
		self.adc0_delta_before_cal_var = StringVar()
		self.adc0_before_cal_var = StringVar()
		self.Rt_before_cal_var = StringVar()
		self.Temp_before_cal_var = StringVar()

		self.hw_adc0_after_cal_var = StringVar()
		self.adc0_delta_after_cal_var = StringVar()
		self.adc0_after_cal_var = StringVar()
		self.Rt_after_cal_var = StringVar()
		self.temp_after_cal_var = StringVar()

		self.low_temp_cal_adc_var = StringVar()
		self.low_temp_cal_R_low_var = StringVar()
		self.low_temp_cal_t_low_var = StringVar()
		self.low_temp_cal_t_std_var = StringVar()
		self.low_temp_cal_t_delta_var = StringVar()

		self.high_temp_cal_adc_var = StringVar()
		self.high_temp_cal_R_high_var = StringVar()
		self.high_temp_cal_t_high_var = StringVar()
		self.high_temp_cal_t_std_var = StringVar()
		self.high_temp_cal_t_delta_var = StringVar()

		self.temp_cal_adc_var = StringVar()
		self.temp_cal_B_delta_var = StringVar()
		self.temp_cal_R25_delta_var = StringVar()
		self.temp_cal_temp_var = StringVar()
		self.temp_cal_t_std_var = StringVar()
		self.temp_cal_t_delta_var = StringVar()

		# menu
		menu_base = Menu(main_win)
		main_win.config(menu = menu_base)

		menu_cascade_set = Menu(menu_base, tearoff = 0)
		menu_cascade_set.add_separator()
		menu_cascade_set.add_command(label = "模式设置", command = self.menu_item_mode)
		menu_cascade_set.add_command(label = "零点校准", command = self.menu_item_zero_cal)
		menu_cascade_set.add_command(label = "高低温校准", command = self.menu_item_temp_cal)
		menu_cascade_set.add_command(label = "退出", command = main_win.quit)
		menu_base.add_cascade(label="设置", menu = menu_cascade_set)
		
		menu_cascade_help = Menu(menu_base, tearoff=0)
		menu_cascade_help.add_command(label = "欢迎", command = self.menu_item_welcome)
		menu_cascade_help.add_separator()
		menu_cascade_help.add_command(label = "使用说明", command = self.menu_item_readme)
		menu_cascade_help.add_separator()
		menu_cascade_help.add_command(label = "AT命令说明", command = self.menu_item_AT_usage)
		menu_cascade_help.add_separator()
		menu_cascade_help.add_command(label = "关于" + SOFTWARE_NAME, command = self.menu_item_about)
		menu_base.add_cascade(label="帮助", menu = menu_cascade_help)

		x_base = 10
		y_base = 20
		x_pos = x_base
		y_pos = y_base

		# text dialog
		self.scrollbar = Scrollbar(main_win)
		self.text_dialog = Text(main_win, height=20, width=70,
									yscrollcommand = self.scrollbar.set, font = self.font_dialog, bg = 'gray')
		x_pos += 0; y_pos += 0; ww = 600; hh = 550
		self.text_dialog.place(x = x_pos, y = y_pos, width = ww, height = hh)
		#t.bind("<KeyPress>", lambda e : "break")
		self.scrollbar.config(command = self.text_dialog.yview)
		x_pos += ww; y_pos += 0; ww = 20; hh = 550
		self.scrollbar.place(x = x_pos, y = y_pos, width = ww, height = hh)

		self.text_dialog.tag_config('fg_blue',foreground = 'blue') # create tag
		self.text_dialog.tag_config('fg_darkred',foreground = 'darkred')

		# indicating bar(such as: typing)
		l = Label(main_win, textvariable = self.indicating_bar_var, anchor = 'w')
		l.config(fg = 'DarkBlue')
		x_pos = x_base; y_pos += hh; ww = 300; hh = 25
		l.place(x = x_pos, y = y_pos, width = ww, height = hh)

		# text input
		self.text_input = Text(main_win, height = 6, width=70, font = self.font_input)
		x_pos = x_base; y_pos += hh; ww = 620; hh = 110
		self.text_input.place(x = x_pos, y = y_pos, width = ww, height = hh)
		#t.bind("<Return>", self.on_send_msg)
		self.text_input.bind("<KeyRelease-Return>", self.on_send_msg)

		x_base = 630
		y_base = 10
		x_pos = x_base
		y_pos = y_base

		l = Label(main_win, text = '                                       串口信息', anchor = 'w')
		l.config(fg = 'white', bg = 'Black')
		x_pos += 0; y_pos += 0; ww = 370; hh = 25
		l.place(x = x_pos, y = y_pos, width = ww, height = hh)

		# UART DUT
		l = Label(main_win, text = 'DUT', anchor = 'w')
		l.config(fg = 'DarkBlue')
		x_pos = x_base + 10; y_pos += hh; ww = 30; hh = 25
		l.place(x = x_pos, y = y_pos, width = ww, height = hh)

		self.uart_dut = Entry(main_win, width = 10, textvariable = self.uart_dut_port_var)
		x_pos += ww + 10; y_pos += 0; ww = 60; hh = 25
		self.uart_dut.place(x = x_pos, y = y_pos, width = ww, height = hh)
		self.uart_dut.bind("<KeyRelease-Return>", self.uart_dut_port_connect2)

		self.uart_dut_status = l = Label(main_win, textvariable = self.uart_dut_status_var, anchor = 'w')
		l.config(fg = 'DarkBlue')
		x_pos += ww + 10; y_pos += 0; ww = 80; hh = 25
		l.place(x = x_pos, y = y_pos, width = ww, height = hh)

		self.button_dut_connect = Button(main_win, text = '连接', command = self.uart_dut_port_connect, width = 10)
		# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
		x_pos += ww + 10; y_pos += 0; ww = 60; hh = 25
		self.button_dut_connect.place(x = x_pos, y = y_pos, width = ww, height = hh)

		self.button_dut_disconnect = Button(main_win, text = '断开', command = self.uart_dut_port_disconnect, width = 10)
		# self.button_dut_disconnect['state'] = 'disabled'	if self.net.net_connected() else 'normal'
		x_pos += ww + 10; y_pos += 0; ww = 60; hh = 25
		self.button_dut_disconnect.place(x = x_pos, y = y_pos, width = ww, height = hh)

		# UART STD
		l = Label(main_win, text = 'STD', anchor = 'w')
		l.config(fg = 'DarkBlue')
		x_pos = x_base + 10; y_pos += hh; ww = 30; hh = 25
		l.place(x = x_pos, y = y_pos, width = ww, height = hh)

		self.uart_std = Entry(main_win, width = 10, textvariable = self.uart_std_port_var)
		x_pos += ww + 10; y_pos += 0; ww = 60; hh = 25
		self.uart_std.place(x = x_pos, y = y_pos, width = ww, height = hh)
		self.uart_std.bind("<KeyRelease-Return>", self.uart_std_port_connect2)

		self.uart_std_status = l = Label(main_win, textvariable = self.uart_std_status_var, anchor = 'w')
		l.config(fg = 'DarkBlue')
		x_pos += ww + 10; y_pos += 0; ww = 80; hh = 25
		l.place(x = x_pos, y = y_pos, width = ww, height = hh)

		self.button_std_connect = Button(main_win, text = '连接', command = self.uart_std_port_connect, width = 10)
		# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
		x_pos += ww + 10; y_pos += 0; ww = 60; hh = 25
		self.button_std_connect.place(x = x_pos, y = y_pos, width = ww, height = hh)

		self.button_std_disconnect = Button(main_win, text = '断开', command = self.uart_std_port_disconnect, width = 10)
		# self.button_dut_disconnect['state'] = 'disabled'	if self.net.net_connected() else 'normal'
		x_pos += ww + 10; y_pos += 0; ww = 60; hh = 25
		self.button_std_disconnect.place(x = x_pos, y = y_pos, width = ww, height = hh)

		x_base = 630
		y_base = 100
		x_pos = x_base
		y_pos = y_base

		if self.mode == 'test' or self.mode == 'all':
			# First Line
			l = Label(main_win, text = '                                       工装测试', anchor = 'w')
			l.config(fg = 'white', bg = 'Black')
			x_pos += 0; y_pos += 0; ww = 370; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_start_test = Button(main_win, text = '开始', bg = 'SteelBlue', command = self.start_test, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos = x_base + 5; y_pos += hh+10; ww = 80; hh = 25
			self.button_start_test.place(x = x_pos, y = y_pos, width = ww, height = hh)

		x_base = 630
		y_base = 200
		x_pos = x_base
		y_pos = y_base

		if self.mode == 'zero' or self.mode == 'all':
			# First Line
			l = Label(main_win, text = '                                       零点校准', anchor = 'w')
			l.config(fg = 'white', bg = 'Black')
			x_pos += 0; y_pos += 0; ww = 370; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			# Second Line
			l = Label(main_win, text = 'HW ADC', anchor = 'c')
			l.config(fg = 'Black')
			x_pos = x_base + 70; y_pos += hh; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Delta', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'ADC', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Rt', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Temp', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			# Third Line
			l = Label(main_win, text = '校准前', anchor = 'c')
			l.config(fg = 'Black')
			x_pos = x_base + 5; y_pos += hh; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, textvariable = self.hw_adc0_before_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.hw_adc0_before_cal_var.set('---')

			l = Label(main_win, textvariable = self.adc0_delta_before_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.adc0_delta_before_cal_var.set('---')

			l = Label(main_win, textvariable = self.adc0_before_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 60; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.adc0_before_cal_var.set('---')

			l = Label(main_win, textvariable = self.Rt_before_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.Rt_before_cal_var.set('---')

			l = Label(main_win, textvariable = self.Temp_before_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.Temp_before_cal_var.set('---')

			# Forth Line
			l = Label(main_win, text = '校准后', anchor = 'c')
			l.config(fg = 'Black')
			x_pos = x_base + 5; y_pos += hh; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, textvariable = self.hw_adc0_after_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.hw_adc0_after_cal_var.set('---')

			l = Label(main_win, textvariable = self.adc0_delta_after_cal_var, anchor = 'c')
			l.config(fg = 'Magenta')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.adc0_delta_after_cal_var.set('---')

			l = Label(main_win, textvariable = self.adc0_after_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 60; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.adc0_after_cal_var.set('---')

			l = Label(main_win, textvariable = self.Rt_after_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.Rt_after_cal_var.set('---')

			l = Label(main_win, textvariable = self.temp_after_cal_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.temp_after_cal_var.set('---')

			# Fifth Line

			self.button_start_zero_cal = Button(main_win, text = '开始', bg = 'SteelBlue', command = self.start_zero_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos = x_base + 5; y_pos += hh+10; ww = 80; hh = 25
			self.button_start_zero_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_read_zero_cal = Button(main_win, text = '读取', command = self.read_zero_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos += ww + 20; y_pos += 0; ww = 80; hh = 25
			self.button_read_zero_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_clear_zero_cal = Button(main_win, text = '清除', command = self.clear_zero_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos += ww + 100; y_pos += 0; ww = 55; hh = 25
			self.button_clear_zero_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

		x_base = 630
		y_base = 350
		x_pos = x_base
		y_pos = y_base

		if self.mode == 'low' or self.mode == 'all':
			# First Line
			l = Label(main_win, text = '                                       低温校准', anchor = 'w')
			l.config(fg = 'white', bg = 'Black')
			x_pos += 0; y_pos += 0; ww = 370; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			# Second Line
			l = Label(main_win, text = 'ADC', anchor = 'c')
			l.config(fg = 'Black')
			x_pos = x_base + 70; y_pos += hh; ww = 45; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Rlow', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Tlow', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Tstd', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 65; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Delta', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)


			# Third Line
			l = Label(main_win, text = '', anchor = 'c')
			l.config(fg = 'Black')
			x_pos = x_base + 5; y_pos += hh; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, textvariable = self.low_temp_cal_adc_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.low_temp_cal_adc_var.set('---')

			l = Label(main_win, textvariable = self.low_temp_cal_R_low_var, anchor = 'c')
			l.config(fg = 'Magenta')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.low_temp_cal_R_low_var.set('---')

			l = Label(main_win, textvariable = self.low_temp_cal_t_low_var, anchor = 'c')
			l.config(fg = 'Magenta')
			x_pos += ww; y_pos += 0; ww = 60; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.low_temp_cal_t_low_var.set('---')

			l = Label(main_win, textvariable = self.low_temp_cal_t_std_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.low_temp_cal_t_std_var.set('---')

			l = Label(main_win, textvariable = self.low_temp_cal_t_delta_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.low_temp_cal_t_delta_var.set('---')

			# Fifth Line

			self.button_start_low_temp_cal = Button(main_win, text = '开始', bg = 'SteelBlue', command = self.start_low_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos = x_base + 5; y_pos += hh+10; ww = 80; hh = 25
			self.button_start_low_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_read_low_temp_cal = Button(main_win, text = '读取', command = self.read_low_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos += ww + 20; y_pos += 0; ww = 80; hh = 25
			self.button_read_low_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_clear_low_temp_cal = Button(main_win, text = '清除', command = self.clear_low_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos += ww + 100; y_pos += 0; ww = 55; hh = 25
			self.button_clear_low_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

		x_base = 630
		y_base = 480
		x_pos = x_base
		y_pos = y_base

		if self.mode == 'high' or self.mode == 'all':
			# First Line
			l = Label(main_win, text = '                                       高温校准', anchor = 'w')
			l.config(fg = 'white', bg = 'Black')
			x_pos += 0; y_pos += 0; ww = 370; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			# Second Line
			l = Label(main_win, text = 'ADC', anchor = 'c')
			l.config(fg = 'Black')
			x_pos = x_base + 70; y_pos += hh; ww = 45; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Rhigh', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Thigh', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Tstd', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 65; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Delta', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)


			# Third Line
			l = Label(main_win, text = '', anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos = x_base + 5; y_pos += hh; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, textvariable = self.high_temp_cal_adc_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.high_temp_cal_adc_var.set('---')

			l = Label(main_win, textvariable = self.high_temp_cal_R_high_var, anchor = 'c')
			l.config(fg = 'Magenta')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.high_temp_cal_R_high_var.set('---')

			l = Label(main_win, textvariable = self.high_temp_cal_t_high_var, anchor = 'c')
			l.config(fg = 'Magenta')
			x_pos += ww; y_pos += 0; ww = 60; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.high_temp_cal_t_high_var.set('---')

			l = Label(main_win, textvariable = self.high_temp_cal_t_std_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.high_temp_cal_t_std_var.set('---')

			l = Label(main_win, textvariable = self.high_temp_cal_t_delta_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.high_temp_cal_t_delta_var.set('---')

			# Fifth Line

			self.button_start_high_temp_cal = Button(main_win, text = '开始', bg = 'SteelBlue', command = self.start_high_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos = x_base + 5; y_pos += hh+10; ww = 80; hh = 25
			self.button_start_high_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_read_high_temp_cal = Button(main_win, text = '读取', command = self.read_high_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos += ww + 20; y_pos += 0; ww = 80; hh = 25
			self.button_read_high_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_clear_high_temp_cal = Button(main_win, text = '清除', command = self.clear_high_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos += ww + 100; y_pos += 0; ww = 55; hh = 25
			self.button_clear_high_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

		x_base = 630
		y_base = 610
		x_pos = x_base
		y_pos = y_base

		if self.mode == 'high' or self.mode == 'all':
			# First Line
			l = Label(main_win, text = '                                       整体校准', anchor = 'w')
			l.config(fg = 'white', bg = 'Black')
			x_pos += 0; y_pos += 0; ww = 370; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			# Second Line
			l = Label(main_win, text = 'ADC', anchor = 'c')
			l.config(fg = 'Black')
			x_pos = x_base + 20; y_pos += hh; ww = 45; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'B_delta', anchor = 'c')
			l.config(fg = 'Black')
			x_pos = x_base + 70; y_pos += 0; ww = 45; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = ' R25_delta', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 60; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Temp', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Tstd', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 65; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)

			l = Label(main_win, text = 'Delta', anchor = 'c')
			l.config(fg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)


			# Third Line
			l = Label(main_win, textvariable = self.temp_cal_adc_var, anchor = 'c')
			l.config(fg = 'DarkBlue')
			x_pos = x_base + 5; y_pos += hh; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.temp_cal_adc_var.set('---')

			l = Label(main_win, textvariable = self.temp_cal_B_delta_var, anchor = 'c')
			l.config(fg = 'Magenta')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.temp_cal_B_delta_var.set('---')

			l = Label(main_win, textvariable = self.temp_cal_R25_delta_var, anchor = 'c')
			l.config(fg = 'Magenta')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.temp_cal_R25_delta_var.set('---')

			l = Label(main_win, textvariable = self.temp_cal_temp_var, anchor = 'c')
			l.config(fg = 'Yellow', bg = 'Dimgrey')
			x_pos += ww; y_pos += 0; ww = 60; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.temp_cal_temp_var.set('---')

			l = Label(main_win, textvariable = self.temp_cal_t_std_var, anchor = 'c')
			l.config(fg = 'Yellow', bg = 'Dimgrey')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.temp_cal_t_std_var.set('---')

			l = Label(main_win, textvariable = self.temp_cal_t_delta_var, anchor = 'c')
			l.config(fg = 'Green', bg = 'Black')
			x_pos += ww; y_pos += 0; ww = 55; hh = 25
			l.place(x = x_pos, y = y_pos, width = ww, height = hh)
			self.temp_cal_t_delta_var.set('---')

			# Fifth Line
			self.button_start_temp_cal = Button(main_win, text = '开始', bg = 'SteelBlue', command = self.start_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos = x_base + 5; y_pos += hh+10; ww = 80; hh = 25
			self.button_start_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_read_temp_cal = Button(main_win, text = '读取', command = self.read_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos += ww + 20; y_pos += 0; ww = 80; hh = 25
			self.button_read_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)

			self.button_clear_temp_cal = Button(main_win, text = '清除', command = self.clear_temp_cal, width = 10)
			# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
			x_pos += ww + 100; y_pos += 0; ww = 55; hh = 25
			self.button_clear_temp_cal.place(x = x_pos, y = y_pos, width = ww, height = hh)


		# Start main window
		self.window_ok = True
		self.main_win.mainloop()
		# when running here, the main window is died
		self.window_ok = False

	#
	# setting Menu
	#
	def menu_item_mode(self):
		sub_w = Toplevel(self.main_win)
		sub_w.title('模式设置')
		self.set_win_geometry(sub_w, 350, 200, 4)

		l = Label(sub_w, text = '工位', anchor = 'c')
		l.config(fg = 'DarkBlue')
		l.place(x = 30, y = 20, width = 100, height = 25)

		e = Entry(sub_w, width = 15, textvariable = self.mode_var)
		e.place(x = 200, y = 20, width = 100, height = 25)

		b = Button(sub_w, text = '保存', command = self.mode_setting_save, width = 10)
		b.place(x = 150, y = 130, width = 80, height = 25)

	def menu_item_zero_cal(self):
		sub_w = Toplevel(self.main_win)
		sub_w.title('零点校准设置')
		self.set_win_geometry(sub_w, 350, 200, 4)

		l = Label(sub_w, text = '理论ADC0值', anchor = 'c')
		l.config(fg = 'DarkBlue')
		l.place(x = 30, y = 20, width = 100, height = 25)

		e = Entry(sub_w, width = 15, textvariable = self.zero_cal_adc0_standard)
		e.place(x = 200, y = 20, width = 100, height = 25)

		b = Button(sub_w, text = '保存', command = self.zero_cal_setting_save, width = 10)
		b.place(x = 150, y = 130, width = 80, height = 25)

	def menu_item_temp_cal(self):
		sub_w = Toplevel(self.main_win)
		sub_w.title('高低温校准设置')
		self.set_win_geometry(sub_w, 350, 200, 4)

		l = Label(sub_w, text = 'ADC0稳定门限值', anchor = 'c')
		l.config(fg = 'DarkBlue')
		l.place(x = 30, y = 20, width = 100, height = 25)

		e = Entry(sub_w, width = 15, textvariable = self.adc0_stable_threshold)
		e.place(x = 200, y = 20, width = 100, height = 25)

		b = Button(sub_w, text = '保存', command = self.temp_cal_setting_save, width = 10)
		b.place(x = 150, y = 130, width = 80, height = 25)

	#
	# help Menu
	#
	def menu_item_welcome(self):
		sub_w = Toplevel(self.main_win)
		sub_w.title('欢迎访问')
		self.set_win_geometry(sub_w, 350, 200, 4)

		txt = '欢迎使用' + SOFTWARE_NAME
		Label(sub_w, text = txt, anchor = 'center', fg = 'blue').place(x = 95, y = 40, width = 100, height = 25)

	def menu_item_readme(self):
		sub_w = Toplevel(self.main_win)
		sub_w.title('使用说明')
		self.set_win_geometry(sub_w, 450, 270, 4)

		t = Text(sub_w, height = 6, width=70, fg = 'blue')
		t.place(x = 10, y = 10, width = 430, height = 250)
		t.bind("<KeyPress>", lambda e : "break")
		t.insert(END, '1. 建立连接' + '\n')
		t.insert(END, '   选择菜单 连接->建立连接，输入IP或者主机名，点击连接' + '\n')
		t.insert(END, '2. 断开连接' + '\n')
		t.insert(END, '   点击菜单 连接->建立连接，点击断开' + '\n')
		t.insert(END, '3. 设置昵称' + '\n')
		t.insert(END, '   点击菜单 设置->我的昵称，输入昵称' + '\n')

	def menu_item_AT_usage(self):
		sub_w = Toplevel(self.main_win)
		sub_w.title('AT命令')
		self.set_win_geometry(sub_w, 450, 350, 4)

		t = Text(sub_w, height = 6, width=70, fg = 'blue')
		t.place(x = 10, y = 10, width = 430, height = 330)
		t.bind("<KeyPress>", lambda e : "break")
		t.insert(END, '输入 ATCMD' + '\n')

	def menu_item_about(self):
		sub_w = Toplevel(self.main_win)
		sub_w.title('关于' + SOFTWARE_NAME)
		self.set_win_geometry(sub_w, 350, 200, 4)

		t = Text(sub_w, height = 6, width=70, fg = 'blue')
		t.place(x = 10, y = 10, width = 330, height = 180)
		t.bind("<KeyPress>", lambda e : "break")
		t.insert(END, '\n')
		t.insert(END, '\n')
		t.insert(END, 'Version:' + VERSION + '\n')
		t.insert(END, '\n')
		t.insert(END, 'Author: 59089403@qq.com' + '\n')
		t.insert(END, '\n')
		t.insert(END, '@All rights reserved' + '\n')

	def mode_setting_save(self):
		self.mode = self.mode_var.get()
		self.sys_config.set('mode', self.mode)

	def zero_cal_setting_save(self):
		adc0_standard = self.zero_cal_adc0_standard.get()
		self.handle_data_from_ui('zero_cal_adc0_standard', adc0_standard)
		self.sys_config.set('zero_cal_adc0_standard', adc0_standard)

	def temp_cal_setting_save(self):
		threshold = self.adc0_stable_threshold.get()
		self.handle_data_from_ui('adc0_stable_threshold', threshold)
		self.sys_config.set('adc0_stable_threshold', threshold)

	def ui_append_dialog(self, type, msg):
		if type == 'to_dut':
			sender = 'PC' + ' ['+ time.strftime('%H:%M:%S',time.localtime(time.time())) + ']:'
			color = 'fg_darkred'
		elif type == 'from_dut':
			sender = 'DUT' + ' ['+ time.strftime('%H:%M:%S',time.localtime(time.time())) + ']:'
			color = 'fg_blue'
		elif type == 'to_std':
			sender = 'ts' + ' ['+ time.strftime('%H:%M:%S',time.localtime(time.time())) + ']:'
			color = 'fg_blue'
		elif type == 'from_std':
			sender = 'fs' + ' ['+ time.strftime('%H:%M:%S',time.localtime(time.time())) + ']:'
			color = 'fg_blue'
		else:
			sender = 'unknown'
			color = 'fg_blue'

		if type == 'to_std' or type == 'from_std':
			self.text_dialog.insert(END, sender + ' ')
			self.text_dialog.insert(END, msg, color)
		else:
			self.text_dialog.insert(END, msg, color)

		self.text_dialog.see(END)

	def remove_duplicated_cr(self, cmd):
		if cmd.endswith('\n\r\n'):
			return cmd[:-2]
		elif cmd.endswith('\n\n'):
			return cmd[:-1]
		elif cmd.endswith('\n'):
			return cmd
		else:
			return cmd

	def remove_cr(self, cmd):
		if cmd.endswith('\n\n'):
			return cmd[:-2]
		elif cmd.endswith('\n'):
			return cmd[:-1]
		else:
			return cmd

	def on_send_msg(self, x):
		data = self.text_input.get(0.0, END)
		data = data.encode('utf8')
		data = self.remove_duplicated_cr(data)

		# only <\n> input, exit
		if not data:
			self.text_input.delete(0.0, END)
			return

		# move msg from text_input to text_history
		self.text_input.delete(0.0, END)
		self.ui_append_dialog('local', data)

		# send cmd to board
		# data = self.remove_cr(data)
		self.handle_data_from_ui('send_to_dut', data)

	def start_test(self):
		self.handle_data_from_ui('start_test', None)

	def start_zero_cal(self):
		self.handle_data_from_ui('start_zero_cal', None)

	def read_zero_cal(self):
		self.handle_data_from_ui('read_zero_cal', None)

	def clear_zero_cal(self):
		self.handle_data_from_ui('clear_zero_cal', None)

	def start_low_temp_cal(self):
		self.handle_data_from_ui('start_low_temp_cal', None)

	def read_low_temp_cal(self):
		self.handle_data_from_ui('read_low_temp_cal', None)

	def clear_low_temp_cal(self):
		self.handle_data_from_ui('clear_low_temp_cal', None)

	def start_high_temp_cal(self):
		self.handle_data_from_ui('start_high_temp_cal', None)

	def read_high_temp_cal(self):
		self.handle_data_from_ui('read_high_temp_cal', None)

	def clear_high_temp_cal(self):
		self.handle_data_from_ui('clear_high_temp_cal', None)

	def start_temp_cal(self):
		self.handle_data_from_ui('start_temp_cal', None)

	def read_temp_cal(self):
		self.handle_data_from_ui('read_temp_cal', None)

	def clear_temp_cal(self):
		self.handle_data_from_ui('clear_temp_cal', None)

	def update_ui(self, type, data):
		if type == 'uart_dut_port': # set uart port
			self.uart_dut_port_var.set(data)

		elif type == 'uart_dut_status':
			if data == 'CONNECT':
				self.uart_dut_status_var.set('连接')
				# self.uart_dut_status.config(fg = 'DarkBlue')
			elif data == 'DISCONNECT':
				self.uart_dut_status_var.set('断开')
				# self.uart_dut_status.config(fg = 'Red')

		elif type == 'uart_std_port': # set uart port
			self.uart_std_port_var.set(data)

		elif type == 'uart_std_status':
			if data == 'CONNECT':
				self.uart_std_status_var.set('连接')
				# self.uart_std_status.config(fg = 'DarkBlue')
			elif data == 'DISCONNECT':
				self.uart_std_status_var.set('断开')
				# self.uart_std_status.config(fg = 'Red')

		elif type == 'zero_cal_result':
			self.hw_adc0_before_cal_var.set(data['hw_adc0_before_cal'])
			self.adc0_delta_before_cal_var.set(data['adc0_delta_before_cal'])
			self.adc0_before_cal_var.set(data['adc0_before_cal'])
			self.Rt_before_cal_var.set(data['Rt_before_cal'])
			self.Temp_before_cal_var.set(data['temp_before_cal'])

			self.hw_adc0_after_cal_var.set(data['hw_adc0_after_cal'])
			self.adc0_delta_after_cal_var.set(data['adc0_delta_after_cal'])
			self.adc0_after_cal_var.set(data['adc0_after_cal'])
			self.Rt_after_cal_var.set(data['Rt_after_cal'])
			self.temp_after_cal_var.set(data['temp_after_cal'])

		elif type == 'low_temp_cal_result':
			self.low_temp_cal_adc_var.set(data['adc0'])
			self.low_temp_cal_R_low_var.set(data['R_low'])
			self.low_temp_cal_t_low_var.set(data['t_low'])
			self.low_temp_cal_t_std_var.set(data['t_std'])
			self.low_temp_cal_t_delta_var.set(data['t_delta'])

		elif type == 'high_temp_cal_result':
			self.high_temp_cal_adc_var.set(data['adc0'])
			self.high_temp_cal_R_high_var.set(data['R_high'])
			self.high_temp_cal_t_high_var.set(data['t_high'])
			self.high_temp_cal_t_std_var.set(data['t_std'])
			self.high_temp_cal_t_delta_var.set(data['t_delta'])

		elif type == 'temp_cal_result':
			self.temp_cal_adc_var.set(data['adc0'])
			self.temp_cal_B_delta_var.set(data['B_delta'])
			self.temp_cal_R25_delta_var.set(data['R25_delta'])
			self.temp_cal_temp_var.set(data['temp'])
			self.temp_cal_t_std_var.set(data['t_std'])
			self.temp_cal_t_delta_var.set(data['t_delta'])

		elif type == 'message_box_info':
			tkMessageBox.showinfo(data['title'], data['RESULT'])

		elif type == 'message_box_err':
			tkMessageBox.showerror(data['title'], data['RESULT'])

		else:
			self.log.write('%s update_ui(): unknown type %s', MODULE, type)

	def uart_dut_port_connect(self):
		self.handle_data_from_ui('uart_dut_port_connect', self.uart_dut_port_var.get())

	def uart_dut_port_connect2(self, x):
		self.uart_dut_port_connect()

	def uart_dut_port_disconnect(self):
		self.handle_data_from_ui('uart_dut_port_disconnect', self.uart_dut_port_var.get())

	def uart_std_port_connect(self):
		self.handle_data_from_ui('uart_std_port_connect', self.uart_std_port_var.get())

	def uart_std_port_connect2(self, x):
		self.uart_std_port_connect()

	def uart_std_port_disconnect(self):
		self.handle_data_from_ui('uart_std_port_disconnect', self.uart_std_port_var.get())

	def set_win_geometry(self, win, width, height, div):
		#win.update()
		win.resizable(False, False)
		cur_width = win.winfo_reqwidth()
		cur_height = win.winfo_height()
		screen_width, screen_height = win.maxsize()
		pos = '%dx%d+%d+%d' %(width, height, (screen_width)/ div, (screen_height)/ div)
		win.geometry(pos)

	def exit(self):
		# self.main_win.destroy()
		# self.com_dut_status_var.__del__()
		pass

	def is_window_ok(self):
		return self.window_ok

if __name__ == '__main__':
	ui = Ui()


