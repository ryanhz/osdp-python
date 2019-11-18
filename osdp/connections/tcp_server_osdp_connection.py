import socket
import sys


class TcpServerOsdpConnection(OsdpConnection):
	
	def __init__(self, port_number: int):
		self._port_number = port_number
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(2)
		server_address = ('0.0.0.0', self._port_number)
		self.sock.bind(server_address)
		self.connection = None

	@property
	def baud_rate(self) -> int:
		return 9600

	@property
	def is_open(self) -> bool:
		return self.connection is not None

	def open(self):
		self.sock.listen(1)
		self.connection, _ = self.sock.accept()

	def close(self):
		self.connection.close()
		self.connection = None

	def write(self, buf: bytes):
		try:
			self.connection.sendall(buf)
		except socket.timeout as e:
			self.close()

	def read(self, size: int=1) -> bytes:
		try:
			return self.connection.recv(size)
		except socket.timeout as e:
			self.close()
		return b''