import logging
import os

def setup_logging(log_folder="logs", log_file="bot.log", level=logging.INFO):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_folder, log_file)),
            logging.StreamHandler(),
        ],
        encoding='utf-8'
    )

    return logging.getLogger(__name__)

