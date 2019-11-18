from command import Command


class InputStatusReportCommand(Command):

	def __init__(self, address: int):
		self.address = address

	def command_code(self) -> int:
		return 0x65

	def security_control_block(self) -> bytes:
		return bytes([ 0x02, 0x15 ])

	def data() -> bytes:
		return bytes([ ])

	def custom_command_update(self, command_buffer: bytearray):
		pass