import logging
import os
import uuid
from logging.handlers import RotatingFileHandler
import json
from utils.env_loader import load_platform_specific_env

load_platform_specific_env()


class JsonFormatter(logging.Formatter):
    def __init__(self, json_format=False):
        """
        Initialize the formatter.

        :param json_format: If True, file logs will use JSON format; otherwise, standard format is used.
        """
        super().__init__()
        self.json_format = json_format

    def format(self, record):
        # Common detailed log fields
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "log_level": record.levelname,
            "log_id": str(uuid.uuid4()),
            "file": os.path.basename(record.pathname),  # File name
            "function": record.funcName,  # Function name
            "line": record.lineno,  # Line number
            "message": record.getMessage(),  # Log message
        }

        # Return JSON string if JSON format is enabled
        if self.json_format:
            return json.dumps(log_record)

        # Return a detailed string for standard formatting
        return (
            f"[{log_record['timestamp']}] {log_record['log_level']} "
            f"[{log_record['file']}:{log_record['line']} - {log_record['function']}] "
            f"{log_record['message']}"
        )


class Logger:
    def __init__(self, name, level=None, log_dir="logs", log_file="application.log", audit_log_file="audit.log"):
        """
        Initialize the Logger.

        :param name: Logger name (module name)
        :param level: Logging level
        :param log_dir: Directory for log files
        :param log_file: Application log file name
        :param audit_log_file: Audit log file name
        """
        if level is None:
            level = logging.DEBUG if os.getenv('DEBUG', False) else logging.INFO

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Application logs
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        app_log_path = os.path.join(log_dir, log_file)
        app_file_handler = RotatingFileHandler(app_log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        app_file_handler.setFormatter(JsonFormatter(json_format=True))  # Use JSON format for file logs
        self.logger.addHandler(app_file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter(json_format=False))  # Use standard format for console logs
        self.logger.addHandler(console_handler)

        # Audit logs
        audit_log_path = os.path.join(log_dir, audit_log_file)
        self.audit_logger = logging.getLogger(f"{name}_audit")
        self.audit_logger.setLevel(level)
        audit_file_handler = RotatingFileHandler(audit_log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        audit_file_handler.setFormatter(JsonFormatter(json_format=True))  # Use JSON format for audit file logs
        self.audit_logger.addHandler(audit_file_handler)

    def info(self, message):
        self.logger.info(message, stacklevel=2)

    def debug(self, message):
        self.logger.debug(message, stacklevel=2)

    def warning(self, message):
        self.logger.warning(message, stacklevel=2)

    def error(self, message):
        self.logger.error(message, stacklevel=2)

    def critical(self, message):
        self.logger.critical(message, stacklevel=2)

    def set_level(self, level):
        """Set the logging level for both application and audit loggers."""
        self.logger.setLevel(level)
        self.audit_logger.setLevel(level)

    def audit_log(self, user_id, action, resource, status, details=None):
        """
        Record an audit log.

        :param user_id: User ID
        :param action: Type of action performed
        :param resource: Target resource of the action
        :param status: Status of the action
        :param details: Additional details (optional)
        """
        audit_record = {
            "timestamp": self._get_current_time(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details,
        }
        self.audit_logger.info(json.dumps(audit_record), stacklevel=2)

    @staticmethod
    def _get_current_time():
        """Get the current time in ISO 8601 format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
