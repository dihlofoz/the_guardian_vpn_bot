import logging

def setup_logger(log_file: str = "bot.log"):
    # --- Отключаем все стандартные логи от aiogram и httpx в консоли ---
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # --- Общий логгер для записи в файл ---
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Можно INFO, WARNING, ERROR, если нужно
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # --- File handler ---
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # --- Stream handler (опционально) ---
    # Можно оставить пустым или тоже писать только WARNING+ в консоль
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger