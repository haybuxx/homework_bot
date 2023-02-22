class Error(Exception):
    """Стандартный класс исключений."""
    pass


class NotListError(Exception):
    """Пустой список домашних работ."""
    pass


class StatusCodeUnknow(Exception):
    """Статус домашней работы неизвестен."""
    pass


class StatusError(Exception):
    """Ошибка в статусе."""
    pass


class StatusNotInDict(Exception):
    """Отсутствие ключа в статусе."""
    pass