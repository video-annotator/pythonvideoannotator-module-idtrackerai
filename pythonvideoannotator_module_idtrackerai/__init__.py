import logging
from confapp import conf

logger = logging.getLogger(__name__)
logger.setLevel(conf.APP_LOG_HANDLER_LEVEL)

from .settings import IDTRACKERAI_SHORT_KEYS

conf.SHORT_KEYS.update(IDTRACKERAI_SHORT_KEYS)