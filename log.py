# -*- coding:utf-8 -*-
#!/usr/bin/python

import sys
import time


'''
there are 3 methods to print:
	print '%s launch ui' %(print_str)
	self.l.log_write('%s launch ui', print_str)
	self.l.log_write('%s launch ui' %(print_str))
'''

class Log():
	ori_fd = None
	file_fd = None
	
	def __init__(self):		
		file_name = '.log'		
		self.file_fd = open(file_name,'ab')
		
		self.ori_fd = sys.stdout		
		#sys.stdout = file_fd

	def __exit__(self):
		if self.file_fd:
			self.file_fd.close()
			
		if self.ori_fd:			
			sys.stdout = self.ori_fd
	
	def write(self, fmt, *args):
		print fmt %(args)

		# Way 1
		#print >> fd, '%s' %('123')
		# fmt = '[%s]' + fmt
		# new_args = (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), ) + args
		#print >> self.file_fd, fmt %(new_args)
		# print fmt %(new_args)
		
		# Way 2
		#print fmt %(args)

if __name__ == '__main__':			
	log = Log()
	log.write('test %s %d', 'abc', 1)
