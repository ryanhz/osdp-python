from command import Command


class ServerCryptogramCommand(Command):

	def __init__(self, address: int, server_cryptogram: bytes):
		self.address = address
		self.server_cryptogram = server_cryptogram

	def command_code(self) -> int:
		return 0x77

	def security_control_block(self) -> bytes:
		return bytes([ 0x03, 0x13, 0x00 ])

	def data() -> bytes:
		return self.server_cryptogram

	def custom_command_update(self, command_buffer: bytearray):
		pass