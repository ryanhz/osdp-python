from enum import Enum

class Nak:

	def __init__(self, error_code: ErrorCode, extra_data: bytes):
		self.error_code = error_code
		self.extra_data = extra_data

	@staticmethod
	def parse_data(reply: Reply) -> Nak:
		data = reply.extract_reply_data
		if len(data)<1:
			raise ValueError("Invalid size for the data")

		error_code = ErrorCode(data[0])
		extra_data = data[1:]
		return Nak(error_code, extra_data)

	def __repr__(self):
		return "Error: {0}\n Data: {1}".format(self.error_code.name, self.extra_data.hex())


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