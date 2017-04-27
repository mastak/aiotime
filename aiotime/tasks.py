import asyncio
import functools
import inspect
import logging
import time
from inspect import getcoroutinelocals


logger = logging.getLogger('aiotime')


def coro_time_(handlers=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # _print_vals(inspect.currentframe().f_back)
            # print("/"*80)
            # _print_vals(inspect.stack())
            # print(func)
            # print(inspect.getouterframes(func.cr_frame))
            outer_frames = inspect.getouterframes(inspect.currentframe())
            for f in outer_frames:
                print(inspect.getframeinfo(f.frame))
            # print(len(outer_frames), "\n\n")
            # print(inspect.currentframe().f_back)

            task = TimedTask(func(*args, **kwargs))
            task.add_done_callback(functools.partial(_results_handler, handlers))
            return await task
        return wrapper
    return decorator


def coro_time(func=None, *, handlers=None):
    if func is None:
        return functools.partial(coro_time, handlers=handlers)

    @functools.wraps(func)
    @asyncio.coroutine
    def wrapper(*args, **kwargs):
        task = TimedTask(func(*args, **kwargs))

        stack_function = []
        outer_frames = inspect.getouterframes(inspect.currentframe())
        for f in outer_frames:
            traceback = inspect.getframeinfo(f.frame)
            stack_function.append(traceback.function)
            print(inspect.getframeinfo(f.frame))

        print("Stack functions", stack_function)
        print("\n\n")

        run_traceback = inspect.getframeinfo(inspect.currentframe().f_back)
        local_vars = str(getcoroutinelocals(task._coro))[:200]

        task.add_done_callback(functools.partial(_results_handler, handlers, local_vars, run_traceback))
        return (yield from task)
    return wrapper



def _results_handler(handlers, local_vars, run_traceback, task):
    if handlers is None:
        return

    for h in handlers:
        h(task, local_vars, run_traceback)


class TimedTask(asyncio.Task):
    def __init__(self, *args, **kwargs):
        super(TimedTask, self).__init__(*args, **kwargs)
        self._timeit = 0.0
        self._run_info = None

    def get_time_result(self):
        return self._timeit

    def _step(self, *args, **kwargs):
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
