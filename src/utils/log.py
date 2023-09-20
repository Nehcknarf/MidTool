import logging.handlers


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.handlers.TimedRotatingFileHandler(
    filename="midtool.log",
    when="D",
    interval=90
)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="%(asctime)s %(module)s.%(funcName)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler.setFormatter(formatter)

logger.addHandler(handler)
