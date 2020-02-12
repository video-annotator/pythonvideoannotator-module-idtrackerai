import logging
from confapp import conf

logger = logging.getLogger(__name__)
logger.setLevel(conf.APP_LOG_HANDLER_LEVEL)
logging.getLogger('idtrackerai').setLevel(logging.DEBUG)

from .settings import IDTRACKERAI_SHORT_KEYS

conf.SHORT_KEYS.update(IDTRACKERAI_SHORT_KEYS)
__version__ = "0.6.67"
