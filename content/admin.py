from django.contrib import admin
from content.models import *
from django.utils.safestring import mark_safe



class BannerAdmin(admin.ModelAdmin):

    def show_img(self, obj):
        url_img = obj.image if obj.image else 'img/c/preview/noimage.webp'
        return mark_safe('<img style="background-color: white; border-radius: 5px;" src="/files/%s" alt="Нет изображения" width="auto" height="120" />' % (url_img))
    show_img.short_description = 'Превью'

    list_display = ('id', 'position', 'is_activated')
    search_fields = ('id', 'position', 'is_activated')
    readonly_fields = ('id', 'show_img', 'created_date', 'latest_update',)
    fieldsets = (
        ('', {'fields': ( ('is_activated', 'created_date', 'latest_update',),)}),
        ('', {'fields': (( 'show_img', 'image',), ('position',),)}),
    )



admin.site.register(BannerModel, BannerAdmin)