from command import Command


class DeviceCapabilitiesCommand(Command):

	def __init__(self, address: int):
		self.address = address

	def command_code(self) -> int:
		return 0x62

	def security_control_block(self) -> bytes:
		return bytes([ 0x02, 0x17 ])

	def data() -> bytes:
		return bytes([ 0x00 ])

	def custom_command_update(self, command_buffer: bytearray):
		pass