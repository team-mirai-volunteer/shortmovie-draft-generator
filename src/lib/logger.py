import logging
import sys

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer
import streamlit as st
import random
import socket
from datetime import datetime

NON_LOGIN_USERNAME = "Unknown"


def get_outbound_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "127.0.0.1"


ip = socket.inet_aton(get_outbound_ip())


def generate_log_id():
    now = datetime.now()
    year_to_sec = now.strftime("%Y%m%d%H%M%S")
    millisec = now.strftime("%f")[:3]
    ip_str = "".join([f"{octet:03d}" for octet in ip])
    rand_str = f"{random.randint(0, 0xFFFFFF):06x}"
    return (year_to_sec + ip_str + millisec + rand_str).upper()


def add_username(logger, method_name, event_dict):
    username = getattr(st.session_state, "username", NON_LOGIN_USERNAME)
    event_dict["username"] = username if username else NON_LOGIN_USERNAME
    return event_dict


def add_log_id(logger, method_name, event_dict):
    if "log_id" not in st.session_state:
        st.session_state.log_id = generate_log_id()
    event_dict["log_id"] = st.session_state.log_id
    return event_dict


# 一度だけ実行するため、st.cache_resourceを使用している
@st.cache_resource
def configure_logger() -> structlog.BoundLogger:
    """
    structlogを使用してロガーを初期化し、標準出力にログを出力する設定を行う関数。
    ユーザー名とログIDをログメッセージに含めます。
    """
    structlog.configure(
        processors=[
            add_username,
            add_log_id,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    handler_stdout = logging.StreamHandler(sys.stdout)
    handler_stdout.setFormatter(structlog.stdlib.ProcessorFormatter(processor=ConsoleRenderer()))

    handler_file = logging.FileHandler("application.log")
    handler_file.setFormatter(structlog.stdlib.ProcessorFormatter(processor=JSONRenderer()))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler_stdout)
    root_logger.addHandler(handler_file)
    root_logger.setLevel(logging.INFO)
    root_logger.propagate = False


if __name__ == "__main__":
    print(get_outbound_ip())
    print(generate_log_id())
    configure_logger()

    logger = structlog.get_logger()
    logger.info("test")
    logger.error("error")
