import json
import logging
import threading
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime

import redis

from app.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class NotificationRecord:
    # Estrutura simples para exibir as ultimas notificacoes no painel.
    reservation_id: int
    customer_email: str
    customer_name: str
    message: str
    sent_at: str


class NotificationStore:
    def __init__(self, maxlen: int) -> None:
        self.records: deque[NotificationRecord] = deque(maxlen=maxlen)
        self.lock = threading.Lock()

    def add(self, notification: NotificationRecord) -> None:
        # Mantem as notificacoes mais recentes no inicio da lista.
        with self.lock:
            self.records.appendleft(notification)

    def list_all(self) -> list[dict]:
        with self.lock:
            return [asdict(record) for record in list(self.records)]


class NotificationWorker:
    def __init__(self, settings: Settings, store: NotificationStore) -> None:
        self.settings = settings
        self.store = store
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True, name="notification-worker")
        self.processed_count = 0
        self.redis_client = redis.Redis.from_url(self.settings.redis_url, decode_responses=True)

    def start(self) -> None:
        self.thread.start()
        logger.info("Worker de notificacoes iniciado.")

    def stop(self) -> None:
        self.stop_event.set()
        self.thread.join(timeout=5)
        logger.info("Worker de notificacoes finalizado.")

    def _run(self) -> None:
        # Consome notificacoes publicadas pela API apos o pagamento.
        while not self.stop_event.is_set():
            item = self.redis_client.blpop(self.settings.notification_queue_name, timeout=1)
            if not item:
                continue

            _, raw_payload = item
            try:
                payload = json.loads(raw_payload)
                notification = NotificationRecord(
                    reservation_id=payload["reservation_id"],
                    customer_email=payload["customer_email"],
                    customer_name=payload["customer_name"],
                    message=payload["message"],
                    sent_at=payload.get("sent_at") or datetime.utcnow().isoformat(),
                )
                self.store.add(notification)
                self.processed_count += 1
                logger.info(
                    "Notificacao simulada enviada para %s referente a reserva %s.",
                    notification.customer_email,
                    notification.reservation_id,
                )
            except Exception as exc:
                logger.exception("Falha ao processar notificacao da fila: %s", exc)
