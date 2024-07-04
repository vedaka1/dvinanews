from dataclasses import dataclass
from logging import Logger

from infrastructure.smtp.main import BaseSMTPServer


@dataclass
class SendMessage:
    smtp_server: BaseSMTPServer
    logger: Logger

    async def __call__(self, content: str) -> str:
        message = self.smtp_server.create_message(content)
        try:
            await self.smtp_server.send_email(message)
            return "Отправлено"
        except Exception as e:
            self.logger.error(f"usecase: SendMessage error: {e}")
            return "Ошибка"
