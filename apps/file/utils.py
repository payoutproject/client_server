

from libs.utils.exceptions import PubErrorCustom
from libs.utils.qrcode import decode_qr
from apps.utils import url_join
from apps.user.models import Token
from apps.public.models import Qrcode,WechatHelper,QrType

def qrtypeHandler(request,url,name):
    if not request.data.get("qrtype"):
        raise PubErrorCustom("请选择二维码类型!")

    try:
        result = Token.objects.get(key=request.data.get("token"))
    except Token.DoesNotExist:
        return (None, 'token已失效,请退出后重新登录！', 200, ResCode.TOKEN_NOT)

    if request.data.get("qrtype") == 'QR001':
        if not request.data.get("wechathelper_id") or str(request.data.get("wechathelper_id")) == '0':
            raise PubErrorCustom("请选择店员助手!")

    QrcodeObj=Qrcode.objects.filter(status__in=[0,1,2,3,5])

    for item in QrcodeObj:
        if item.name == name :
            raise PubErrorCustom("一个昵称只能存一张二维码!")

    create_order_dict = {
        "name": name,
        "status": '3',
        "updtime": 0,
        "userid": result.userid,
        "wechathelper_id": request.data.get("wechathelper_id"),
        "type": request.data.get("qrtype")
    }


    return create_order_dict
