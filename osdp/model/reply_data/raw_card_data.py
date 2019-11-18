from enum import Enum


class RawCardData:

	def __init__(self, reader_number: int, format_code: FormatCode, bit_count: int, data: bytes):
		self.reader_number = reader_number
		self.format_code = format_code
		self.bit_count = bit_count
		self.data = data

	@staticmethod
	def parse_data(reply: Reply) -> Nak:
		data = reply.extract_reply_data
		if len(data)<4:
			raise ValueError("Invalid size for the data")

		reader_number = data[0]
		format_code = FormatCode(data[1])
		bit_count = Message.convert_bytes_to_short(data[2:4])
		data = data[4:]
		return RawCardData(reader_number, format_code, bit_count, data)

	def __repr__(self):
		return "Reader Number: {0}\n  Format Code: {1}\n    Bit Count: {2}\n         Data: {3}".format(self.reader_number, self.format_code.name, self.bit_count, self.data.hex())

class FormatCode(Enum):
	NotSpecified = 0x0
	Wiegand = 0x1