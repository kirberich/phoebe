from tornado import (
    escape,
    gen,
    httpclient,
    httputil,
    ioloop,
    websocket
)

import functools
import json
import time


DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60


class Client():
    def __init__(self, *, connect_timeout=DEFAULT_CONNECT_TIMEOUT, request_timeout=DEFAULT_REQUEST_TIMEOUT):
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout

    def connect(self, url):
        """ Connect to the server. """

        headers = httputil.HTTPHeaders({'Content-Type': 'application/json'})
        request = httpclient.HTTPRequest(
            url=url,
            connect_timeout=self.connect_timeout,
            request_timeout=self.request_timeout,
            headers=headers
        )
        ws_conn = websocket.WebSocketClientConnection(
            ioloop.IOLoop.current(),
            request
        )
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def send(self, json_data):
        """ Send message to the server """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')

        self._ws_connection.write_message(escape.utf8(json.dumps(json_data)))

    def close(self):
        """ Close connection. """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')

        self._ws_connection.close()

    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self._on_connection_close()
                break

            self._on_message(msg)

    def _on_message(self, msg):
        """ This is called when new message is available from the server. """
        print(msg)

    def _on_connection_success(self):
        """ This is called on successful connection of the server. """
        print("connection opened")
        self.send("hey")

    def _on_connection_close(self):
        """ This is called when server closed the connection. """
        print("connection closed")

    def _on_connection_error(self, exception):
        """ This is called in case if connection to the server could not established. """
        print("connection failed: {}".format(exception))

