import requests
from requests.adapters import HTTPAdapter
from typing import Any, List, Tuple


class CatGPT:
    def __init__(self, qwen_bearer: str = '', yuanqi_bearer: str = '', yuanqi_id: str = ''):
        """
        通义千问及腾讯元器的聊天对话
        :param qwen_bearer: 通义千问的API-KEY
        :param yuanqi_bearer: 腾讯元器的Token
        :param yuanqi_id: 智能体ID
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        self.qwen_bearer = qwen_bearer
        self.yuanqi_bearer = yuanqi_bearer
        self.yuanqi_id = yuanqi_id

        self._session = requests.Session()
        option = HTTPAdapter(max_retries=3)
        self._session.mount('http://', adapter=option)
        self._session.mount('https://', adapter=option)

    def _request(self,
                 method: str,
                 url: str,
                 check_resp: bool = True,
                 return_type: int = 0,
                 timeout: int = 30,
                 encoding: str = 'utf-8',
                 **kwargs) -> Any:
        """
        发送网络请求
        :param method: 请求方式
        :param url: 接口地址
        :param check_resp: 是否校验状态码
        :param return_type: 数据返回格式类型，0表示不返回数据，1返回文本数据，2返回json数据，3返回字节数据
        :param timeout: 此次请求连接用时的时间范围（秒）
        :param encoding: 指定文本数据的解码方式
        :param kwargs: 发送网络请求的其它所需参数
        :return: 返回响应数据或提示状态码，通常0表示请求失败，可能是网络问题；-1代表此次请求成功，但未得到响应数据；
        1代表此次请求成功，成功得到响应数据；根据return_type返回相应类型数据
        """
        method = method.upper()
        try:
            if method == 'GET':
                resp = self._session.get(url, headers=self.headers, timeout=timeout, **kwargs)
            elif method == 'POST':
                resp = self._session.post(url, headers=self.headers, timeout=timeout, **kwargs)
            elif method == 'PUT':
                resp = self._session.put(url, headers=self.headers, timeout=timeout, **kwargs)
            elif method == 'DELETE':
                resp = self._session.delete(url, headers=self.headers, timeout=timeout, **kwargs)
            else:
                raise KeyError(f'当前不支持的HTTP请求方式：{method}')
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout):
            return 0

        if check_resp and not resp.ok:
            resp.close()
            return -1

        if return_type == 0:
            resp.close()
            return 1
        elif return_type == 1:
            resp.encoding = encoding
            data = resp.text
        elif return_type == 2:
            data = resp.json()
        else:
            data = resp.content

        resp.close()
        return data

    @staticmethod
    def _qwen_message_preprocess(messages: List[dict], allow_record: bool) -> List[dict]:
        """
        将本地聊天记录处理成通义千问的信息输入格式
        :param messages: 本地聊天记录
        :param allow_record: 是否记录之前的聊天内容，最多记录20条，开启后将消耗更多的token
        :return: 通义千问的信息输入格式
        """
        input_messages = []
        if not allow_record:
            input_message = {'role': messages[-1]['role'], 'content': messages[-1]['content']}
            input_messages.append(input_message)
            return input_messages

        for i in messages[-21:][1:]:
            if i['role'] == 'system':
                continue
            if i['role'] == 'assistant' and len(input_messages) == 0:
                continue
            if i['role'] == 'user' and len(input_messages) > 0 and input_messages[-1]['role'] == 'user':
                input_messages[-1]['content'] = i['content']
                continue

            input_message = {'role': i['role'], 'content': i['content']}
            input_messages.append(input_message)
        return input_messages

    def qwen_gpt(self,
                 messages: List[dict],
                 model_type: str = 'qwen-plus',
                 allow_record: bool = False) -> Tuple[bool, str, int]:
        """
        使用通义千问聊天对话
        :param messages: 本地聊天记录
        :param model_type: 通义千问的模型类型
        :param allow_record: 是否记录之前的聊天内容，最多记录20条，开启后将消耗更多的token
        :return: 返回三个参数，第一个参数为是否成功使用，第二个参数为回复内容或错误原因，第三个参数为对话消耗的token总数
        """
        url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
        self.headers['Authorization'] = f'Bearer {self.qwen_bearer}'
        input_messages = self._qwen_message_preprocess(messages, allow_record)
        data = {'model': model_type, 'messages': input_messages, 'enable_search': True}

        result = self._request('POST', url, return_type=2, timeout=300, json=data)
        if result == 0:
            return False, '连接失败！', 0
        elif result == -1:
            return False, '不正确的ApiKey或用户额度已耗尽', 0
        else:
            return True, result['choices'][0]['message']['content'], result['usage']['total_tokens']

    @staticmethod
    def _yuanqi_message_preprocess(messages: List[dict], allow_record: bool) -> List[dict]:
        """
        将本地聊天记录处理成腾讯元器的信息输入格式
        :param messages: 本地聊天记录
        :param allow_record: 是否记录之前的聊天内容，最多记录20条，开启后将消耗更多的token
        :return: 腾讯元器的信息输入格式
        """
        input_messages = []
        if not allow_record:
            input_message = {'role': messages[-1]['role'], 'content': [{'type': 'text', 'text': messages[-1]['content']}]}
            input_messages.append(input_message)
            return input_messages

        for i in messages[-21:][1:]:
            if i['role'] == 'system':
                continue
            if i['role'] == 'assistant' and len(input_messages) == 0:
                continue
            if i['role'] == 'user' and len(input_messages) > 0 and input_messages[-1]['role'] == 'user':
                input_messages[-1]['content'][0]['text'] = i['content']
                continue

            input_message = {'role': i['role'], 'content': [{'type': 'text', 'text': i['content']}]}
            input_messages.append(input_message)
        return input_messages

    def yuanqi_gpt(self, messages: List[dict], allow_record: bool = False) -> Tuple[bool, str, int]:
        """
        使用腾讯元器聊天对话
        :param messages: 本地聊天记录
        :param allow_record: 是否记录之前的聊天内容，最多记录20条，开启后将消耗更多的token
        :return: 返回三个参数，第一个参数为是否成功使用，第二个参数为回复内容或错误原因，第三个参数为对话消耗的token总数
        """
        url = 'https://yuanqi.tencent.com/openapi/v1/agent/chat/completions'
        self.headers['Authorization'] = f'Bearer {self.yuanqi_bearer}'
        input_messages = self._yuanqi_message_preprocess(messages, allow_record)
        data = {'assistant_id': self.yuanqi_id, 'stream': False, 'messages': input_messages}

        result = self._request('POST', url, return_type=2, timeout=300, json=data)
        if result == 0:
            return False, '连接失败！', 0
        elif result == -1:
            return False, '不正确的ApiKey或用户额度已耗尽', 0
        else:
            return True, result['choices'][0]['message']['content'], result['usage']['total_tokens']
