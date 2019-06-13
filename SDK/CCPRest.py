# -*- coding: utf-8 -*-
"""
#project: CCP_Python3
#file: CCPRest.py
#author: ceephoen
#contact: ceephoen@163.com
#time: 2019/6/13 21:43:21
#desc: 
"""
import hashlib
import base64
import datetime
import logging
import functools
import requests


#################
# 单例模式装饰器 #
#################
def singleton(cls):
    """
    单例模式装饰器
    :param cls: class
    :return: cls
    """
    cls.__new_original__ = cls.__new__

    @functools.wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        it = cls.__dict__.get('__it__')
        if it is not None:
            return it

        cls.__it__ = it = cls.__new_original__(cls, *args, **kw)
        it.__init_original__(*args, **kw)
        return it

    cls.__new__ = singleton_new
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__

    return cls


@singleton
class CCP(object):
    def __new__(cls, *args, **kwargs):
        """
        __new__方法接收参数
        :param args: args
        :param kwargs: kwargs
        :return: cls
        """
        return object.__new__(cls)

    def __init__(self, app_id, svr_ip, svr_port, version, acc_sid, acc_token, sub_acc_sid=None, sub_acc_token=None, batch=None):
        """
        __init__方法
        :param app_id: 应用id
        :param svr_ip: 服务器地址
        :param svr_port: 服务器端口
        :param version: REST版本号
        :param acc_sid: 主帐号id
        :param acc_token: 主帐号Token
        :param sub_acc_sid: 子帐号
        :param sub_acc_token: 子帐号Token
        :param batch: 时间戳
        """
        self.app_id = app_id
        self.svr_ip = svr_ip
        self.svr_port = svr_port
        self.version = version
        self.acc_sid = acc_sid
        self.acc_token = acc_token

        self.sub_acc_sid = sub_acc_sid
        self.sub_acc_token = sub_acc_token
        self.batch = batch

    @staticmethod
    def info(url, body, data):
        logging.info('这是请求的URL：', url)
        logging.info('这是请求包体: ', body)
        logging.info('这是响应包体: ', data)
        logging.info('<---------->')

    @staticmethod
    def _set_headers(auth):
        """
        设置包头
        :param auth: 签名数据
        :return: headers type:dict
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': auth
        }

        return headers

    def authentication(self):
        """
        主帐号鉴权
        :return: None
        """
        if self.svr_ip == '':
            print('172004  IP为空')

        if self.svr_port <= 0:
            print('172005  端口错误（小于等于0）')

        if self.version == '':
            print('172013  版本号为空')

        if self.acc_sid == '':
            print('172006  主帐号为空')

        if self.acc_token == '':
            print('172007  主帐号令牌为空')

        if self.app_id == '':
            print('172012  应用ID为空')

    def send_template_message(self, to, data, temp_id):
        """
        发送模板短信
        :param to: 短信接收彿手机号码集合,用英文逗号分开
        :param data: 内容数据
        :param temp_id: 模板id
        :return: None
        """
        # 主帐号鉴权
        self.authentication()

        # 时间戳
        now = datetime.datetime.now()
        self.batch = now.strftime('%Y%m%d%H%M%S')

        # 生成sig
        sign = self.acc_sid + self.acc_token + self.batch  # type:str
        signature = hashlib.md5(sign.encode('utf-8')).hexdigest().upper()

        # 拼接URL
        url = 'https://{}:{}/{}/Accounts/{}/SMS/TemplateSMS?sig={}'.format(self.svr_ip, self.svr_port, self.version, self.acc_sid, signature)

        # 生成auth
        src = self.acc_sid + ':' + self.batch
        auth = base64.b64encode(src.encode('utf-8')).strip()

        # 生成headers
        headers = self._set_headers(auth)

        # 创建包体
        b = '['
        for d in data:
            b += '%s,' % d
        b += ']'

        # body
        body = "{'to': '{}', 'datas': {}, 'templateId': '{}', 'appId': '%s'}".format(to, b, temp_id, self.app_id)

        # 发送post请求
        rsp = requests.post(url=url, headers=headers, data=body.encode('utf-8'))
        logging.info('短信发送结果: ', rsp)
        return rsp.json()
