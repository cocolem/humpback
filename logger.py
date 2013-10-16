#!/usr/local/bin/python

### Import Module ###
from sys import stdout,stderr
from time import gmtime
import os
import logging

# Define all level same as logging's level
LogLevelNone = 0
LogLevelDebug = 10
LogLevelInfo = 20
LogLevelWarning = 30
LogLevelError = 40
LogLevelCrit = 50

### Class Define ###
class Logger(object):
	'''
	This is a simple encapsulation interface for logging.

	Sample:
	from logger import Logger
	l = Logger('/tmp/log')
	l = set_level_info() 
	l.p_info('hello world !')

	'''

	TimeFormat = '%Y-%b-%d %H:%M:%S'
	LogFormat = '[%(levelname)s][%(asctime)s] %(message)s'

	def __init__(self, fullpath):
		self.fullpath = fullpath
		self.logger = self._LoggerSetup()

	def _LoggerFormat(self):
		return logging.Formatter(self.LogFormat, self.TimeFormat)	

	def _SreamHandlerSetup(self, std = stdout or stderr):
		streamhandler = logging.StreamHandler(std)
		streamhandler.setFormatter(self._LoggerFormat())
		# Set output format
		return streamhandler

	def _FileHandlerSetup(self):
		if not os.path.isabs(self.fullpath):
			self.fullpath = os.path.abspath(self.fullpath)
		tempdir = os.path.dirname(self.fullpath)
		# Check whether path is exist ?
		if not os.path.exists(tempdir):
			os.mkdir(tempdir)

		filehandler = logging.FileHandler(self.fullpath)
		filehandler.setFormatter(self._LoggerFormat())
		return filehandler

	def _LoggerSetup(self):
		logger = logging.getLogger()
		logger.setLevel(LogLevelNone)
		# Set output format
		streamhandler = self._SreamHandlerSetup(stdout)
		logger.addHandler(streamhandler)
		# Set logfile format
		filehandler = self._FileHandlerSetup()
		logger.addHandler(filehandler)
		return logger

	@staticmethod
	def printf(format, *args):
		stdout.write(format % args)

	@staticmethod
	def perror(format, *args):
		stderr.write(format % args)

	def p_info(self, msg, *args, **kwargs):
		self.logger.info(msg, *args, **kwargs)

	def p_debug(self, msg, *args, **kwargs):
		self.logger.debug(msg, *args, **kwargs)

	def p_warning(self, msg, *args, **kwargs):
		self.logger.warning(msg, *args, **kwargs)

	def p_error(self, msg, *args, **kwargs):
		self.logger.error(msg, *args, **kwargs)

	def p_crit(self, msg, *args, **kwargs):
		self.logger.critical(msg, *args, **kwargs)

	def set_level_none(self):
		self.logger.setLevel(LogLevelNone)

	def set_level_debug(self):
		self.logger.setLevel(LogLevelDebug)

	def set_level_info(self):
		self.logger.setLevel(LogLevelInfo)

	def set_level_warning(self):
		self.logger.setLevel(LogLevelWarning)

	def set_level_error(self):
		self.logger.setLevel(LogLevelError)

	def set_level_crit(self):
		self.logger.setLevel(LogLevelCrit)

### Unit Test ###
'''
p = Logger('Logger_config.py')
p.printf('Hello World %s\n' , 'kkk')
p.printf('Hello World\n')
p.p_info('Hello World %s' , 'kkk')
p.p_info('Hello World')
'''
