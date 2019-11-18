from enum import Enum


class ReaderLedControls:

	def __init__(self, controls):
		self.controls = controls

	def build_data(self) -> bytes:
		data = bytearray()
		for control in controls:
			data.extend(control.build_data())
		return bytes(data)

class ReaderLedControl:

	def __init__(self, reader_number: int, led_number: int,
			temporary_mode: TemporaryReaderControlCode,
			temporary_on_time: int,
			temporary_off_time: int,
			temporary_on_color: LedColor,
			temporary_off_color: LedColor,
			temporary_timer: int,
			permanent_mode: PermanentReaderControlCode,
			permanent_on_time: int,
			permanent_off_time: int,
			permanent_on_color: LedColor,
			permanent_off_color: LedColor):
		self.reader_number = reader_number
		self.led_number = led_number
		self.temporary_mode = temporary_mode
		self.temporary_on_time = temporary_on_time
		self.temporary_off_time = temporary_off_time
		self.temporary_on_color = temporary_on_color
		self.temporary_off_color = temporary_off_color
		self.temporary_timer = temporary_timer
		self.permanent_mode = permanent_mode
		self.permanent_on_time = permanent_on_time
		self.permanent_off_time = permanent_off_time
		self.permanent_on_color = permanent_on_color
		self.permanent_off_color = permanent_off_color

	def build_data(self) -> bytes:
		temporary_timer_bytes = Message.convert_short_to_bytes(self.temporary_timer)
		return bytes([self.reader_number, self.led_number,
			self.temporary_mode.value,
			self.temporary_on_time,
			self.temporary_off_time,
			self.temporary_on_color.value,
			self.temporary_off_color.value,
			temporary_timer_bytes[0],
			temporary_timer_bytes[1],
			self.permanent_mode,
			self.permanent_on_time,
			self.permanent_off_time,
			self.permanent_on_color.value,
			self.permanent_off_color.value
		])

class TemporaryReaderControlCode(Enum):
	Nop = 0x00
	CancelAnyTemporaryAndDisplayPermanent = 0x01
	SetTemporaryAndStartTimer = 0x02

class PermanentReaderControlCode(Enum):
	Nop = 0x00
	SetPermanentState = 0x02

class LedColor(Enum):
	Black = 0
	Red = 1
	Green =  2
	Amber = 3
	Blue = 4