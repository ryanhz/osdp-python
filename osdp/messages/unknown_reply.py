from uuid import UUID, uuid4
from message import Message
from command import Command
from reply import Reply


class UnknownReply(Command):

	def __init__(self, data: bytes, connection_id: UUID, issuing_command: Command, device: Device):
		super().__init__(data, connection_id, issuing_command, device)

	def reply_code(self) -> int:
		return self.type.value

	def security_control_block(self) -> bytes:
		security_block_length = len(self.secure_block_data) + 2
		secbk = bytearray([self.security_block_type, security_block_length])
		secbk.extend(self.secure_block_data)
		return bytes(secbk)

	def data() -> bytes:
		return self.extract_reply_data
