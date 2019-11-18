import serial


class SerialPortOsdpConnection(OsdpConnection):
	
	def __init__(self, port: str, baud_rate: int):
		self._port = port
		self._baud_rate = baud_rate
		self.serial_port = None

	@property
	def baud_rate(self) -> int:
		return self._baud_rate

	@property
	def is_open(self) -> bool:
		self.serial_port is not None and self.serial_port.is_open

	def open(self):
		self.serial_port = serial.Serial(port=self._port, baudrate=self._baud_rate, timeout=2.0)

	def close(self):
		if self.serial_port is not None:
			self.serial_port.close()
			self.serial_port = None

	def write(self, buf: bytes):
		self.serial_port.write(buf)

	def read(self, size: int=1) -> bytes:
		return self.serial_port.read(size)