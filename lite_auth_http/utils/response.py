from django.http import JsonResponse

from utils.json_encoder import LiteAuthJsonEncoder

"""
code:

 - 0 : 成功
 - 1 : 失败
 - 400 : 未登录
"""


def json_response(data=None, code=0, msg=''):
    """
    返回json结构

    :return:
    """

    return JsonResponse({'data': data, 'code': code, 'msg': msg}, encoder=LiteAuthJsonEncoder)


