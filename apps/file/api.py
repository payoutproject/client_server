
import os

from rest_framework import viewsets
from libs.core.decorator.fileresponse import Core_connector
from education.settings import IMAGE_PATH
from education.config.common import ServerUrl
from libs.utils.mytime import UtilTime
from libs.utils.exceptions import PubErrorCustom
from libs.utils.qrcode import decode_qr
from apps.utils import url_join
from apps.user.models import Token
from apps.public.models import Qrcode,WechatHelper,QrType
from rest_framework.decorators import list_route
from apps.file.utils import qrtypeHandler

class FileAPIView(viewsets.ViewSet):

    @list_route(methods=['POST','OPTIONS'])
    @Core_connector(transaction=True)
    def upload(self,request, *args, **kwargs):

        file_obj = request.FILES.get('file')
        img_type = file_obj.name.split('.')[1]
        img_type = img_type.lower()

        if img_type in ['png', 'jpg', 'jpeg', 'gif']:
            timestr = UtilTime().arrow_to_string(format_v="YYYYMMDD")
            path = os.path.join(IMAGE_PATH, '{}'.format(timestr))

            outpath = "{}/statics/images/{}/{}".format(ServerUrl,timestr,file_obj.name)
            name = file_obj.name
            obj = qrtypeHandler(request=request,url=outpath,name=name)

            # if os.path.exists(os.path.join(path,file_obj.name)):
            #     # c=0
            #     # while True:
            #     #     if len(file_obj.name.split('images_teshudaima_images'))>1:
            #     #         file_obj.name = file_obj.name.split('images_teshudaima_images')[1]
            #     #     file_obj.name="copy{}images_teshudaima_images{}".format(c,file_obj.name)
            #     #     c=c+1
            #     #     if not os.path.exists(os.path.join(path,file_obj.name.replace("images_teshudaima_images","_"))):
            #     #         file_obj.name = file_obj.name.replace("images_teshudaima_images","_")
            #     #         break

            if not os.path.exists(path):
                os.makedirs(path)

            with open(os.path.join(path,file_obj.name),'wb+') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            QrcodeObj = Qrcode.objects.create(**obj)

            print(outpath)
            decode_res = decode_qr(outpath)

            if not decode_res:
                raise PubErrorCustom("上传失败,请稍等再试!")

            # decode_res="localhost:8001/statics/images/20200228/copy6_timg (2).jpg"

            QrcodeObj.url = decode_res
            QrcodeObj.path = outpath
            QrcodeObj.save()

            return {"data":{
                "path": outpath,
                "name": name
            }}
        else:
            raise PubErrorCustom("文件类型有误!")

        return None