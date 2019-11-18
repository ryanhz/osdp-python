

class Control:

	def __init__(self, sequence: int, use_crc: bool, has_security_control_block: bool):
		self.sequence = sequence
		self.use_crc = use_crc
		self.has_security_control_block = has_security_control_block

	@property
	def control_byte(self) -> int:
		return (self.sequence & 0x03 | (0x04 if self.use_crc else 0) | (0x08 if self.has_security_control_block else 0)) & 0xFF

	def increment_sequence(self, _sequence: int):
		_sequence = (_sequence+1)%3 + 1
		self.sequence = _sequence
