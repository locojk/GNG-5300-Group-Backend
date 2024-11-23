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
        初始化格式化器
        :param json_format: 如果为 True，则文件日志使用 JSON 格式，否则为标准格式
        """
        super().__init__()
        self.json_format = json_format

    def format(self, record):
        # 通用的详细日志字段
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "log_level": record.levelname,
            "log_id": str(uuid.uuid4()),
            "file": os.path.basename(record.pathname),  # 文件名
            "function": record.funcName,  # 函数名
            "line": record.lineno,  # 行号
            "message": record.getMessage(),  # 日志消息
        }

        # 如果是 JSON 格式，直接返回 JSON 字符串
        if self.json_format:
            return json.dumps(log_record)

        # 标准格式返回字符串形式，包含详细信息
        return (
            f"[{log_record['timestamp']}] {log_record['log_level']} "
            f"[{log_record['file']}:{log_record['line']} - {log_record['function']}] "
            f"{log_record['message']}"
        )


class Logger:
    def __init__(self, name, level=None, log_dir="logs", log_file="application.log", audit_log_file="audit.log"):
        """
        初始化 Logger
        :param name: 日志名称（模块名）
        :param level: 日志级别
        :param log_dir: 日志目录
        :param log_file: 应用日志文件名
        :param audit_log_file: 审计日志文件名
        """
        if level is None:
            level = logging.DEBUG if os.getenv('DEBUG', False) else logging.INFO

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 应用日志
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        app_log_path = os.path.join(log_dir, log_file)
        app_file_handler = RotatingFileHandler(app_log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        app_file_handler.setFormatter(JsonFormatter(json_format=True))  # 文件使用 JSON 格式
        self.logger.addHandler(app_file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter(json_format=False))  # 控制台使用标准格式
        self.logger.addHandler(console_handler)

        # 审计日志
        audit_log_path = os.path.join(log_dir, audit_log_file)
        self.audit_logger = logging.getLogger(f"{name}_audit")
        self.audit_logger.setLevel(level)
        audit_file_handler = RotatingFileHandler(audit_log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        audit_file_handler.setFormatter(JsonFormatter(json_format=True))  # 文件使用 JSON 格式
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
        self.logger.setLevel(level)
        self.audit_logger.setLevel(level)

    def audit_log(self, user_id, action, resource, status, details=None):
        """
        记录审计日志
        :param user_id: 用户 ID
        :param action: 操作类型
        :param resource: 操作资源
        :param status: 操作状态
        :param details: 其他详情
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
        """获取当前时间的字符串格式"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
