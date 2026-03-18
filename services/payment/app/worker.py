import json
import logging
import threading
import time
from datetime import datetime

import httpx
import redis

from app.config import Settings

logger = logging.getLogger(__name__)


class PaymentWorker:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True, name="payment-worker")
        self.processed_count = 0
        self.failed_callbacks = 0
        self.redis_client = redis.Redis.from_url(self.settings.redis_url, decode_responses=True)

    def start(self) -> None:
        self.thread.start()
        logger.info("Worker de pagamentos iniciado.")

    def stop(self) -> None:
        self.stop_event.set()
        self.thread.join(timeout=5)
        logger.info("Worker de pagamentos finalizado.")

    def _run(self) -> None:
        # Fica escutando a fila continuamente enquanto o servico estiver ativo.
        while not self.stop_event.is_set():
            item = self.redis_client.blpop(self.settings.payment_queue_name, timeout=1)
            if not item:
                continue

            _, raw_payload = item
            try:
                payload = json.loads(raw_payload)
                self._process_payload(payload)
            except Exception as exc:
                logger.exception("Falha ao processar mensagem da fila de pagamentos: %s", exc)

    def _process_payload(self, payload: dict) -> None:
        # A falha pode ser simulada para facilitar testes do fluxo completo.
        reservation_id = payload["reservation_id"]
        retry_count = int(payload.get("retry_count", 0))
        simulate_failure = bool(payload.get("simulate_payment_failure", False))

        logger.info("Processando pagamento da reserva %s.", reservation_id)
        time.sleep(self.settings.simulated_payment_delay_seconds)

        payment_status = "failed" if simulate_failure else "paid"
        message = (
            "Pagamento recusado pela simulacao do fluxo."
            if simulate_failure
            else "Pagamento processado com sucesso."
        )
        processed_at = datetime.utcnow().isoformat()
        callback_payload = {
            "reservation_id": reservation_id,
            "payment_status": payment_status,
            "provider_reference": f"PAY-{reservation_id}-{int(time.time())}",
            "message": message,
            "processed_at": processed_at,
        }

        try:
            response = httpx.post(
                self.settings.api_internal_url,
                json=callback_payload,
                headers={"X-Internal-Token": self.settings.internal_service_token},
                timeout=self.settings.callback_timeout_seconds,
            )
            response.raise_for_status()
            self.processed_count += 1
            logger.info("Pagamento da reserva %s finalizado com status %s.", reservation_id, payment_status)
        except Exception as exc:
            # Reenvia a mensagem quando o callback falha por motivo temporario.
            self.failed_callbacks += 1
            logger.warning(
                "Falha no callback da reserva %s (tentativa %s/%s): %s",
                reservation_id,
                retry_count + 1,
                self.settings.max_callback_retries,
                exc,
            )
            if retry_count < self.settings.max_callback_retries:
                payload["retry_count"] = retry_count + 1
                self.redis_client.rpush(self.settings.payment_queue_name, json.dumps(payload))
            else:
                logger.error("Callback da reserva %s falhou definitivamente.", reservation_id)
