from django.db import models



class AbstractStatusModel(models.Model):
    """ Абстрактная модель, которая добавляет поля created_date, latest_update и is_activated. """
   
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    latest_update = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление",)
    is_activated = models.BooleanField(default=True, verbose_name="Активирован")

    class Meta:
        abstract = True