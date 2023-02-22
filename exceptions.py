class Error(Exception):
    """Стандартный класс исключений."""
    pass


class StatusCodeUnknown(Exception):
    """Статус домашней работы неизвестен."""
    pass


class StatusError(Exception):
    """Ошибка в статусе."""
    pass


class StatusNotInDict(Exception):
    """Отсутствие ключа в статусе."""
    pass