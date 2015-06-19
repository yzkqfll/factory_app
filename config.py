# -*- coding:utf-8 -*-
#!/usr/bin/python

import ConfigParser

MODULE = '[config]'

FILENAME = 'cfg'

class Config:

	def __init__(self, log):
		self.log = log

	def __exit__(self):
		pass

	def get(self, item):
		config = ConfigParser.ConfigParser()
		#config.readfp('.conf',"rb")
		config.read(FILENAME)
		try:
			c = config.get("ALL", item)
		except:
			c = ''
			pass

		# self.log.write('%s get "%s" as "%s"', MODULE, item, c)

		return c

	def set(self, item, val):
		# self.log.write('%s set "%s" as "%s"', MODULE, item, val)

		config = ConfigParser.ConfigParser()
		#config.readfp('.conf',"rb")
		config.read(FILENAME)

		# config.set("global", type, val.encode('utf8'))
		config.set("ALL", item, val)
		config.write(open(FILENAME, "w"))
