from abc import ABC, abstractmethod
import serial
import fcntl
import struct
import socket


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
	def read(self, size: int = 1) -> bytes:
		pass


class SerialPortOsdpConnection(OsdpConnection):

	def __init__(self, port: str, baud_rate: int, raspberry_pi: bool = False):
		self._port = port
		self._baud_rate = baud_rate
		self.serial_port = None
		self.raspberry_pi = raspberry_pi

	@property
	def baud_rate(self) -> int:
		return self._baud_rate

	@property
	def is_open(self) -> bool:
		return self.serial_port is not None and self.serial_port.is_open

	def open(self):
		self.serial_port = serial.Serial(port=self._port, baudrate=self._baud_rate, timeout=2.0)
		if self.raspberry_pi:
			fd = self.serial_port.fileno()
			# See struct serial_rs485 in linux kernel.
			# SER_RS485_ENABLED = 1 and SER_RS485_RTS_ON_SEND = 1
			# https://www.kernel.org/doc/Documentation/serial/serial-rs485.txt
			serial_rs485 = struct.pack('IIIIIIII', 3, 0, 0, 0, 0, 0, 0, 0)
			fcntl.ioctl(fd, 0x542F, serial_rs485)

	def close(self):
		if self.serial_port is not None:
			self.serial_port.close()
			self.serial_port = None

	def write(self, buf: bytes):
		self.serial_port.write(buf)

	def read(self, size: int = 1) -> bytes:
		return self.serial_port.read(size)


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
		except socket.timeout:
			self.is_connected = False

	def read(self, size: int = 1) -> bytes:
		try:
			return self.sock.recv(size)
		except socket.timeout:
			self.is_connected = False
		return b''


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
		except socket.timeout:
			self.close()

	def read(self, size: int = 1) -> bytes:
		try:
			return self.connection.recv(size)
		except socket.timeout:
			self.close()
		return b''
