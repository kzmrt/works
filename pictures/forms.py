from django import forms
import os

VALID_EXTENSIONS = ['.jpg']


class UploadFileForm(forms.Form):
    image = forms.ImageField()

    def clean_image(self):
        image = self.cleaned_data['image']
        extension = os.path.splitext(image.name)[1]  # 拡張子を取得
        if not extension.lower() in VALID_EXTENSIONS:
            raise forms.ValidationError('jpgファイルを選択してください！')
        return image  # viewsでcleaned_dataを参照するためreturnする
