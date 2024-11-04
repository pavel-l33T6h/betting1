import asyncio
import logging
import sys

import aiokafka
from fastapi import FastAPI

from models.event import Event
from settings import settings

log = logging.getLogger(__name__)


async def consume(app: FastAPI):
    app.state.events = {}
    app.state.events_ready = False

    def parse_message(msg):
        try:
            return Event.model_validate_json(msg)
        except Exception as err:
            log.warning("failed to parse message, skipping: %s", err)
            return None

    try:
        consumer = aiokafka.AIOKafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=settings.kafka_brokers,
            value_deserializer=parse_message,
            key_deserializer=lambda s: s.decode("utf-8"),
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        await consumer.start()

        topic_partitions: list[aiokafka.TopicPartition] = []
        partitions_to_backfill: set[int] = set()
        for partition in consumer.partitions_for_topic(settings.kafka_topic):
            topic_partitions.append(
                aiokafka.TopicPartition(topic=settings.kafka_topic, partition=partition)
            )
            partitions_to_backfill.add(partition)

        init_max_offsets: dict[int, int] = {}
        for k, v in (await consumer.end_offsets(topic_partitions)).items():
            if v == 0:
                partitions_to_backfill.remove(k.partition)
                continue
            init_max_offsets[k.partition] = v - 1

        log.debug("latest partition offsets: %s", init_max_offsets)

        log.info("consuming events from kafka")
        try:
            async for message in consumer:
                if message.value:
                    log.debug("message read: %s", message.value)
                    app.state.events[message.value.id] = message.value
                if (
                    not app.state.events_ready
                    and message.partition in partitions_to_backfill
                ):
                    if message.offset >= init_max_offsets[message.partition]:
                        partitions_to_backfill.remove(message.partition)
                    if not partitions_to_backfill:
                        log.info("done backfilling events")
                        app.state.events_ready = True
        except asyncio.CancelledError:
            log.warning("the app has been stopped: shutting down kafka consumer")
            await consumer.stop()
    except Exception:
        log.error("consumer error occurred, triggering app shutdown", exc_info=True)
        await consumer.stop()
        sys.exit(1)
