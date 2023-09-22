import logging
from settings import settings

def configure_logger():

    logging.basicConfig(format="'%(asctime)s - %(name)s - %(levelname)s - %(message)s'",
                        level=settings.log_level)

    logging.getLogger(__name__).info(f'Logger configured with loglevel {settings.log_level}.')
