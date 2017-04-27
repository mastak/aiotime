import asyncio
import inspect
from asyncio.coroutines import CoroWrapper


def inspect_coroutine(coro):
    """stolen from asyncio.coroutines """
    assert asyncio.iscoroutine(coro)

    if not hasattr(coro, 'cr_code') and not hasattr(coro, 'gi_code'):
        # Most likely a built-in type or a Cython coroutine.

        # Built-in types might not have __qualname__ or __name__.
        coro_name = getattr(
            coro, '__qualname__',
            getattr(coro, '__name__', type(coro).__name__))
        coro_name = '{}()'.format(coro_name)

        running = False
        try:
            running = coro.cr_running
        except AttributeError:
            try:
                running = coro.gi_running
            except AttributeError:
                pass

        if running:
            return '{} running'.format(coro_name)
        else:
            return coro_name

    coro_name = None
    if isinstance(coro, CoroWrapper):
        func = coro.func
        coro_name = coro.__qualname__
        if coro_name is not None:
            coro_name = '{}()'.format(coro_name)
    else:
        func = coro

    if coro_name is None:
        coro_name = asyncio.events._format_callback(func, (), {})

    try:
        coro_code = coro.gi_code
    except AttributeError:
        coro_code = coro.cr_code

    try:
        coro_frame = coro.gi_frame
    except AttributeError:
        coro_frame = coro.cr_frame

    filename = coro_code.co_filename
    lineno = 0
    if (isinstance(coro, CoroWrapper) and
            not inspect.isgeneratorfunction(coro.func) and
            coro.func is not None):
        source = asyncio.events._get_function_source(coro.func)
        if source is not None:
            filename, lineno = source
        if coro_frame is not None:
            coro_repr = ('%s running, defined at %s:%s'
                         % (coro_name, filename, lineno))
    elif coro_frame is not None:
        lineno = coro_frame.f_lineno
    else:
        lineno = coro_code.co_firstlineno

    # return coro_repr
    return {
        'name': coro_name,
        'filename': filename,
        'lineno': lineno,
    }
