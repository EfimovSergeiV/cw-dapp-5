from django.db import models
from main.models import AbstractStatusModel
from django_resized import ResizedImageField



class BannerModel(AbstractStatusModel):
    """ Баннеры на главной странице """

    POSITIONS = (
        ("1", "Шапка сайта"),
        ("2", "Главная/новинки"),
        ("3", "Секция Esab"),
    )

    image = ResizedImageField(
        size = [1024, 320], crop = ['middle', 'center'], verbose_name='',       
        upload_to='img/c/widebaners/', quality=100, force_format='WEBP',
    )
    name = models.CharField(verbose_name="Название", max_length=150)
    position = models.CharField(verbose_name="Позиция", max_length=100, choices=POSITIONS)
    ordering = models.IntegerField(verbose_name="Выдача", default=0)
    link = models.URLField(verbose_name="Внешняя ссылка", null=True, blank=True)
    path = models.JSONField(verbose_name="Внутренняя ссылка", null=True, blank=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "(2.1) Баннеры"
        ordering = ['ordering',]

    def __str__(self):
        return self.title