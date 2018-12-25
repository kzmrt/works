from django.shortcuts import redirect
from django.views import generic
from .models import Work, Image
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from .forms import UploadFileForm
from django.views.generic.edit import FormView

logger = logging.getLogger('development')


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


# ファイルアップロード
class Upload(FormView):
    template_name = 'pictures/upload.html'
    form_class = UploadFileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        context = {
            'work_pk': self.kwargs['pk'],
            'form': form,
        }
        return context

    def form_valid(self, form):

        image = Image()  # DBへの保存
        image.work_id = self.kwargs['pk']  # 作品ID
        image.image = form.cleaned_data['image']  # アップロードしたイメージパス
        image.save()

        return redirect('pictures:upload_complete', self.kwargs['pk'])  # アップロード完了画面にリダイレクト


# ファイルアップロード完了
class UploadComplete(FormView):
    template_name = 'pictures/upload_complete.html'
    form_class = UploadFileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session.modified = True  # セッション更新
        context['work_pk'] = self.kwargs['pk']

        return context
