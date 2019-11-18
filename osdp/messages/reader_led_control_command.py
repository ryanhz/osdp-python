from command import Command


class ReaderLedControlCommand(Command):

	def __init__(self, address: int, reader_led_controls ReaderLedControls):
		self.address = address
		self.reader_led_controls = reader_led_controls

	def command_code(self) -> int:
		return 0x69

	def security_control_block(self) -> bytes:
		return bytes([ 0x02, 0x17 ])

	def data() -> bytes:
		return self.reader_led_controls.build_data()

	def custom_command_update(self, command_buffer: bytearray):
		pass