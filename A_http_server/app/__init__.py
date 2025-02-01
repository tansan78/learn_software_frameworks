import logging


log_format = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

logging.basicConfig(level=logging.DEBUG)
