import asyncio

async def producer(queue: asyncio.Queue[int]):
    for i in range(100):
        await queue.put(i)  # blocks when queue is full

async def consumer(queue: asyncio.Queue[int]):
    while True:
        item = await queue.get()  # blocks when queue is empty
        await asyncio.sleep(0.1)  # simulate slow processing

async def main():
    queue: asyncio.Queue[int] = asyncio.Queue(maxsize=5)  # bounded
    await asyncio.gather(producer(queue), consumer(queue))
