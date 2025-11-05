from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Глобальный producer (создаётся один раз)
_producer: KafkaProducer | None = None


def get_producer() -> KafkaProducer:
    """
    Создать или получить существующий KafkaProducer.
    Используется singleton паттерн - один producer на всё приложение.
    """
    global _producer
    
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # Настройки для надёжности
            acks='all',  # Ждём подтверждения от всех реплик
            retries=3,   # Количество попыток при ошибке
            max_in_flight_requests_per_connection=1,  # Порядок гарантирован
        )
        logger.info(f"Kafka producer создан. Подключение к {settings.KAFKA_BOOTSTRAP_SERVERS}")
    
    return _producer


def send_event(topic: str, event: Dict[str, Any], key: str | None = None) -> bool:
    """
    Отправить событие в Kafka топик.
    
    Args:
        topic: Название топика (например, "user-events")
        event: Словарь с данными события
        key: Опциональный ключ для партиционирования (по умолчанию None)
    
    Returns:
        True если событие успешно отправлено, False при ошибке
    """
    try:
        producer = get_producer()
        
        # Отправляем событие в Kafka
        future = producer.send(topic, value=event, key=key)
        
        # Ждём подтверждения (можно сделать асинхронно, но для простоты синхронно)
        record_metadata = future.get(timeout=10)
        
        logger.info(
            f"Событие отправлено в топик '{topic}'. "
            f"Партиция: {record_metadata.partition}, "
            f"Offset: {record_metadata.offset}"
        )
        
        return True
        
    except KafkaError as e:
        logger.error(f"Ошибка при отправке события в Kafka: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке события: {e}")
        return False


def close_producer():
    """Закрыть producer (вызывается при завершении приложения)."""
    global _producer
    
    if _producer is not None:
        _producer.close()
        _producer = None
        logger.info("Kafka producer закрыт")

