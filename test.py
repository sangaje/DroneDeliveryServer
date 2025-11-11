import asyncio
import time

async def say_after(delay, what):
    i = 0
    for i in range(delay):
        print('1', end="")
    await asyncio.sleep(1)
    for i in range(delay):
        print('1', end="")

    print(what)
async def say_after2(delay, what):
    i = 0
    for i in range(delay):
        print('2', end="")
    await asyncio.sleep(1)
    for i in range(delay):
        print('2', end="")
    print(what)
async def say_world():
    print("before gather")

async def main():
    print(f"started at {time.strftime('%X')}")



    asyncio.task = say_after(200, 'hello')
    b = say_after2(200, 'world')

    
    await say_world()
    await a
    await b

    

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())