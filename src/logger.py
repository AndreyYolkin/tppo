import logging
import os
from pathlib import Path

class Logger:
    def __init__(self, name, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
    def add_file_handler(self, filename):
        working_directory = os.getcwd()
        file_path = os.path.join(working_directory, filename)
        folder = os.path.dirname(file_path)
        p = Path(folder)
        p.mkdir(exist_ok=True, parents=True)
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)