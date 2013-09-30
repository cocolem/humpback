
from humpback.module.logger import Logger as Lg
from Queue import Queue, Empty

try:
	import threading #Py2
except:
	import _thread as threading #Py3

try:
	import stackless #Stackless Module

	class Worker(object):

		channel = stackless.channel()

		def __init__(self, pool):
			self.__pool = pool
			self.__id = self.__pool._work_id()
			self.__mutex = self.__pool.lock
			stackless.tasklet(self.run)()

		def wakeup(self):
			self.channel.send("start")

		def start(self):
			stackless.run()

		def stop(self):
			self.__running = False

		def index(self):
			return self.__id

		def run(self):
			with self.__pool.semaphore:
				self.__running = True
				Lg.p_info('Worker %s start to do jobs !' % (self.__id) )
				while self.__running:
					event = self.__pool.pop()
					if event is not None:
						Lg.p_info('Worker %s get the job:%d !' % (self.__id, event.id()) )
						self.__mutex.acquire()
						event.execute()
						self.__mutex.release()
					else:
						try:
							self.__pool._del_worker(self)
							self.__pool._add_wait_worker(self)
						except ValueError:	
							Lg.p_info('Worker %s already move to the wait queue !' % (self.__id) )
						Lg.p_info('Worker %s no job !!!' % (self.__id) )
						self.channel.receive()

except:
	class Worker(threading.Thread):

		signal = threading.Event()

		def __init__(self, pool):
			super(Worker, self).__init__()
			self.__pool = pool
			self.__id = self.__pool._work_id()
			self.__mutex = self.__pool.lock
			self.setDaemon(True)

		def wakeup(self):
			self.signal.set()

		def start(self):
			super(Worker, self).start()

		def stop(self):
			self.__running = False

		def index(self):
			return self.__id

		def run(self):
			with self.__pool.semaphore:
				self.__running = True
				Lg.p_info('Worker %s start to do jobs !' % (self.__id) )
				while self.__running:
					event = self.__pool.pop()
					if event is not None:
						Lg.p_info('Worker %s get the job:%d !' % (self.__id, event.id()))
						self.__mutex.acquire()
						event.execute()
						self.__mutex.release()
					else:
						try:
							self.__pool._del_worker(self)
							self.__pool._add_wait_worker(self)
						except ValueError:	
							Lg.p_info('Worker %s already move to the wait queue !' % (self.__id) )
						Lg.p_info('Worker %s no job !!!' % (self.__id) )
						self.signal.wait()

class Event(object):
	'''
	An simple event including function name, arguments, 
	if necessary check return value by callback.
	'''
	def __init__(self, idx, callback, func, *args, **kwargs):
		self.__id = idx
		self.__callback = callback
		self.__func = func
		self.__args = args
		self.__kwargs = kwargs
		Lg.p_debug('funcname:%s, argument:%s, dict:%s, callback:%s' % (self.__func, self.__args, self.__kwargs, self.__callback))

	def id(self):
		return self.__id

	def execute(self):
		try:
			ret = self.__func(*self.__args, **self.__kwargs)
		except Exception, error:
			Lg.p_warning('TaskPool event raise a exception:[%s]' % (error) )
			return error

		try:
			if self.__callback != None:
				self.__callback(ret)
		except Exception, error:
			Lg.p_warning('TaskPool callback raise a exception:[%s]' % (error) )

class TaskPool(object):

	semaphore = None
	lock = threading.RLock()

	def __init__(self, maximun = 1024, minimum = 10):
		self.__current = threading.local()
		self.__max = maximun
		self.__min = minimum
		self.__event_index = 0
		self.__events = Queue()
		self.__worker_index = 0
		self.__workers = []
		self.__wait_workers = []

	'''
	'''
	def push(self, id, callback, func, *args, **kwargs):
		event = Event(id, callback, func, *args, **kwargs)
		self.__events.put(event)
		self.__event_index += 1
		self._call_wait_worket()
		return event

	'''
	'''
	def pop(self):
		try:
			return self.__events.get(block = False)
		except Empty:
			return None

	def remove(self, event):
		self.__events.remove(event)

	'''
	'''
	def clear(self):
		with TaskPool.lock:
			self.__events.clear()

	'''
	'''
	def isempty(self):
		return self.__events is not None and True or False

	'''
	'''
	def close(self):
		self.clear()
		self.cleanall()

	def wait_worker_count(self):
		return len(self.__wait_workers)

	def _work_id(self):
		return self.__worker_index

	def _add_wait_worker(self, worker):
		self.__wait_workers.append(worker)

	def _del_wait_worker(self, worker):
		self.__wait_workers.remove(worker)

	def _call_wait_worket(self):
		if not self.__workers:
			try:
				work = self.__wait_workers.pop()
				work.wakeup()
				self._add_worker(worker)
			except IndexError:
				pass

	def _clean_wait_workers(self):
		Lg.p_info('Wait worker count:%d and begin to clear !' % (self.wait_worker_count()))
		while self.__wait_workers:
			worker = self.__wait_workers.pop()
			worker.stop()
			Lg.p_info('Worker count:%s, index:%s be free !' % (self.count(), worker.index()))

	def _add_worker(self, worker):
		self.__workers.append(worker)

	def _del_worker(self, worker):
		self.__workers.remove(worker)

	def _clean_workers(self):
		Lg.p_info('Live worker count:%d and begin to clear !' % (self.count() - self.wait_worker_count()))
		while self.__workers:
			worker = self.__workers.pop()
			worker.stop()
			Lg.p_info('Worker count:%s, index:%s be free !' % (self.count(), worker.index()))

	'''
	'''
	def count(self):
		return (len(self.__workers) + len(self.__wait_workers))

	'''
	'''
	def new(self):
		with TaskPool.lock:
			self.__worker_index += 1
			worker = Worker(self)
			self._add_worker(worker)

	def add(self, count = 1):
		for i in xrange(0, count):
			self.new()

	def start(self):
		TaskPool.semaphore = threading.Semaphore(self.__worker_index)
		for worker in self.__wait_workers:
			worker.wakeup()
		for worker in  self.__workers :
			worker.start()
	'''
	'''
	def autoclean(self):
		while self.count() > self.__min and self.wait_worker_count() !=0:
			self._clean_wait_workers()

	'''
	'''
	def cleanall(self):
		self._clean_workers()
		self._clean_wait_workers()

	def wait_all_complete(self):
		while True:
			if not self.__workers: 
				break
