
import logging.handlers
import os
import queue
from PyQt6 import QtWidgets
import sys
def configure_logger(location):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    que = queue.Queue(-1)
    queue_handler = logging.handlers.QueueHandler(que)
    file_handler = logging.FileHandler(
        os.path.join(location, "socket_server.log"), mode="w"
    )
    queue_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(threadName)s %(module)s.%(funcName)s:%(lineno)d %(message)s")
    )

    queuelistener = logging.handlers.QueueListener(que, file_handler)
    logger.addHandler(queue_handler)
    return queuelistener

def uncaught_exception(exctype, value, tb):
    logger.error("Uncaught exception", exc_info=(exctype, value, tb))
    queuelistener.stop()
    sys.__excepthook__(exctype, value, tb)
    exit(1)



if __name__=='__main__':
    if getattr(sys,'frozen',False):
        apppath=os.path.dirname(sys.executable)   
    else:
        apppath=os.path.dirname(__file__)
    queuelistener=configure_logger(apppath)
    queuelistener.start()
    logger=logging.getLogger(__name__)
    import component
    app = QtWidgets.QApplication(sys.argv)
    ui = component.Ui_MainWindow_2()
    window=QtWidgets.QMainWindow()
    ui.setupUi(window)
    sys.excepthook=uncaught_exception
    window.show()
    ret=app.exec()
    logger.debug(f"end with {ret}")
    queuelistener.stop()

    sys.exit(ret)