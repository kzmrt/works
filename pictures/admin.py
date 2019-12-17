from django.contrib import admin

from .models import Work, Image

# admin.site.register(Work)
# admin.site.register(Image)


class WorkModelAdmin(admin.ModelAdmin):
    # 一覧表示画面のフィールド
    list_display = ('name', 'memo', 'author', 'created_at', 'updated_at')
    # 一覧表示画面のソート
    ordering = ('created_at',)  # '-created_at' とすると降順になります。
    # 編集画面のフィールド
    fields = ('name', 'memo', 'author')


class ImageModelAdmin(admin.ModelAdmin):
    # 一覧表示画面のフィールド
    list_display = ('work', 'image', 'created_at', 'updated_at')
    # 編集画面のフィールド
    fields = ('work', 'image', 'data_datetime')


admin.site.register(Work, WorkModelAdmin)
admin.site.register(Image, ImageModelAdmin)