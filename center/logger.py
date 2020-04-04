import logging
import logging.handlers

class Logger(object):
    def __init__(self, name="center"):
        self.logger = logging.getLogger("%s_logger" % name)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        self.err_handler = logging.FileHandler(filename="%s_error.log" % name)
        self.err_handler.setLevel(logging.ERROR)
        self.err_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.err_handler)

        self.warn_handler = logging.FileHandler(filename="%s_warning.log" % name)
        self.warn_handler.setLevel(logging.WARNING)
        self.warn_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.warn_handler)
        

    def Error(self, msg, e = None, extra=None, screen=False):
        self.logger.error(msg, exc_info=e, stack_info=False, extra=extra)
        if screen:
            print(msg, extra if extra else "")

    def Warning(self, msg, extra=None, screen=False):
        self.logger.warning(msg, extra=extra)
        if screen:
            print(msg, extra if extra else "")