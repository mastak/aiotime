import asyncio
import logging
import socket

import aiohttp

try:
    import ujson as json
except ImportError:
    import json

HOSTNAME = socket.gethostname()
logger = logging.getLogger('aiotime')


class NewRelicHandler:

    URL = 'https://platform-api.newrelic.com/platform/v1/metrics'

    def __init__(self, name, license_key, keepalive=True, verify_ssl=True,
                 timeout=30, duration=60, limit=(50, 70)):
        self._name = name
        self._license_key = license_key
        self._keepalive = keepalive
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._duration = duration
        self._limit = limit

        self._loop = None
        self._records = []
        self._sender = None
        self._client_session = None

    def init_sender(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._sender = asyncio.ensure_future(self._sender_worker(), loop=self._loop)

    def add_record(self, component, total_time):
        # if len(self._records) > self._limit[1]:
        #     logger.warning("NewRelicHandler queue of records if full ({})".
        #                    format(len(self._records)))
        #     return None

        self._records.append((component, total_time))

        # if len(self._records) > self._limit[0]:
        #     asyncio.ensure_future(self._flush(), loop=self._loop)

    def __call__(self, component, total_time, *, loop=None):
        if self._sender is None:
            self.init_sender(loop)
        return self.add_record(component, total_time)

    @asyncio.coroutine
    def _sender_worker(self):
        while True:
            yield from self._flush()
            yield from asyncio.sleep(self._duration)

    def _client_session(self):
        if not self._keepalive or \
                (self._client_session is None or self._client_session.closed):
            connector = aiohttp.TCPConnector(verify_ssl=self._verify_ssl,
                                             loop=self._loop)
            self._client_session = aiohttp.ClientSession(connector=connector,
                                                         loop=self._loop)
        return self._client_session

    @asyncio.coroutine
    def _flush(self):
        if len(self._records) is 0:
            return

        metrics = {}
        for component, times in self._records:
            max_, min_ = max(times), min(times)
            metrics['Component/{}'.format(component)] = dict(
                total=sum(times),
                count=len(times),
                max=max_,
                min=min_,
                sum_of_squares=min_**2 + max_**2
            )
        self._records = []

        data = {
            "agent": {
                "host": HOSTNAME,
                "version": "1.0.0"
            },
            "components": [{
                "name": self._name,
                "guid": "com.darwinmonroy.aiometrics",
                "duration": self._duration,
                "metrics": metrics
            }]
        }
        yield from self._send(data)

    @asyncio.coroutine
    def _send(self, data):
        headers = (
            ('X-License-Key', self._license_key),
            ('Content-Type', 'application/json'),
            ('Accept', 'application/json'),
        )

        session = self._client_session()
        try:
            with aiohttp.Timeout(self._timeout):
                resp = session.post(self.URL, data=json.dumps(data),
                                    compress=False, headers=headers)
                try:
                    text = yield from resp.text()
                finally:
                    yield from resp.release()
                if resp.status != 200:
                    logger.warning("Error newrelic response %s", text)
        except Exception as exc:
            logger.exception(exc)
        finally:
            if not self._keepalive:
                yield from session.close()
