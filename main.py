from fastapi import FastAPI
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio

app = FastAPI()
loop = asyncio.get_event_loop()

producer = AIOKafkaProducer(loop=loop, bootstrap_servers="kafka:9092")
consumer = AIOKafkaConsumer("my_topic", loop=loop, bootstrap_servers="kafka:9092")


@app.on_event("startup")
async def startup_event():
    await producer.start()
    await consumer.start()
    app.state.consumer_task = asyncio.create_task(consume_forever())


@app.on_event("shutdown")
async def shutdown_event():
    app.state.consumer_task.cancel()
    await producer.stop()
    await consumer.stop()


async def consume_forever():
    try:
        # Get stream of messages from consumer
        async for msg in consumer:
            print(f"Received: {msg.value.decode()}")
    except asyncio.CancelledError:
        pass


@app.post("/send_message/{message}")
async def send_message(message: str):
    await producer.send_and_wait("my_topic", message.encode())
