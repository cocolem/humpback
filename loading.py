import os.path

PySettingObject = type(os)

class PySetting(object):
	def __init__(self):
		# Save configure as buffer
		self.dict = {} # Dict type
		self.config = {} # Normal type

	'''
		This method is only support dictionary configration.
		Just support a single dictionary in a file.
		The format:
		{
			"a" : "val_a" ,
			"b" : "val_b" ,
			"c" : "val_c"  ,
			"d" : [0, 1, 2, 3]
		}
	'''
	def LoadConfig(self, fullpath):
		# Be sure to get fullpath
		if not os.path.isabs(fullpath):
			fullpath = os.path.abspath(fullpath)
		# Search module name
		fname = os.path.basename(fullpath)
		if fname in self.dict:
			return self.dict[fname]
		# Get the context
		try:
			config = open(fullpath).read()
		except IOError:
			raise IOError, 'No such file: %s' % fullpath

		# Check syntax
		try:
			m = eval(config)
		except SyntaxError:
			raise SyntaxError, 'invalid syntax' 

		# Put in dict
		self.dict[fname] = m

		return m

	def UnloadConfig(self, fullpath):
		if not os.path.isabs(fullpath):
			# Get module fullpath
			fullpath = os.path.abspath(fullpath)
		fname = os.path.basename(fullpath)
		if fname in self.dict:
			del self.dict[fname]

		return None

	'''
		This method is only support object-oriented configration.
		Like the format below:
		A = {
			"a" : "val_a" ,
			"b" : "val_b" ,
			"c" : "val_c"  ,
			"d" : [0, 1, 2, 3]
		}
	'''
	def LoadSimpleConfig(self, fullpath):
		# Be sure to get fullpath
		if not os.path.isabs(fullpath):
			fullpath = os.path.abspath(fullpath)
		# Search module name
		fname = os.path.basename(fullpath)
		if fname in self.config:
			return self.config[fname]
		# Get the context
		try:
			config = open(fullpath).read()
		except IOError:
			raise IOError, 'No such file: %s' % fullpath

		# Excute setting in dict-target
		m = PySettingObject(fname)
		exec(compile(config, fname, 'exec')) in m.__dict__

		# Put in config buffer
		self.config[fname] = m

		return m

	def UnloadSimpleConfig(self, fullpath):
		if not os.path.isabs(fullpath):
			# Get module fullpath
			fullpath = os.path.abspath(fullpath)
		fname = os.path.basename(fullpath)
		if fname in self.config:
			del self.config[fname]

		return None
