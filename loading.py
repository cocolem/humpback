import os.path

# Save configure as buffer
Modules = {}

class PySettingObject(object):
	def __init__(self, name):
		self.name = name 

	def __name__(self):
		return self.name

	def __getitem__(self, key):
		return self.__dict__[key]

	def __setitem__(self, key, value):
		self.__dict__[key] = value

class PySetting(object):
	@staticmethod
	def load(fullpath):
		# Be sure to get fullpath
		if not os.path.isabs(fullpath):
			fullpath = os.path.abspath(fullpath)
		# Get the context
		try:
			config = open(fullpath).read()
		except IOError:
			raise IOError, 'No such file: %s' % fullpath
		# Module name
		fname = os.path.basename(fullpath)
		if fname in Modules:
			return Modules[fname]

		m = PySettingObject(fname)
		exec(compile(config, fname, 'exec')) in m.__dict__
		Modules[fname] = m

		return m

	@staticmethod
	def unload(fullpath):
		if not os.path.isabs(fullpath):
			# Get module fullpath
			fullpath = os.path.abspath(fullpath)
			fname = os.path.basename(fullpath)
		else:
			fname = os.path.basename(fullpath)
		if fname in Modules:
			del Modules[fname]

		return None

