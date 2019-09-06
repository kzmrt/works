from django.shortcuts import redirect
from django.views import generic
from .models import Work, Image
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from .forms import UploadFileForm
from django.views.generic.edit import FormView
import requests
import json
from works import settings
import os
from django.shortcuts import render

logger = logging.getLogger('development')

# アップロードした画像を保存するディレクトリ
UPLOAD_IMG_DIR = settings.MEDIA_ROOT + '/image/'

# オブジェクトストレージ接続パラメータ
USER_NAME = "gncu00000000"  # ユーザー名
PASSWORD = "passpasspass"  # パスワード
TENANT_ID = "9999999999999999999999999"  # テナントID
URL = 'https://identity.tyo2.conoha.io/v2.0/tokens'  # トークン取得用URL
OBJECT_STORAGE = 'https://object-storage.tyo2.conoha.io/v1/nc_9999999999999999999999999999'  # オブジェクトストレージURL
CONTAINER = 'sample1'  # コンテナ名


# 一覧画面
class IndexView(LoginRequiredMixin, generic.ListView):
    model = Work
    paginate_by = 5
    ordering = ['-updated_at']
    template_name = 'pictures/index.html'


# 詳細画面
class DetailView(generic.DetailView):
    model = Work
    template_name = 'pictures/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session.modified = True  # セッション更新
        context['work_pk'] = self.kwargs['pk']

        return context


# # ファイルアップロード
# class Upload(FormView):
#     template_name = 'pictures/upload.html'
#     form_class = UploadFileForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         form = self.get_form()
#         context = {
#             'work_pk': self.kwargs['pk'],
#             'form': form,
#         }
#         return context
#
#     def form_valid(self, form):
#
#         image = Image()  # DBへの保存
#         image.work_id = self.kwargs['pk']  # 作品ID
#         image.image = form.cleaned_data['image']  # アップロードしたイメージパス
#         image.save()
#
#         return redirect('pictures:upload_complete', self.kwargs['pk'])  # アップロード完了画面にリダイレクト


def getToken(userName, password, tenantId, url):
    """
    tokenの取得
    :param userName:
    :param password:
    :param tenantId:
    :param url:
    :return:
    """

    headers = {
        'Accept': 'application/json',
    }

    data = '{"auth":{"passwordCredentials":{"username":"%s","password":"%s"},"tenantId":"%s"}}' % (
    userName, password, tenantId)

    response = requests.post(url, headers=headers, data=data)
    data = response.json()

    return json.dumps(data["access"]["token"]["id"], indent=4)


def uploadObject(token, path, objectStorageUrl, container, fileName):
    """
    オブジェクトのアップロード
    :param token:
    :param path:
    :param objectStorageUrl:
    :param container:
    :param fileName:
    :return:
    """

    headers = {
        'Accept': 'application/json',
        'X-Auth-Token': token,
    }

    with open(path, 'rb') as image:
        response = requests.put(objectStorageUrl + '/' + container + '/' + fileName, headers=headers, data=image)

    return response


def handle_uploaded_image(upload_image, pk):
    """
    アップロードされた画像のハンドル
    :param upload_image:
    :param pk:
    :return:
    """
    # アップロードファイルを一旦保存する。
    path = os.path.join(UPLOAD_IMG_DIR, upload_image.name)
    with open(path, 'wb+') as destination:
        for chunk in upload_image.chunks():
            destination.write(chunk)

    # オブジェクトストレージにアップロードする。
    token = getToken(USER_NAME, PASSWORD, TENANT_ID, URL).replace('\"', '')  # tokenの取得

    fileName = str(upload_image.name)  # ファイル名

    result = uploadObject(token, path, OBJECT_STORAGE, CONTAINER, fileName)  # オブジェクトのアップロード

    if result.status_code == 201:  # アップロード成功の場合

        image = Image()  # DBへの保存
        image.work_id = pk  # 作品ID
        image.image = OBJECT_STORAGE + '/' + CONTAINER + '/' + fileName  # アップロードしたイメージパス
        image.save()

        # アップロードしたファイルを削除する
        os.remove(path)

    else:  # アップロード失敗の場合
        logger.warning('オブジェクトのアップロードに失敗しました。')


def uploadImage(request, pk):
    """
    画像のアップロード
    :param request:
    :param pk:
    :return:
    """
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():

            handle_uploaded_image(request.FILES['image'], pk)  # アップロードされた画像のハンドル
            return redirect('pictures:upload_complete', pk)  # アップロード完了画面にリダイレクト
    else:
        form = UploadFileForm()
    return render(request, 'pictures/upload.html', {'form': form})


class UploadComplete(FormView):
    """
    ファイルアップロード完了
    """
    template_name = 'pictures/upload_complete.html'
    form_class = UploadFileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session.modified = True  # セッション更新
        context['work_pk'] = self.kwargs['pk']

        return context
