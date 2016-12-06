import tornado

from websocket import Client


def main():
    client = Client()
    client.connect('ws://echo.websocket.org')

    def test_callback():
        client.send("hello")

    main_loop = tornado.ioloop.IOLoop.instance()
    sched = tornado.ioloop.PeriodicCallback(test_callback, 1000, io_loop = main_loop)
    sched.start()

    try:
        main_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()

