#!/usr/bin/env python3

import asyncio
import websockets

@asyncio.coroutine
def hello(websocket, path):
    print(path)
    i = 0
    while True:
        yield from websocket.send("{}".format(i))
        i += 1
        yield from asyncio.sleep(1)

start_server = websockets.serve(hello, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
