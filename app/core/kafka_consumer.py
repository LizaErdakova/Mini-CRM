from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_consumer(topic: str) -> KafkaConsumer:
    """
    Создать KafkaConsumer для чтения событий из топика.
    
    Args:
        topic: Название топика для чтения
    
    Returns:
        Настроенный KafkaConsumer
    """
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
        # Начинаем читать с последнего непрочитанного сообщения
        auto_offset_reset='latest',
        # Группа потребителей (для балансировки нагрузки)
        group_id='crm-consumer-group',
        # Подтверждаем чтение сообщений
        enable_auto_commit=True,
        auto_commit_interval_ms=1000,
    )
    
    logger.info(f"Kafka consumer создан для топика '{topic}'")
    return consumer


def process_user_event(event: Dict[str, Any]):
    """Обработать событие пользователя."""
    event_type = event.get('event_type')
    
    if event_type == 'user.created':
        logger.info(
            f"📝 Событие: Пользователь создан - "
            f"ID: {event.get('user_id')}, "
            f"Email: {event.get('email')}, "
            f"Имя: {event.get('name')}"
        )
        # Здесь можно добавить дополнительную логику:
        # - Отправка приветственного email
        # - Создание профиля пользователя
        # - Отправка в аналитическую систему
        
    elif event_type == 'user.logged_in':
        logger.info(
            f"🔐 Событие: Пользователь вошёл в систему - "
            f"ID: {event.get('user_id')}, "
            f"Email: {event.get('email')}"
        )
        # Здесь можно добавить:
        # - Логирование активности
        # - Обновление последнего времени входа
        # - Отправка уведомления о безопасности


def process_course_event(event: Dict[str, Any]):
    """Обработать событие курса."""
    event_type = event.get('event_type')
    
    if event_type == 'course.created':
        logger.info(
            f"📚 Событие: Курс создан - "
            f"ID: {event.get('course_id')}, "
            f"Название: {event.get('title')}, "
            f"Цена: {event.get('price')}, "
            f"Создан администратором: {event.get('created_by')}"
        )
        # Здесь можно добавить:
        # - Отправка уведомления администраторам
        # - Создание метаданных курса
        # - Индексация для поиска


def start_user_events_consumer():
    """Запустить consumer для событий пользователей."""
    try:
        consumer = create_consumer(settings.KAFKA_TOPIC_USER_EVENTS)
        logger.info(f"🚀 Consumer для топика '{settings.KAFKA_TOPIC_USER_EVENTS}' запущен")
        
        for message in consumer:
            try:
                event = message.value
                process_user_event(event)
                
            except Exception as e:
                logger.error(f"Ошибка при обработке события пользователя: {e}")
                
    except KafkaError as e:
        logger.error(f"Ошибка Kafka consumer для пользователей: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка в consumer пользователей: {e}")


def start_course_events_consumer():
    """Запустить consumer для событий курсов."""
    try:
        consumer = create_consumer(settings.KAFKA_TOPIC_COURSE_EVENTS)
        logger.info(f"🚀 Consumer для топика '{settings.KAFKA_TOPIC_COURSE_EVENTS}' запущен")
        
        for message in consumer:
            try:
                event = message.value
                process_course_event(event)
                
            except Exception as e:
                logger.error(f"Ошибка при обработке события курса: {e}")
                
    except KafkaError as e:
        logger.error(f"Ошибка Kafka consumer для курсов: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка в consumer курсов: {e}")


def start_consumers():
    """
    Запустить все consumers в отдельных потоках.
    Эта функция вызывается при старте приложения.
    """
    import threading
    
    # Запускаем consumer для событий пользователей
    user_thread = threading.Thread(
        target=start_user_events_consumer,
        daemon=True,  # Поток завершится при завершении основного процесса
        name="user-events-consumer"
    )
    user_thread.start()
    logger.info("✅ Поток consumer для событий пользователей запущен")
    
    # Запускаем consumer для событий курсов
    course_thread = threading.Thread(
        target=start_course_events_consumer,
        daemon=True,
        name="course-events-consumer"
    )
    course_thread.start()
    logger.info("✅ Поток consumer для событий курсов запущен")

