
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from osdp import *
import time
import logging
import random

log = logging.getLogger('osdp')

class PuppetOsdpConnection(OsdpConnection):
	
	def __init__(self):
		self._open = False
		self.should_reply = b''

	@property
	def baud_rate(self) -> int:
		return 9600

	@property
	def is_open(self) -> bool:
		return self._open

	def open(self):
		self._open = True

	def close(self):
		self._open = False

	def write(self, buf: bytes):
		if self._open:
			log.debug("Written: %s", buf)
		else:
			raise Exception("Connection is closed while writing")

	def read(self, size: int=1) -> bytes:
		time.sleep(random.random()*0.5)
		taken = self.should_reply[:size]
		remain = self.should_reply[size:]
		self.should_reply = remain
		return taken