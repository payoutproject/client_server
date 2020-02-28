
import os
import time

from functools import wraps
from django.db import transaction

from core.http.response import HttpResponse

from utils.log import logger
from utils.exceptions import PubErrorCustom,InnerErrorCustom
from core.paginator import Pagination

from django.template import loader
from django.core.serializers.json import DjangoJSONEncoder
from data import dictlist

from apps.user.models import Users

import json

from django.http import StreamingHttpResponse
from libs.utils.redlock import ReadLock
from apps.utils import url_join

from cryptokit import AESCrypto
from apps.public.utils import CheckIpForLogin
import base64


class Core_connector:
    def __init__(self,**kwargs):

        self.transaction = kwargs.get("transaction",None)
        pass

    #前置处理
    def __request_validate(self,request,**kwargs):

       return kwargs

    def __run(self,func,outside_self,request,*args, **kwargs):

        if self.transaction:
            with transaction.atomic():
                res = func(outside_self, request, *args, **kwargs)
        else:
            res = func(outside_self, request, *args, **kwargs)

        if not isinstance(res, dict):
            res = {'data': None, 'msg': None, 'header': None}
        if 'data' not in res:
            res['data'] = None
        if 'msg' not in res:
            res['msg'] =  {}
        if 'header' not in res:
            res['header'] = None

        return HttpResponse(data= res['data'],headers=res['header'], msg=res['msg'])

    #后置处理
    def __response__validate(self,outside_self,func,response,request):

        return response

    def __call__(self,func):
        @wraps(func)
        def wrapper(outside_self,request,*args, **kwargs):
            try:
                self.start = time.time()
                kwargs=self.__request_validate(request,**kwargs)
                response=self.__run(func,outside_self,request,*args, **kwargs)
                self.end=time.time()
                return self.__response__validate(outside_self,func,response,request)
            except PubErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse(success=False, msg=e.msg, data=None)
            except InnerErrorCustom as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),e.msg))
                return HttpResponse(success=False, msg=e.msg, rescode=e.code, data=None)
            except Exception as e:
                logger.error('[%s : %s  ] : [%s]'%(outside_self.__class__.__name__, getattr(func, '__name__'),str(e)))
                return HttpResponse(success=False, msg=str(e), data=None)
        return wrapper