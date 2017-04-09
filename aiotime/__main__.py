import asyncio
import logging
import time

import coloredlogs

from aiotime import coro_time
from aiotime.handlers import logging_handler
from aiotime.tasks import print_res

coloredlogs.install(level=logging.INFO)


decor = coro_time(handlers=(logging_handler,))

async def some(aaa):
    await some2(123)


@decor
async def some2(bb):
    # time.sleep(0.1)
    await some3()

# @trace_coro
async def some3():
    # time.sleep(0.1)
    await some4(777)
    return await some5(2, 5)


async def some4(c):
    await asyncio.sleep(0.1)
    time.sleep(0.1)
    return 3


async def some5(a, b):
    await asyncio.sleep(0.1)
    time.sleep(0.1)
    return 3


# # @trace_coro
# async def bar():
#     await asyncio.sleep(2)
#     time.sleep(0.2)
#     return 3

loop = asyncio.get_event_loop()
results, _ = loop.run_until_complete(asyncio.wait([some(111)]))
# for r in results:
#     print("Result: {}".format(r.result()))
