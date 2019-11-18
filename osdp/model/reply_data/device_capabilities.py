from enum import Enum

class DeviceCapabilities:

	def __init__(self, capabilities):
		self.capabilities = capabilities

	@staticmethod
	def parse_data(reply: Reply) -> DeviceCapabilities:
		data = reply.extract_reply_data
		if len(data)%3!=0:
			raise ValueError("Invalid size for the data")

		capabilities = []
		for i in range(0, len(data), 3):
			capabilities.append(DeviceCapability.parse_data(data[i:i+3]))
		return DeviceCapabilities(capabilities)

	def __repr__(self):
		return '\n\n'.join([str(capability) for capability in self.capabilities])

class DeviceCapability:

	def __init__(self, function: CapabilityFunction, compliance: int, number_of: int):
		self.function = function
		self.compliance = compliance
		self.number_of = number_of

	@staticmethod
	def parse_data(data: bytes) -> DeviceCapability:
		function = CapabilityFunction(data[0]) if data[0]<=14 else CapabilityFunction.Unknown
		compliance = data[1]
		number_of = data[2]
		return DeviceCapability(function, compliance, number_of)

	def __repr__(self):
		if(self.function==CapabilityFunction.ReceiveBufferSize or self.function==CapabilityFunction.LargestCombinedMessageSize):
			return "  Function: {0}\n      Size: {1}".format(self.function.name, Message.convert_bytes_to_short(bytes([self.compliance, self.number_of])))
		else:
			return "  Function: {0}\nCompliance: {1}\n Number Of: {2}".format(self.function.name, self.compliance, self.number_of)

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