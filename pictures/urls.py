from django.urls import path
from . import views

app_name = 'pictures'

urlpatterns = [
    # トップ画面
    path('', views.IndexView.as_view(), name='index'),

    # 詳細画面
    path('pictures/<int:pk>/', views.DetailView.as_view(), name='detail'),

    # ファイルアップロード用
    # path('pictures/<int:pk>/upload/', views.Upload.as_view(), name='upload'),
    path('pictures/<int:pk>/upload/', views.uploadImage, name='upload'),  # ConoHaオブジェクトストレージに登録
    path('pictures/<int:pk>/upload_complete/', views.UploadComplete.as_view(), name='upload_complete'),
]