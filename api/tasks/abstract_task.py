from abc import ABC, abstractmethod

class AbstractTask(ABC):
	@abstractmethod
	def perform_task(self):
		pass
