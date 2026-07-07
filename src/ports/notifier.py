# src/ports/notifier.py
from abc import ABC, abstractmethod

class Notifier(ABC):

    @abstractmethod
    def send_notification(self, text: str) -> None:
        """Envía una alerta con formato HTML a los suscriptores."""
        pass