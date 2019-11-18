

class OutputStatus:

	def __init__(self, statuses):
		self.statuses = statuses

	@staticmethod
	def parse_data(reply: Reply) -> OutputStatus:
		data = reply.extract_reply_data
		statuses = map(lambda b : b!=0, data)
		return OutputStatus(statuses)

	def __repr__(self):
		return 'Output: [' + ', '.join([str(status) for status in self.statuses]) + ']'