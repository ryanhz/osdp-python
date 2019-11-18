from reply import Reply


class AckReply(Command):

	def reply_code(self) -> int:
		return 0x40

	def security_control_block(self) -> bytes:
		return bytes([ 0x02, 0x16 ])

	def data() -> bytes:
		return bytes([ ])
