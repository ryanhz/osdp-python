from enum import Enum

class OutputControls:

	def __init__(self, controls):
		self.controls = controls

	def build_data(self) -> bytes:
		data = bytearray()
		for control in controls:
			data.extend(control.build_data())
		return bytes(data)

class OutputControl:

	def __init__(self, output_number: int, output_control_code: OutputControlCode, timer: int):
		self.output_number = output_number
		self.output_control_code = output_control_code
		self.timer = timer

	def build_data(self) -> bytes:
		timer_bytes = Message.convert_short_to_bytes(self.timer)
		return bytes([self.output_number, self.output_control_code.value, timer_bytes[0], timer_bytes[1]])

class OutputControlCode(Enum):
	Nop = 0x00
	PermanentStateOffAbortTimedOperation = 0x01
	PermanentStateOnAbortTimedOperation = 0x02
	PermanentStateOffAllowTimedOperation = 0x03
	PermanentStateOnAllowTimedOperation = 0x04
	TemporaryStateOnResumePermanentState = 0x05
	TemporaryStateOffResumePermanentState = 0x06
