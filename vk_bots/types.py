import typing
from types import MethodType, FunctionType

class Data():
    def __init__(self, *args, **kwargs):
        self._dict: dict = kwargs
        self._list: list = list(args)

        for k, v in kwargs.items():
            self.__setattr__(k, v)
    def __getitem__(self, key: str | int) -> typing.Any:
        return self._list[key] if type(key) == int else self._dict[key]
    def __setitem__(self, key: str | int, value: typing.Any) -> None:
        if type(key) == int:
            try: self._list[key] = value
            except IndexError: self._list.insert(key, value)
        else:
            self._dict[key] = value

    def __contains__(self, key: str):
        return key in self._dict
    
    def __delattr__(self, key: str):
        del self._dict[key]
    def __delitem__(self, key: str | int):
        if type(key) == int:
            del self._list[key]
        else:
            del self._dict[key]

class EnumMeta(type):
    def _find_value_path(self, value: typing.Any) -> str | None:
        _path = None
        for attrName in self._get_enum_values():
            attrValue = getattr(self, attrName)
            if type(attrValue) == EnumMeta:
                _temp = attrValue._find_value_path(value)
                if _temp == None: continue
                else: 
                    _path = f"{attrValue.__name__}_" + _temp
                    break
            elif attrValue == value:
                return str(attrName)
        return _path
    def _get_enum_values(self) -> list[str]:
        return [_attrName for _attrName in dir(self) if not _attrName.startswith('_')]
    def __setattr__(self, name: str, value: typing.Any) -> None: return
    def __contains__(self, value: typing.Any) -> bool:
        for attrName in self._get_enum_values():
            if getattr(self, attrName) == value:
                return True
        return False
    def __iter__(self):
        for attrName in self._get_enum_values():
            yield (attrName, getattr(self, attrName))
class Enum(metaclass=EnumMeta):
    def __new__(cls, *args, **kwargs): return cls
    

class CommandParam(object):
    """Creates a dict with format of Command Parameter"""
    def __new__(cls, name: str, is_optimal: bool, default_value: typing.Any = None) -> dict:
        return {'name': str(name), 'optimal': bool(is_optimal), 'default': default_value}
    def __init__(self, name: str, is_optimal: bool, default_value: typing.Any = None): pass

class Command(object):
    """Creates a dict with format of Command"""
    def __new__(cls, name: str, handler: typing.Callable, about: str = '', params: list[CommandParam] = []) -> dict:
        return {'name': str(name), 'about': str(about), 'params': params, 'handler': handler}
    def __init__(self, name: str, handler: typing.Callable, about: str = '', params: list[CommandParam] = []): pass