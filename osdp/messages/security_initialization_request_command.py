from command import Command


class SecurityInitializationRequestCommand(Command):

	def __init__(self, address: int, server_random_number: bytes):
		self.address = address
		self.server_random_number = server_random_number

	def command_code(self) -> int:
		return 0x76

	def security_control_block(self) -> bytes:
		return bytes([ 0x03, 0x11, 0x00 ])

	def data() -> bytes:
		return self.server_random_number

	def custom_command_update(self, command_buffer: bytearray):
		pass