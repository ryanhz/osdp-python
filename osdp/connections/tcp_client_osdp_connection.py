import socket
import sys


class TcpClientOsdpConnection(OsdpConnection):
	
	def __init__(self, server: str, port_number: int):
		self._server = server
		self._port_number = port_number
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(2)
		self.is_connected = False

	@property
	def baud_rate(self) -> int:
		return 9600

	@property
	def is_open(self) -> bool:
		return self.is_connected

	def open(self):
		server_address = (self._server, self._port_number)
		self.sock.connect(server_address)
		self.is_connected = True

	def close(self):
		self.sock.close()
		self.is_connected = False

	def write(self, buf: bytes):
		try:
			self.sock.send(buf)
		except socket.timeout as e:
			self.is_connected = False		

	def read(self, size: int=1) -> bytes:
		try:
			return self.sock.recv(size)
		except socket.timeout as e:
			self.is_connected = False
		return b''