from abc import ABC, abstractmethod 

class OsdpConnection(ABC):

	@property
	@abstractmethod
	def baud_rate(self) -> int:
		pass

	@property
	@abstractmethod
	def is_open(self) -> bool:
		pass

	@abstractmethod
	def open(self):
		pass

	@abstractmethod
	def close(self):
		pass

	@abstractmethod
	def write(self, buf: bytes):
		pass

	@abstractmethod
	def read(self, size: int=1) -> bytes:
		pass