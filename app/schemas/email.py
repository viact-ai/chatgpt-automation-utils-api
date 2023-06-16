class Email:
    def __init__(
        self,
        threadId: str,
        labelIds: list[str],
        messageId: str,
        subject: str,
        sendFrom: str,
        sendTo: str,
        body: str,
        sendDate: str,  # in ISO format
    ) -> None:
        self.threadId = threadId
        self.labelIds = labelIds
        self.messageId = messageId
        self.subject = subject
        self.sendFrom = sendFrom
        self.sendTo = sendTo
        self.body = body
        self.sendDate = sendDate
