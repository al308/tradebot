# logger_setup.py
import logging


def setup_logger():
    # Create a logger
    logger = logging.getLogger("tradebot")
    logger.setLevel(logging.INFO)

    # Check if logger already has handlers (to avoid duplicate logs)
    if not logger.hasHandlers():
        # Create handlers for both console and file
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler("tradebot.log")

        # Set level for handlers
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

        # Create a formatter and add it to the handlers
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
