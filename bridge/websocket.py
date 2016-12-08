import functools
import json
import time

from tornado import (
    escape,
    gen,
    httpclient,
    httpserver,
    httputil,
    ioloop,
    websocket,
)

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import socket

DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60


class Client():
    def __init__(
            self, 
            url, 
            *, 
            connect_timeout=DEFAULT_CONNECT_TIMEOUT, 
            request_timeout=DEFAULT_REQUEST_TIMEOUT,
            message_handler=None,
            connect_handler=None
        ):
        self.message_handler = message_handler
        self.connect_handler = connect_handler
        self.url = url
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout

    def connect(self):
        """ Connect to the server. """

        headers = httputil.HTTPHeaders({'Content-Type': 'application/json'})
        request = httpclient.HTTPRequest(
            url=self.url,
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
            else:
                self._on_message(msg)

    def _on_connection_success(self):
        """ This is called on successful connection of the server. """
        if self.connect_handler:
            self.connect_handler()

    def _on_message(self, message):
        if self.message_handler:
            self.message_handler(message)

    def _on_connection_close(self):
        """ This is called when server closed the connection. """
        print("connection was closed, reconnecting...")

        self.connect()

    def _on_connection_error(self, exception):
        """ This is called in case if connection to the server could not established. """
        print("connection failed: {}".format(exception))
        time.sleep(1)
        self.connect()

def make_server(connect_handler=None, message_handler=None, disconnect_handler=None): 
    class Server(tornado.websocket.WebSocketHandler):
        def open(self):
            print('new connection')
            if connect_handler:
                return connect_handler(self)
          
        def on_message(self, message):
            if message_handler:
                return message_handler(json.loads(message))
     
        def on_close(self):
            print('connection closed')
            if disconnect_handler:
                return disconnect_handler(self)
     
        def check_origin(self, origin):
            return True
    return Server



 