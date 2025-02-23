import logging
import sys

log_format = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

logging.basicConfig(level=logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
