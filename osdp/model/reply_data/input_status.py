

class InputStatus:

	def __init__(self, statuses):
		self.statuses = statuses

	@staticmethod
	def parse_data(reply: Reply) -> InputStatus:
		data = reply.extract_reply_data
		statuses = map(lambda b : b!=0, data)
		return InputStatus(statuses)

	def __repr__(self):
		return 'Input: [' + ', '.join([str(status) for status in self.statuses]) + ']'