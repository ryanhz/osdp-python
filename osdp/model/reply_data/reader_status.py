

class ReaderStatus:

	def __init__(self, statuses):
		self.statuses = statuses

	@staticmethod
	def parse_data(reply: Reply) -> ReaderStatus:
		data = reply.extract_reply_data
		statuses = map(lambda b : ReaderTamperStatus(b), data)
		return ReaderStatus(statuses)

	def __repr__(self):
		return 'Reader Status: [' + ', '.join([str(status) for status in self.statuses]) + ']'

class ReaderTamperStatus(Enum):
	Normal = 0x00
	NotConnected = 0x01
	Tamper = 0x02