import logging
import sys

def setup_logging(level=logging.INFO):
    """
    Configure global logger.
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout) # for docker
        ],
        force=True # for multiprocessing
    )