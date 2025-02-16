import logging
from customtkinter import CTkTextbox # type: ignore

from core.interfaces import LoggerProtocol, TextBoxProtocol

class TextHandler(logging.Handler):
    """Кастомный обработчик для вывода логов в текстовое поле."""

    def __init__(self, text_widget: CTkTextbox)->None:
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record: logging.LogRecord) -> None:
        """Записывает сообщение логгера в текстовое поле."""
        log_message = self.format(record)
        self.text_widget.configure(state="normal")  # Разрешаем редактирование
        self.text_widget.insert("end", log_message + "\n")  # Добавляем сообщение
        self.text_widget.configure(state="disabled")  # Запрещаем редактирование
        self.text_widget.see("end")  # Прокручиваем текстовое поле вниз


class SetupLoggerMixin(LoggerProtocol, TextBoxProtocol):
    def setup_logger(self)->None:
        """Настройка логгера."""
        self.logger.setLevel(logging.DEBUG)
        # Создаем форматтер
        formatter = logging.Formatter("%(asctime)s - %(filename)s:%(lineno)d - [%(levelname)s] - %(message)s")
        # Создаем кастомный обработчик и добавляем его в логгер
        text_handler = TextHandler(self.text_box)
        text_handler.setFormatter(formatter)
        self.logger.addHandler(text_handler)
