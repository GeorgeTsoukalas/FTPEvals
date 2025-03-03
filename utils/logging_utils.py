import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, name: str, log_dir: str = "logs", log_filename: str = "main.log", timestamp: str = None):
        self.name = name
        self.log_dir = log_dir
        # File handler
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') if timestamp is None else timestamp
        self.log_filename = log_filename
        
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        full_log_dir = os.path.join(self.log_dir, self.name, self.timestamp)
        # Create logs directory if it doesn't exist
        os.makedirs(full_log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(full_log_dir, f'{self.log_filename}')
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
    
    def clone_with(self, **kwargs):
        name = kwargs.get('name', self.name)
        log_dir = kwargs.get('log_dir', self.log_dir)
        log_filename = kwargs.get('log_filename', self.log_filename)
        timestamp = kwargs.get('timestamp', self.timestamp)
        return Logger(name, log_dir, log_filename, timestamp)
    
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
        
    def exception(self, message):
        """Log an exception with traceback information."""
        self.logger.exception(message) 