"""A separate terminal for every websocket opened.
"""
import tornado.web
# This demo requires tornado_xstatic and XStatic-term.js
import tornado_xstatic

from terminado import TermSocket, UniqueTermManager
from common_demo_stuff import run_and_show_browser, STATIC_DIR, TEMPLATE_DIR

class TerminalPageHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("termpage.html", static=self.static_url,
                           xstatic=self.application.settings['xstatic_url'],
                           ws_url_path="/websocket")

def main(argv):
    print("Starting MazinGame...")
    term_manager = UniqueTermManager(shell_command=['bash','start_script.sh'])
    handlers = [
                (r"/websocket", TermSocket,
                     {'term_manager': term_manager}),
                (r"/", TerminalPageHandler),
                (r"/xstatic/(.*)", tornado_xstatic.XStaticFileHandler,
                     {'allowed_modules': ['termjs']})
                #(r"/favicon.ico", tornado.web.StaticFileHandler, {'path': "./templates/favicon.ico"})
               ]
    app = tornado.web.Application(handlers, static_path=STATIC_DIR,
                      template_path=TEMPLATE_DIR,
                      xstatic_url = tornado_xstatic.url_maker('/xstatic/'))
    app.listen(8080, '0.0.0.0')
    loop = tornado.ioloop.IOLoop.instance()
    try:
        loop.start()
    except KeyboardInterrupt:
        print(" Shutting down on SIGINT")
    finally:
        term_manager.shutdown()
        loop.close()
    #run_and_show_browser("http://0.0.0.0:8080/", term_manager)

if __name__ == '__main__':
    main([])