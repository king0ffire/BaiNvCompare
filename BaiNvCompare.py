import logging.handlers
import os
import queue
from PyQt6 import QtWidgets
import sys


def configure_logger(location:str, level:int=logging.DEBUG):
    logger = logging.getLogger()
    logger.setLevel(level)

    que = queue.Queue(-1)
    queue_handler = logging.handlers.QueueHandler(que)
    file_handler = logging.FileHandler(
        os.path.join(location, "BaiNvCompare.log"), mode="w"
    )
    queue_handler.setLevel(level)
    file_handler.setLevel(level)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(threadName)s %(module)s.%(funcName)s:%(lineno)d %(message)s"
        )
    )

    queuelistener = logging.handlers.QueueListener(que, file_handler)
    logger.addHandler(queue_handler)
    return queuelistener


def uncaught_exception(exctype, value, tb):
    logger.error("Uncaught exception", exc_info=(exctype, value, tb))
    queuelistener.stop()
    exit(0)
    sys.__excepthook__(exctype, value, tb)
    


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        apppath = os.path.dirname(sys.executable)
        queuelistener = configure_logger(apppath, logging.DEBUG)
    else:
        apppath = os.path.dirname(__file__)
        queuelistener = configure_logger(apppath)
    queuelistener.start()
    from ui import uisetter

    logger = logging.getLogger(__name__)
    app = QtWidgets.QApplication(sys.argv)
    app.setCursorFlashTime(1000)
    ui = uisetter.Ui_MainWindow_2()
    window = QtWidgets.QMainWindow()
    ui.setupUi(window)
    sys.excepthook = uncaught_exception
    window.show()
    ret = app.exec()
    logger.debug(f"end with {ret}")
    queuelistener.stop()

    sys.exit(ret)
