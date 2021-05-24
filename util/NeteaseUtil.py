#!/usr/bin/env python
# -*- coding=utf-8 -*-
import base64
import random
import codecs
# pip3 install -i https://pypi.douban.com/simple pycryptodome
# 直接通过whl文件安装，文件https://pypi.org/project/pycryptodome/3.9.0/#files (阿里云盘中也存储了)
from Crypto.Cipher import AES
from Crypto.Cipher import ARC4
from config.Config import Conf


class NeteaseUtil:
    """
    机器人工具类
    """
    @staticmethod
    def rand_ua():
        """
        获取随机 User-Agent
        :return:
        """
        return {'User-Agent': random.choice(Conf.UAS)}

    @staticmethod
    def pkcs7padding(text):
        """
        明文使用PKCS7填充
        最终调用AES加密方法时，传入的是一个byte数组，
        要求是16的整数倍，因此需要对明文进行处理
        :param text: 待加密内容(明文)
        :return:
        """
        bs = AES.block_size  # 16
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        # tips：utf-8编码时，英文占1个byte，而中文占3个byte
        padding_size = length if(bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
        padding_text = chr(padding) * padding
        return text + padding_text

    @staticmethod
    def pkcs7unpadding(text):
        """
        处理使用PKCS7填充过的数据
        :param text: 解密后的字符串
        :return:
        """
        length = len(text)
        unpadding = ord(text[length-1])
        return text[0:length-unpadding]

    @staticmethod
    def rc4_encrypt(data):
        rc4 = ARC4.new(bytes('zhx-201511180318', 'utf-8'))
        encrypted = rc4.encrypt(data.encode())
        return encrypted.hex().upper()

    @staticmethod
    def aes_encrypt(key, content):
        """
        AES加密
        key,iv使用同一个
        模式cbc
        填充pkcs7
        :param key: 密钥
        :param content: 加密内容
        :return:
        """
        key_bytes = bytes(key, encoding='utf-8')
        iv = bytes('0102030405060708', encoding='utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # 处理明文
        content_padding = NeteaseUtil.pkcs7padding(content)
        # 加密
        encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        # 重新编码
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
        return result

    @staticmethod
    def aes_decrypt(key, content):
        """
        AES解密
         key,iv使用同一个
        模式cbc
        去填充pkcs7
        :param key:
        :param content:
        :return:
        """
        key_bytes = bytes(key, encoding='utf-8')
        # iv = key_bytes
        iv = bytes('0102030405060708', encoding='utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # base64解码
        encrypt_bytes = base64.b64decode(content)
        # 解密
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        # 重新编码
        result = str(decrypt_bytes, encoding='utf-8')
        # 去除填充内容
        result = NeteaseUtil.pkcs7unpadding(result)
        return result

    @staticmethod
    def aes_encrypt_all(key, iv, content):
        key_bytes = bytes(key, encoding='utf-8')
        iv = bytes(iv, encoding='utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # 处理明文
        content_padding = NeteaseUtil.pkcs7padding(content)
        # 加密
        encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        # 重新编码
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
        return result

    @staticmethod
    def aes_decrypt_all(key, iv, content):
        key_bytes = bytes(key, encoding='utf-8')
        # iv = key_bytes
        iv = bytes(iv, encoding='utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # base64解码iv
        encrypt_bytes = base64.b64decode(content)
        # 解密
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        # 重新编码
        result = str(decrypt_bytes, encoding='utf-8')
        # 去除填充内容
        result = NeteaseUtil.pkcs7unpadding(result)
        return result

    @staticmethod
    def get_random_key(n):
        """
        获取密钥 n 密钥长度
        :return:
        """
        c_length = int(n)
        source = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
        length = len(source) - 1
        result = ''
        for i in range(c_length):
            result += source[random.randint(0, length)]
        return result

    @staticmethod
    def rsa_encrypt(random_str, key, secret):
        random_str = random_str[::-1]
        text = bytes(random_str, 'utf-8')
        sec_key = int(codecs.encode(text, encoding="hex"), 16) ** int(key, 16) % int(secret, 16)
        return format(sec_key, 'x').zfill(256)


if __name__ == '__main__':
    pass


