import asyncio
import functools
import inspect
import logging
import time
from asyncio import coroutines


logger = logging.getLogger('aiotime')


def coro_time(handlers=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # _print_vals(inspect.currentframe().f_back)
            # print("/"*80)
            # _print_vals(inspect.stack())
            # print(func)
            # print(inspect.getouterframes(func.cr_frame))
            # outer_frames = inspect.getouterframes(inspect.currentframe())
            # for f in outer_frames:
            #     print(inspect.getframeinfo(f.frame))
            # print(len(outer_frames), "\n\n")
            # print(inspect.currentframe().f_back)

            task = TimedTask(func(*args, **kwargs))
            task.add_done_callback(functools.partial(_results_handler, handlers))
            return await task
        return wrapper
    return decorator


def _results_handler(handlers, task):
    if handlers is None:
        return

    for h in handlers:
        h(task)


def print_res(fut):
    # print(_get_vals(fut._coro))
    # print(_get_vals(fut._coro.cr_code))
    # import ipdb; ipdb.set_trace()

    async def f():
        print("Task done", coroutines._format_coroutine(fut._coro), fut._run_info, fut.get_time_reault())
        # print(inspect.getouterframes(fut._coro.cr_frame))

    asyncio.ensure_future(f())
    # print("Task done", dir(fut))


class TimedTask(asyncio.Task):
    def __init__(self, *args, **kwargs):
        super(TimedTask, self).__init__(*args, **kwargs)
        self._timeit = 0.0
        self._run_info = None

    def get_time_reault(self):
        return self._timeit

    def _step(self, *args, **kwargs):
        # print("="*80)
        # for i, v in _get_vals(self._coro.cr_frame).items():
        #     print(i, v)
        #     print("\n\n")

        start = time.time()
        result = super()._step(*args, **kwargs)
        self._timeit += time.time() - start


        # print("-"*50)
        # print(inspect.getouterframes(inspect.currentframe()))

        # for i, v in _get_vals(self._coro.cr_frame).items():
        #     print(i, v)
        #     print("\n\n")
        # print("+"*80)

        if self._run_info is None:
            # _frame = self._coro.cr_frame
            # _frame = inspect.getouterframes(self._coro.cr_frame)
            # frame_info = inspect.getframeinfo(_frame)
            # _print_vals(frame_info)
            # print(frame_info._asdict())
            self._run_info = 1
        return result


def _get_vals(obj):
    return {i: getattr(obj, i) for i in dir(obj) if not i.startswith("__")}


def _print_vals(obj):
    for i in dir(obj):
        if i.startswith("__"):
            continue
        print("\n\n")
        print(i, getattr(obj, i))
    # return [i for i in dir(obj) if not i.startswith("__")]