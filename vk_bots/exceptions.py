class VkBotsError(Exception):
    """Основной класс для всех исключений в модуле"""
    def __init__(self, about: str, *args, **kwargs):
        self.about = about
        self.args = args
        self.kwargs = kwargs
    def __str__(self):
        return self.about.format(*self.args, **self.kwargs)

class LongPollError(VkBotsError): 
    """Ошибка LongPoll"""
    pass

class LongPollDisabled(LongPollError):
    """LongPoll выключен в настройках сообщества"""
    def __init__(self, about: str = "LongPoll сервер выключен. Включите его в настройках сообщества и снова запустите программу"):
        super().__init__(about)

class LongPollInfoWasLost(LongPollError):
    def __init__(self, failedCode: int, about: str = "Информация LongPoll устарела. Обновите её, используя метод 'groups.getLongPollServer'. Failed: {failed}"):
        super().__init__(about, failed=failedCode)

class UnknownLongPollCycleError(LongPollError):
    def __init__(self, failedCode: int, about: str = "Произошла неизвестная ошибка LongPoll. Failed: {failed}"):
        super().__init__(about, failed=failedCode)

