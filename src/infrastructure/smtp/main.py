import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.message import EmailMessage


@dataclass
class BaseSMTPServer(ABC):
    @abstractmethod
    def start(self): ...

    @abstractmethod
    def create_message(self, content: str) -> EmailMessage: ...

    @abstractmethod
    def send_email(self, message: EmailMessage) -> None: ...

    @abstractmethod
    def stop(self): ...


@dataclass
class SMTPServer(BaseSMTPServer):
    server: smtplib.SMTP_SSL
    from_address: str
    password: str
    to_address: str
    subject: str

    def start(self) -> None:
        self.server.login(self.from_address, self.password)

    def create_message(self, content: str) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = self.subject
        message["From"] = self.from_address
        message["To"] = self.to_address
        message.set_content(content)
        return message

    def send_email(self, message: EmailMessage) -> None:
        self.server.send_message(message)

    def stop(self) -> None:
        self.server.quit()
