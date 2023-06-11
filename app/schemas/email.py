class Email:
    def __init__(
        self,
        messageId: str,
        subject: str,
        sendFrom: str,
        sendTo: str,
        body: str,
    ) -> None:
        self.messageId = messageId
        self.subject = subject
        self.sendFrom = sendFrom
        self.sendTo = sendTo
        self.body = body
