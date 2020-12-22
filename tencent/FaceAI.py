# -*- coding:utf-8 -*-
import json
import base64
from config.Config import Conf
from tencentcloud.common import credential
from tencentcloud.ft.v20200304 import ft_client, models as ft_m
from tencentcloud.iai.v20200303 import iai_client, models as iai_m
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile


def image_to_base64(url):
    with open(url, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        s = base64_data.decode()
        return f'data:image/jpeg;base64,{s}'


class FaceIAIAI:
    def __init__(self):
        """
        人脸识别
        """
        self._cred = credential.Credential(Conf.TENCENT_AI_SECRET_ID, Conf.TENCENT_AI_SECRET_KEY)
        self._httpProfile = HttpProfile()
        self._httpProfile.endpoint = "iai.tencentcloudapi.com"
        self._clientProfile = ClientProfile()
        self._clientProfile.httpProfile = self._httpProfile
        self.client = iai_client.IaiClient(self._cred, "ap-beijing", self._clientProfile)

    def detect_face(self, face_base64):
        req = iai_m.DetectFaceRequest()
        params = {
            'Image': face_base64
        }
        req.from_json_string(json.dumps(params))
        resp = self.client.DetectFace(req)
        return resp.to_json_string()


class FaceFTAI:
    def __init__(self):
        """
        人脸变换
        """
        self._cred = credential.Credential(Conf.TENCENT_AI_SECRET_ID, Conf.TENCENT_AI_SECRET_KEY)
        self._httpProfile = HttpProfile()
        self._httpProfile.endpoint = "ft.tencentcloudapi.com"
        self._clientProfile = ClientProfile()
        self._clientProfile.httpProfile = self._httpProfile
        self.client = ft_client.FtClient(self._cred, "ap-beijing", self._clientProfile)

    def face_change_age(self, face_base64, age):
        # 检测图片中的人脸，并获取人脸Rect信息
        ret = FaceIAIAI().detect_face(face_base64)
        ret = json.loads(ret)
        if ret and ret['FaceInfos'] and len(ret['FaceInfos']) > 0:
            face_info = ret['FaceInfos'][0]
            del face_info['FaceAttributesInfo']
            del face_info['FaceQualityInfo']
            age_info = [{'Age': int(age), 'FaceRect': face_info}]
            # 请求改变年龄
            req = ft_m.ChangeAgePicRequest()
            param = {
                'Image': face_base64,
                'AgeInfos': age_info,
                'RspImgType': 'url'
            }
            req.from_json_string(json.dumps(param))
            resp = self.client.ChangeAgePic(req)
            resp = resp.to_json_string()
            resp = json.loads(resp)
            if resp and resp['ResultUrl']:
                return resp['ResultUrl']
        return None

