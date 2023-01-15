from loguru import logger

fmt = "[{time:YYYY-MM-DD HH:mm:ss}] {message} {extra[data]}"
action_log = logger
action_log.add('../log/action.log', level='DEBUG', format=fmt)
