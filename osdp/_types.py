from enum import Enum
from threading import Event


class ReplyType(Enum):
	Ack = 0x40
	Nak = 0x41
	PdIdReport = 0x45
	PdCapabilitiesReport = 0x46
	LocalStatusReport = 0x48
	InputStatusReport = 0x49
	OutputStatusReport = 0x4A
	ReaderStatusReport = 0x4B
	RawReaderData = 0x50
	FormattedReaderData = 0x51
	KeypadData = 0x53
	PdCommunicationsConfigurationReport = 0x54
	BiometricData = 0x57
	BiometricMatchResult = 0x58
	CrypticData = 0x76
	InitialRMac = 0x78
	Busy = 0x79
	ManufactureSpecific = 0x90


class SecurityBlockType(Enum):
	BeginNewSecureConnectionSequence = 0x11
	SecureConnectionSequenceStep2 = 0x12
	SecureConnectionSequenceStep3 = 0x13
	SecureConnectionSequenceStep4 = 0x14
	CommandMessageWithNoDataSecurity = 0x15
	ReplyMessageWithNoDataSecurity = 0x16
	CommandMessageWithDataSecurity = 0x17
	ReplyMessageWithDataSecurity = 0x18


class Control:

	def __init__(self, sequence: int, use_crc: bool, has_security_control_block: bool):
		self.sequence = sequence
		self.use_crc = use_crc
		self.has_security_control_block = has_security_control_block

	@property
	def control_byte(self) -> int:
		cb = self.sequence & 0x03
		cb |= (0x04 if self.use_crc else 0)
		cb |= (0x08 if self.has_security_control_block else 0)
		return cb & 0xFF

	def increment_sequence(self):
		self.sequence = self.sequence % 3 + 1


class ErrorCode(Enum):
	NoError = 0x0
	BadChecksumOrCrc = 0x1
	InvalidCommandLength = 0x2
	UnknownCommandCode = 0x3
	UnexpectedSequenceNumber = 0x4
	DoesNotSupportSecurityBlock = 0x5
	CommunicationSecurityNotMet = 0x6
	BioTypeNotSupported = 0x7
	BioFormatNotSupported = 0x8
	UnableToProcessCommand = 0x9
	GenericError = 0xFF


class Nak:

	def __init__(self, error_code: ErrorCode, extra_data: bytes):
		self.error_code = error_code
		self.extra_data = extra_data

	@staticmethod
	def parse_data(reply):
		data = reply.extract_reply_data
		if len(data) < 1:
			raise ValueError("Invalid size for the data")

		error_code = ErrorCode(data[0])
		extra_data = data[1:]
		return Nak(error_code, extra_data)

	def __repr__(self):
		return "Error: {0}\n Data: {1}".format(self.error_code.name, self.extra_data.hex())


class DeviceIdentification:

	def __init__(
		self, vendor_code: bytes, model_number: int, version: int, serial_number: int,
		firmware_major: int, firmware_minor: int, firmware_build: int
	):
		self.vendor_code = vendor_code
		self.model_number = model_number
		self.version = version
		self.serial_number = serial_number
		self.firmware_major = firmware_major
		self.firmware_minor = firmware_minor
		self.firmware_build = firmware_build

	@staticmethod
	def parse_data(reply):
		data = reply.extract_reply_data
		if len(data) != 12:
			raise ValueError("Invalid size for the data")

		vendor_code = data[0:3]
		model_number = data[3]
		version = data[4]
		serial_number = int.from_bytes(data[5:9], byteorder='little')
		firmware_major = data[9]
		firmware_minor = data[10]
		firmware_build = data[11]
		return DeviceIdentification(
			vendor_code,
			model_number,
			version,
			serial_number,
			firmware_major,
			firmware_minor,
			firmware_build
		)

	def __repr__(self):
		return \
			"     Vendor Code: {0}\n"\
			"    Model Number: {1}\n"\
			"         Version: {2}\n"\
			"   Serial Number: {3}\n"\
			"Firmware Version: {4}.{5}.{6}"\
			.format(
				self.vendor_code.hex(),
				self.model_number,
				self.version,
				self.serial_number.to_bytes(4, byteorder='little').hex(),
				self.firmware_major,
				self.firmware_minor,
				self.firmware_build
			)


class CapabilityFunction(Enum):
	Unknown = 0
	ContactStatusMonitoring = 1
	OutputControl = 2
	CardDataFormat = 3
	ReaderLEDControl = 4
	ReaderAudibleOutput = 5
	ReaderTextOutput = 6
	TimeKeeping = 7
	CheckCharacterSupport = 8
	CommunicationSecurity = 9
	ReceiveBufferSize = 10
	LargestCombinedMessageSize = 11
	SmartCardSupport = 12
	Readers = 13
	Biometrics = 14


class DeviceCapability:

	def __init__(self, function: CapabilityFunction, compliance: int, number_of: int):
		self.function = function
		self.compliance = compliance
		self.number_of = number_of

	@staticmethod
	def parse_data(data: bytes):
		function = CapabilityFunction(data[0]) if data[0] <= 14 else CapabilityFunction.Unknown
		compliance = data[1]
		number_of = data[2]
		return DeviceCapability(function, compliance, number_of)

	def __repr__(self):
		if self.function == CapabilityFunction.ReceiveBufferSize or \
			self.function == CapabilityFunction.LargestCombinedMessageSize:
			return \
				"  Function: {0}\n"\
				"      Size: {1}".format(
					self.function.name,
					int.from_bytes(bytes([self.compliance, self.number_of]), byteorder='little')
				)
		else:
			return \
				"  Function: {0}\n"\
				"Compliance: {1}\n"\
				" Number Of: {2}".format(
					self.function.name,
					self.compliance,
					self.number_of
				)


class DeviceCapabilities:

	def __init__(self, capabilities):
		self.capabilities = capabilities

	@staticmethod
	def parse_data(reply):
		data = reply.extract_reply_data
		if len(data) % 3 != 0:
			raise ValueError("Invalid size for the data")

		capabilities = []
		for i in range(0, len(data), 3):
			capabilities.append(DeviceCapability.parse_data(data[i:(i + 3)]))
		return DeviceCapabilities(capabilities)

	def __repr__(self):
		return '\n\n'.join([str(capability) for capability in self.capabilities])


class InputStatus:

	def __init__(self, statuses):
		self.statuses = statuses

	@staticmethod
	def parse_data(reply):
		data = reply.extract_reply_data
		statuses = map(lambda b: b != 0, data)
		return InputStatus(statuses)

	def __repr__(self):
		return 'Input: [' + ', '.join([str(status) for status in self.statuses]) + ']'


class OutputStatus:

	def __init__(self, statuses):
		self.statuses = statuses

	@staticmethod
	def parse_data(reply):
		data = reply.extract_reply_data
		statuses = map(lambda b: b != 0, data)
		return OutputStatus(statuses)

	def __repr__(self):
		return 'Output: [' + ', '.join([str(status) for status in self.statuses]) + ']'


class LocalStatus:

	def __init__(self, tamper: bool, power_failure: bool):
		self.tamper = tamper
		self.power_failure = power_failure

	@staticmethod
	def parse_data(reply):
		data = reply.extract_reply_data
		if len(data) < 2:
			raise ValueError("Invalid size for the data")

		tamper = data[0] != 0
		power_failure = data[1] != 0
		return LocalStatus(tamper, power_failure)

	def __repr__(self):
		return "       Tamper: {0}\nCPower Failure: {1}".format(self.tamper, self.power_failure)


class ReaderTamperStatus(Enum):
	Normal = 0x00
	NotConnected = 0x01
	Tamper = 0x02


class ReaderStatus:

	def __init__(self, statuses):
		self.statuses = statuses

	@staticmethod
	def parse_data(reply):
		data = reply.extract_reply_data
		statuses = map(lambda b: ReaderTamperStatus(b), data)
		return ReaderStatus(statuses)

	def __repr__(self):
		return 'Reader Status: [' + ', '.join([str(status) for status in self.statuses]) + ']'


class OutputControlCode(Enum):
	Nop = 0x00
	PermanentStateOffAbortTimedOperation = 0x01
	PermanentStateOnAbortTimedOperation = 0x02
	PermanentStateOffAllowTimedOperation = 0x03
	PermanentStateOnAllowTimedOperation = 0x04
	TemporaryStateOnResumePermanentState = 0x05
	TemporaryStateOffResumePermanentState = 0x06


class OutputControl:

	def __init__(self, output_number: int, output_control_code: OutputControlCode, timer: int):
		self.output_number = output_number
		self.output_control_code = output_control_code
		self.timer = timer

	def build_data(self) -> bytes:
		timer_bytes = self.timer.to_bytes(2, byteorder='little')
		return bytes([self.output_number, self.output_control_code.value, timer_bytes[0], timer_bytes[1]])


class OutputControls:

	def __init__(self, controls):
		self.controls = controls

	def build_data(self) -> bytes:
		data = bytearray()
		for control in self.controls:
			data.extend(control.build_data())
		return bytes(data)


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
	Green = 2
	Amber = 3
	Blue = 4


class ReaderLedControl:

	def __init__(
		self, reader_number: int, led_number: int,
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
		permanent_off_color: LedColor
	):
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
		temporary_timer_bytes = self.temporary_timer.to_bytes(2, byteorder='little')
		return bytes([
			self.reader_number, self.led_number,
			self.temporary_mode.value,
			self.temporary_on_time,
			self.temporary_off_time,
			self.temporary_on_color.value,
			self.temporary_off_color.value,
			temporary_timer_bytes[0],
			temporary_timer_bytes[1],
			self.permanent_mode.value,
			self.permanent_on_time,
			self.permanent_off_time,
			self.permanent_on_color.value,
			self.permanent_off_color.value
		])


class ReaderLedControls:

	def __init__(self, controls):
		self.controls = controls

	def build_data(self) -> bytes:
		data = bytearray()
		for control in self.controls:
			data.extend(control.build_data())
		return bytes(data)


class ToneCode(Enum):
	NoTone = 0
	Off = 1
	DefaultTone = 2
	TBD = 3


class ReaderBuzzerControl:

	def __init__(
		self,
		reader_number: int,
		tone_code: ToneCode,
		on_time: int,
		off_time: int,
		count: int
	):
		self.reader_number = reader_number
		self.tone_code = tone_code
		self.on_time = on_time
		self.off_time = off_time
		self.count = count

	def build_data(self) -> bytes:
		return bytes([
			self.reader_number,
			self.tone_code.value,
			self.on_time,
			self.off_time,
			self.count
		])


class TextCommand(Enum):
	PermanentTextNoWrap = 0x01
	PermanentTextWithWrap = 0x02
	TempTextNoWrap = 0x02
	TempTextWithWrap = 0x04


class ReaderTextOutput:

	def __init__(
		self,
		reader_number: int,
		text_command: TextCommand,
		temp_text_time: int,
		row: int,
		column: int,
		text: str
	):
		self.reader_number = reader_number
		self.text_command = text_command
		self.temp_text_time = temp_text_time
		self.row = row
		self.column = column
		self.text = text

	def build_data(self) -> bytes:
		text_length = len(self.text)
		return bytes([
			self.reader_number,
			self.text_command.value,
			self.temp_text_time,
			self.row,
			self.column,
			text_length,
		]) + self.text.encode("ascii")


class FormatCode(Enum):
	NotSpecified = 0x0
	Wiegand = 0x1


class RawCardData:

	def __init__(self, reader_number: int, format_code: FormatCode, bit_count: int, data: bytes):
		self.reader_number = reader_number
		self.format_code = format_code
		self.bit_count = bit_count
		self.data = data

	@staticmethod
	def parse_data(reply) -> Nak:
		data = reply.extract_reply_data
		if len(data) < 4:
			raise ValueError("Invalid size for the data")

		reader_number = data[0]
		format_code = FormatCode(data[1])
		bit_count = int.from_bytes(data[2:4], byteorder='little')
		data = data[4:]
		return RawCardData(reader_number, format_code, bit_count, data)

	def __repr__(self):
		return \
			"Reader Number: {0}\n"\
			"  Format Code: {1}\n"\
			"    Bit Count: {2}\n"\
			"         Data: {3}".format(
				self.reader_number,
				self.format_code.name,
				self.bit_count,
				self.data.hex().upper()
			)


class KeypadData:

	def __init__(self, reader_number: int, bit_count: int, data: bytes):
		self.reader_number = reader_number
		self.bit_count = bit_count
		self.data = data

	@staticmethod
	def parse_data(reply) -> Nak:
		data = reply.extract_reply_data
		if len(data) < 2:
			raise ValueError("Invalid size for the data")

		reader_number = data[0]
		bit_count = int.from_bytes(data[1:2], byteorder='little')
		data = data[2:]
		return KeypadData(reader_number, bit_count, data)

	def __repr__(self):
		return \
			"Reader Number: {0}\n"\
			"    Bit Count: {1}\n"\
			"         Data: {2}".format(
				self.reader_number,
				self.bit_count,
				self.data.hex().upper()
			)


class DataEvent(Event):

	def __init__(self):
		super().__init__()
		self.data = None

	def set_data(self, data):
		self.data = data
		super().set()

	def clear_data(self):
		self.data = None
		super().clear()

	def wait_data(self, timeout=None):
		self.wait(timeout)
		if self.is_set():
			return self.data
		else:
			return None
