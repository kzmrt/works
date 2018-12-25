from django import forms
import os

VALID_EXTENSIONS = ['.jpg']


class UploadFileForm(forms.Form):
    image = forms.ImageField()

    def clean_file(self):
        file = self.cleaned_data['file']
        extension = os.path.splitext(file.name)[1] # 拡張子を取得
        if not extension.lower() in VALID_EXTENSIONS:
            raise forms.ValidationError('jpgファイルを選択してください！')