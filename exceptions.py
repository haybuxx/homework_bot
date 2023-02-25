class StatusCodeUnknown(Exception):
    """Статус домашней работы неизвестен."""
    pass


class StatusError(Exception):
    """Ошибка в статусе."""
    pass


class StatusNotInDict(Exception):
    """Отсутствие ключа в статусе."""
    pass


class ErrorResponse(Exception):
    """Ошибка в запросе к API."""