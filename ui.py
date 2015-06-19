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
VERSION = 'v0.1'

class Ui:

	def __init__(self, log, handle_data_from_ui):
		self.window_ok = False

		self.log = log

		self.handle_data_from_ui = handle_data_from_ui

		# get configs


		# launch UI
		self.ui_mainloop_thread = thread.start_new_thread(self.lanuch_ui, (None, ))

	def lanuch_ui(self, x):
		self.log.write('%s launch ui', MODULE)

		# create main window
		self.main_win = main_win = Tk()
		main_win.title(SOFTWARE_NAME + VERSION)
		self.set_win_geometry(main_win, 900, 600, 5)

		# font
		self.font_dialog = tkFont.Font(family = '宋体', size = 11, weight = "bold")
		self.font_input = tkFont.Font(family = '宋体', size = 11, weight = "bold")

		# String var
		self.indicating_bar_var = StringVar()

		self.uart_dut_port_var = StringVar()
		self.uart_dut_status_var = StringVar()
		self.uart_std_port_var = StringVar()
		self.uart_std_status_var = StringVar()

		self.self_zero_adc = StringVar()

		# create menu
		menu_base = Menu(main_win)
		main_win.config(menu = menu_base)

		menu_cascade_set = Menu(menu_base, tearoff = 0)
		menu_cascade_set.add_separator()
		menu_cascade_set.add_command(label = "退出", command = main_win.quit)
		menu_base.add_cascade(label="设置", menu = menu_cascade_set)
		
		menu_cascade_help = Menu(menu_base, tearoff=0)
		menu_cascade_help.add_command(label = "欢迎", command = self.menu_item_welcome)
		menu_cascade_help.add_separator()
		menu_cascade_help.add_command(label = "使用说明", command = self.menu_item_readme)
		menu_cascade_help.add_separator()
		menu_cascade_help.add_command(label = "关于" + SOFTWARE_NAME, command = self.menu_item_about)
		menu_base.add_cascade(label="帮助", menu = menu_cascade_help)

		# text history
		self.scrollbar = Scrollbar(main_win)
		self.text_dialog = self.text_dialog = Text(main_win, height=20, width=70,
									yscrollcommand = self.scrollbar.set, font = self.font_dialog, bg = 'gray')
		self.text_dialog.place(x = 10, y = 20, width = 560, height = 400)
		#t.bind("<KeyPress>", lambda e : "break")
		self.scrollbar.config(command = self.text_dialog.yview)
		self.scrollbar.place(x = 570, y = 20, width = 20, height = 400)

		self.text_dialog.tag_config('fg_blue',foreground = 'blue') # create tag
		self.text_dialog.tag_config('fg_darkred',foreground = 'darkred')

		# indicating bar(such as: typing)
		l = Label(main_win, textvariable = self.indicating_bar_var, anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 10, y = 420, width = 300, height = 25)

		# text input
		self.text_input = Text(main_win, height = 6, width=70, font = self.font_input)
		self.text_input.place(x = 10, y = 445, width = 580, height = 135)
		#t.bind("<Return>", self.on_send_msg)
		self.text_input.bind("<KeyRelease-Return>", self.on_send_msg)

		# seperator
		l = Label(main_win, text = '-----------------------串口信息-----------------------', anchor = 'w')
		l.config(fg = 'DarkGreen')
		l.place(x = 600, y = 10, width = 300, height = 25)

		# UART DUT
		l = Label(main_win, text = 'DUT', anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 600, y = 40, width = 30, height = 25)

		self.uart_dut = Entry(main_win, width = 10, textvariable = self.uart_dut_port_var)
		self.uart_dut.place(x = 640, y = 40, width = 90, height = 25)
		self.uart_dut.bind("<KeyRelease-Return>", self.uart_dut_port_changed)

		l = Label(main_win, textvariable = self.uart_dut_status_var, anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 750, y = 40, width = 80, height = 25)

		# UART STD
		l = Label(main_win, text = 'STD', anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 600, y = 70, width = 30, height = 25)

		self.uart_std = Entry(main_win, width = 10, textvariable = self.uart_std_port_var)
		self.uart_std.place(x = 640, y = 70, width = 90, height = 25)

		l = Label(main_win, textvariable = self.uart_std_status_var, anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 750, y = 70, width = 70, height = 25)
		self.uart_std_status_var.set('N/A')
		l.config(fg = 'Grey')

		# seperator
		l = Label(main_win, text = '-----------------------零点校准-----------------------', anchor = 'w')
		l.config(fg = 'DarkGreen')
		l.place(x = 600, y = 100, width = 300, height = 25)

		# ADC
		l = Label(main_win, text = 'ADC ', anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 600, y = 130, width = 30, height = 25)

		l = Label(main_win, textvariable = self.self_zero_adc, anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 670, y = 130, width = 50, height = 25)
		self.self_zero_adc.set('1000')

		l = Label(main_win, text = 'ADC偏差 ', anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 600, y = 160, width = 60, height = 25)

		l = Label(main_win, textvariable = self.self_zero_adc, anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 670, y = 160, width = 50, height = 25)
		self.self_zero_adc.set('1000')

		# R
		l = Label(main_win, text = '电阻值 ', anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 750, y = 130, width = 50, height = 25)

		l = Label(main_win, textvariable = self.self_zero_adc, anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 820, y = 130, width = 50, height = 25)
		self.self_zero_adc.set('1000')

		l = Label(main_win, text = '电阻偏差 ', anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 750, y = 160, width = 60, height = 25)

		l = Label(main_win, textvariable = self.self_zero_adc, anchor = 'w')
		l.config(fg = 'DarkBlue')
		l.place(x = 820, y = 160, width = 50, height = 25)
		self.self_zero_adc.set('1000')

		self.button_zero_cal = Button(main_win, text = '开始零点校准', command = self.start_zero_cal, width = 10)
		# self.button_zero_cal['state'] = 'disabled'	if self.net.net_connected() else 'normal'
		self.button_zero_cal.place(x = 700, y = 190, width = 80, height = 35)

		# seperator
		l = Label(main_win, text = '-----------------------低温校准-----------------------', anchor = 'w')
		l.config(fg = 'DarkGreen')
		l.place(x = 600, y = 240, width = 300, height = 25)

		# seperator
		l = Label(main_win, text = '-----------------------高温校准-----------------------', anchor = 'w')
		l.config(fg = 'DarkGreen')
		l.place(x = 600, y = 400, width = 300, height = 25)

		# Start main window
		self.window_ok = True
		self.main_win.mainloop()
		# when running here, the main window is died
		self.window_ok = False


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

	def ui_append_dialog(self, type, msg):
		if type == 'local':
			sender = 'PC' + ' ['+ time.strftime('%H:%M:%S',time.localtime(time.time())) + ']:'
			color = 'fg_blue'
		else:
			sender = 'Board' + ' ['+ time.strftime('%H:%M:%S',time.localtime(time.time())) + ']:'
			color = 'fg_darkred'

		self.text_dialog.insert(END, sender + '\n')
		# self.text_dialog.insert(END, msg + '\n', color)
		self.text_dialog.insert(END, msg, color)
		self.text_dialog.see(END)

	def strip_end(self, cmd):
		if cmd.endswith('\n\n'):
			# return cmd[:-2]
			return cmd[:-1]
		elif cmd.endswith('\n'):
			# return cmd[:-1]
			return cmd
		else:
			return cmd


	def on_send_msg(self, x):
		data = self.text_input.get(0.0, END)
		data = self.strip_end(data)

		# only <\n> input, exit
		if not data:
			self.text_input.delete(0.0, END)
			return

		# send cmd to board
		self.handle_data_from_ui('send_to_dut', data)

		# move msg from text_input to text_history
		self.text_input.delete(0.0, END)
		self.ui_append_dialog('local', data)

	def start_zero_cal(self):
		pass


	def update_ui(self, type, data):
		if type == 'uart_dut_port': # set uart port
			self.uart_dut_port_var.set(data)
		elif type == 'uart_dut_status':
			self.uart_dut_status_var.set(data)
		elif type == 'uart_std_status':
			self.uart_std_status_var.set(data)
		else:
			self.log.write('%s update_ui(): unknown type %s', MODULE, type)

	def uart_dut_port_changed(self, x):
		self.handle_data_from_ui('uart_dut_port_changed', self.uart_dut_port_var.get())

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


