import logging
from aiotime.utils import inspect_coroutine

logger = logging.getLogger('aiotime')


def logging_handler(task, local_vars, run_traceback):
    info = inspect_coroutine(task._coro)
    logger.info("CORO STATS: %s %f, at %s:%d in %s as %s, local vars: %s. defined at %s:%s",
                info['name'], task.get_time_result(), run_traceback.filename, run_traceback.lineno,
                run_traceback.function, run_traceback.code_context, local_vars, info['filename'], info['lineno'])
