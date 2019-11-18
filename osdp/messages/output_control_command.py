from command import Command
from output_controls import OutputControls


class OutputControlCommand(Command):

	def __init__(self, address: int, output_controls: OutputControls):
		self.address = address
		self.output_controls = output_controls

	def command_code(self) -> int:
		return 0x68

	def security_control_block(self) -> bytes:
		return bytes([ 0x02, 0x17 ])

	def data() -> bytes:
		return self.output_controls.build_data()

	def custom_command_update(self, command_buffer: bytearray):
		pass