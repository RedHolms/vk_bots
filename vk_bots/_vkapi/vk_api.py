import requests
from .exceptions import *

API_URL = 'https://api.vk.com/'
API_METHOD_URL = API_URL + 'method/'

class VkAPI(object):
    def __new__(cls): return cls

    class ApiSession(object):
        def __init__(self, token: str, version: str = '5.131', httpSession: requests.Session = None) -> None:
            self.token = token
            self.v = version
            self.httpSession = httpSession if type(httpSession) == requests.Session else requests.Session()
            self.method = VkAPI.VkApiMethod(self)
        def methodRequest(self, methodName: str, params: dict, requestMode: str = 'get', safeMode: bool = False, returnRaw: bool = False):
            methodName = str(methodName)
            requestMode = str(requestMode)
            assert type(params) == dict, (TypeError, "Invalid type of param #2 'params': Expected 'dict'")

            if not 'v' in params: params['v'] = self.v
            if not 'access_token' in params: params['access_token'] = self.token

            response = self.httpSession.request(requestMode, API_METHOD_URL + methodName, params)

            if response.status_code not in range(200, 299):
                raise ConnectionError(response)

            json = response.json()

            if 'error' in json and not safeMode:
                raise ApiResponseError(json)

            return response if returnRaw else json['response']
        def execVKScript(self, code: str):
            return self.methodRequest("execute", {'code': str(code)})

    class VkApiMethod(object): # СПИЖЕНО ИЗ МОДУЛЯ 'vk_api' ОТ 'python273'
        __slots__ = ('_vk', '_method')

        def __init__(self, vk, method=None):
            self._vk: VkAPI.ApiSession = vk
            self._method = method

        def __getattr__(self, method: str):
            if '_' in method:
                m = method.split('_')
                method = m[0] + ''.join(i.title() for i in m[1:])

            return VkAPI.VkApiMethod(
                self._vk,
                (self._method + '.' if self._method else '') + method
            )

        def __call__(self, **kwargs):
            for k, v in kwargs.items():
                if isinstance(v, (list, tuple)):
                    kwargs[k] = ','.join(str(x) for x in v)

            return self._vk.methodRequest(self._method, kwargs)