
### Import Module ###
from sys import stdout,stderr
from time import gmtime
import os
import logging
#from inspect import stack

### Local Setting ###
LoggerSetting = {
	'FileSetting' : {
		'TempDirectory' : '/tmp/mylog',
		'TempPrefix' : 'track',	
		'TempSuffix' : '.log'
	},
	'TimeFormat' : '%Y-%b-%d %H:%M:%S',
}

### Class Define ###
class Logger(object):
	'''
	This is a simple encapsulation interface for logging.

	Sample:
	from logger import Logger as Logger
	Logger.set_level_info()

	def foo():
		Logger.p_info('hello world !')
	'''

	# Define all level same as logging's level
	LogLevelNone = 0
	LogLevelDebug = 10
	LogLevelInfo = 20
	LogLevelWarning = 30
	LogLevelError = 40
	LogLevelCrit = 50

	LogYear = gmtime().tm_year
	LogMonth = gmtime().tm_mon
	LogMday = gmtime().tm_mday

	LogFormat = '[%(levelname)s][%(asctime)s] %(message)s'
#	LogFormat = '[%(levelname)s][%(asctime)s]['+ stack()[3][3] +'] %(message)s'

	def __init__(self, setting = LoggerSetting):
		self.setting = setting
		#! Check Input Setting First
		self.logger = self._LoggerSetup()

	def _LoggerFormat(self):
		timeformat = self.setting['TimeFormat']
		logformat = self.LogFormat
		return logging.Formatter(logformat, timeformat)	

	def _SreamHandlerSetup(self):
		streamhandler = logging.StreamHandler(stdout)
		#streamhandler = logging.StreamHandler(stderr)
		streamhandler.setFormatter(self._LoggerFormat())
		# Set output format
		return streamhandler

	def _FileHandlerSetup(self):
		# Read file setting 
		tempdir = self.setting['FileSetting']['TempDirectory']
		tempprefix = self.setting['FileSetting']['TempPrefix']
		tempsuffix = self.setting['FileSetting']['TempSuffix']
		# Check whether path is exist ?
		if not os.path.exists(tempdir):
			os.mkdir(tempdir)

		filestream = tempdir +  '/' + tempprefix + str(Logger.LogYear) + '-' + str(Logger.LogMonth) + '-' + str(Logger.LogMday) + tempsuffix

		filehandler = logging.FileHandler(filestream)
		filehandler.setFormatter(self._LoggerFormat())
		return filehandler

	def _LoggerSetup(self):
		logger = logging.getLogger()
		logger.setLevel(self.LogLevelNone)
		# Set output format
		streamhandler = self._SreamHandlerSetup()
		logger.addHandler(streamhandler)
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

	def set_level_debug(self):
		self.logger.setLevel(self.LogLevelDebug)

	def set_level_info(self):
		self.logger.setLevel(self.LogLevelInfo)

	def set_level_warning(self):
		self.logger.setLevel(self.LogLevelWarning)

	def set_level_error(self):
		self.logger.setLevel(self.LogLevelError)

	def set_level_crit(self):
		self.logger.setLevel(self.LogLevelCrit)

### Unit Test ###
'''
p = Logger()
p.printf('Hello World %s\n' , 'kkk')
p.printf('Hello World\n')
p.p_info('Hello World %s' , 'kkk')
p.p_info('Hello World')
'''