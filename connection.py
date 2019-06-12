import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
import manager
import signal
import sys
from tornado.ioloop import IOLoop


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    counter = 0

    def open(self, *args):
        WebSocketHandler.counter += 1
        self.id = WebSocketHandler.counter
        print "Client %s connected." % self.id
        manager.Manager.add_client(self.id, self)

    def on_message(self, message):
        manager.Manager.handle_message(self.id, message)

    def on_close(self):
        manager.Manager.remove_client(self.id)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "templates/"}),
            (r"/", IndexHandler),
            (r"/ws", WebSocketHandler)
        ]

        settings = {
            'template_path': 'templates'
        }
        tornado.web.Application.__init__(self, handlers, **settings)

def on_shutdown():
    print('Shutting down')
    manager.Manager.setActFlag(False)
    IOLoop.instance().stop()
    sys.exit(0)

if __name__ == '__main__':
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(9090)
    ioloop = tornado.ioloop.IOLoop.instance()

    signal.signal(signal.SIGINT, lambda sig, frame: ioloop.add_callback_from_signal(on_shutdown))

    ioloop.start()
