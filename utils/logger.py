import logging
import os
import uuid
from logging.handlers import RotatingFileHandler


class SimpleFormatter(logging.Formatter):
    def format(self, record):
        # Construct a simple log format
        log_id = str(uuid.uuid4())  # Generate a unique log ID
        timestamp = self.formatTime(record, self.datefmt)
        log_level = record.levelname
        file = os.path.basename(record.pathname)
        function = record.funcName
        line = record.lineno
        message = record.getMessage()

        # Define the log message format
        return f"[{timestamp}] [{log_level}] [ID: {log_id}] [{file}:{function}:{line}] {message}"


class Logger:
    def __init__(self, name, log_dir='logs', app_log_file='application.log', audit_log_file='audit.log'):
        # Ensure log directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.app_log_path = os.path.join(log_dir, app_log_file)
        self.audit_log_path = os.path.join(log_dir, audit_log_file)

        # Initialize application logger
        self.app_logger = logging.getLogger(f'{name}_application')
        self.app_logger.setLevel(logging.DEBUG)
        app_log_handler = RotatingFileHandler(self.app_log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        app_log_handler.setFormatter(SimpleFormatter())
        self.app_logger.addHandler(app_log_handler)

        # Add console output for application logs
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(SimpleFormatter())
        self.app_logger.addHandler(console_handler)

        # Initialize audit logger
        self.audit_logger = logging.getLogger(f'{name}_audit')
        self.audit_logger.setLevel(logging.INFO)
        audit_log_handler = RotatingFileHandler(self.audit_log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        audit_log_handler.setFormatter(SimpleFormatter())
        self.audit_logger.addHandler(audit_log_handler)

        # Add console output for audit logs
        audit_console_handler = logging.StreamHandler()
        audit_console_handler.setFormatter(SimpleFormatter())
        self.audit_logger.addHandler(audit_console_handler)

    def info(self, message):
        """Log application info messages"""
        self.app_logger.info(message, stacklevel=2)

    def error(self, message):
        """Log application error messages"""
        self.app_logger.error(message, stacklevel=2)

    def debug(self, message):
        """Log application debug messages"""
        self.app_logger.debug(message, stacklevel=2)

    def audit(self, message):
        """Log audit messages"""
        self.audit_logger.info(message, stacklevel=2)

    def warning(self, message):
        """Log application warning messages"""
        self.app_logger.warning(message, stacklevel=2)

    def critical(self, message):
        """Log application critical messages"""
        self.app_logger.critical(message, stacklevel=2)

    def set_log_level(self, level):
        """Dynamically set application log level"""
        self.app_logger.setLevel(level)

    def set_audit_level(self, level):
        """Dynamically set audit log level"""
        self.audit_logger.setLevel(level)


# Instantiate the Logger class
logger = Logger(name='fitness-main.py')
