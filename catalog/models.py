import uuid
from django.db import models
from django.utils import timezone
from main.models import AbstractStatusModel
from django_resized import ResizedImageField
from mptt.models import MPTTModel, TreeForeignKey
from django_ckeditor_5.fields import CKEditor5Field



class ShopModel(AbstractStatusModel):
    """ Магазины """

    uuid = models.UUIDField(verbose_name="Идентификатор", primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    position = models.PositiveIntegerField(verbose_name="Позиция в списке", default=0)

    region_code = models.CharField(verbose_name="Код региона", default='PSK', max_length=3)
    city = models.CharField(verbose_name="Город", max_length=100, null=True, blank=True)
    adress = models.CharField(verbose_name="Адрес", max_length=100, null=True, blank=True)
    geo = models.CharField(verbose_name="Координаты", max_length=20, null=True, blank=True)
    google_maps = models.URLField(verbose_name="Google Maps", null=True, blank=True)
    yandex_maps = models.URLField(verbose_name="Yandex Maps", null=True, blank=True)

    phone = models.CharField(verbose_name="Телефон", max_length=20, null=True, blank=True)
    mobile = models.CharField(verbose_name="Моб.телефон", max_length=20, null=True, blank=True)

    telegram = models.CharField(verbose_name="Телеграмм", max_length=100, null=True, blank=True)
    whatsapp = models.CharField(verbose_name="WhatsApp", max_length=100, null=True, blank=True)
    viber = models.CharField(verbose_name="Viber", max_length=100, null=True, blank=True)

    wday = models.CharField(verbose_name="График по будням", null=True, blank=True, max_length=60)
    wend = models.CharField(verbose_name="График по выходным", null=True, blank=True, max_length=60)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "(1.1) Магазины"
        ordering = ['position', '-city',]

    def __str__(self):
        return f'{self.city}, {self.adress}'


class ProductModel(AbstractStatusModel):
    """
        Товары каталога, которые есть в наличии.
        Заносятся при парсинге
    """
    uuid = models.UUIDField(verbose_name="Идентификатор", primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(verbose_name="Название", unique=True, max_length=100)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "(1.2) Товары"
        ordering = ['name',]

    def __str__(self):
        return self.name


class StockModel(AbstractStatusModel):
    """ Наличие, остаток товаров и стоимость """
   
    shop = models.ForeignKey(ShopModel, verbose_name="Магазин", related_name="shop_uuid", on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, verbose_name="Товар", related_name="product_uuid", on_delete=models.CASCADE)

    price = models.PositiveIntegerField(verbose_name="Стоимость", null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество", null=True, blank=True)

    class Meta:
        verbose_name = "Остаток товара"
        verbose_name_plural = "Остатки товаров"

    def __str__(self):
        return self.product.name


import pandas as pd
from django.db.models import Q

class ProductsTableModel(models.Model):
    """ Таблица c товарами, которые есть в наличии """

    shop = models.ForeignKey(ShopModel, related_name="shops_xls", on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateField(verbose_name="Дата выгрузки", auto_now=True)
    file = models.FileField(verbose_name="Файл xls", upload_to='c/import-1c/')

    class Meta:
        verbose_name = "XLS Таблица товаров"
        verbose_name_plural = "(1.3) XLS Таблицы товаров"

    def __str__(self):
        return f'{ self.shop }, Выгружен: { self.created_date }'


    def save(self, *args, **kwargs):
        super(ProductsTableModel, self).save(*args, **kwargs)

        prods_qs = ProductModel.objects.all()
        stock_qs = StockModel.objects.all()

        df = pd.read_excel(f'{self.file.path}', sheet_name='TDSheet', header=None, index_col=0)
        for index, row in df.iterrows():

            price = row[12] if type(row[12]) == int else None
            quantity = row[13] if type(row[13]) == int else None

            if price and quantity:
                tokens = str(index).split()
                conditions = Q()
                for token in tokens:
                    conditions &= Q(name__icontains=token)

                prod = prods_qs.filter(conditions).first()
                prod = prod = prods_qs.create(name=str(index),) if not prod else prod

                stock_qs.update_or_create(
                    shop = self.shop,
                    product = prod,
                    defaults = {
                        "price": price,
                        "quantity": quantity,
                    }
                )



""" Карточки товаров могут существовать независимо от товаров """

class CategoryModel(MPTTModel):
    """ Категории карточек товаров """
   
    image = ResizedImageField(
        size = [120, 85], verbose_name="", crop = ['middle', 'center'],
        help_text="Миниатира категории, только первого уровня (120x85 px)",
        quality=100, null=True, blank=True, force_format='WEBP', upload_to='img/c/preview/',
    )
    name = models.CharField(verbose_name="Название", max_length=100)
    parent = TreeForeignKey('self', verbose_name="Вложенность", on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_activated = models.BooleanField(default=True, verbose_name="Активирован")
    visible = models.BooleanField(verbose_name="Отображать в категориях", default=True)
    related = models.ManyToManyField('self', verbose_name='Связанные категории', blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "(1.4) Категории"
        
    class MPTTMeta:
        order_insertion_by = ['name',]

    def __str__(self):
        return str(self.id) + '. ' + self.name


class ProductCardModel(AbstractStatusModel):
    """ Карточка товара """

    name = models.CharField(verbose_name="Название", max_length=100)
    keywords = models.CharField(verbose_name="Ключевые слова", max_length=100, null=True, blank=True)
    price = models.PositiveIntegerField(verbose_name="Стоимость", null=True, blank=True)
    category = models.ForeignKey(CategoryModel, verbose_name="Категория", on_delete=models.SET_NULL, null=True, blank=True)
    description = CKEditor5Field(verbose_name="Описание", null=True, blank=True)
    preview = ResizedImageField(
        size = [235, 177], verbose_name="", crop = ['middle', 'center'],       
        help_text="Миниатира товара (235x177 px)",
        default='img/c/preview/noimage.webp', quality=100,
        force_format='WEBP', upload_to='img/c/preview/',
    )

    class Meta:
        verbose_name = "Карточка товара"
        verbose_name_plural = "(1.5) Карточки товаров"
        ordering = ['name',]

    def __str__(self):
        return self.name
    

class ProductImagesModel(models.Model):
    """ Изображения к карточке товара """

    product = models.ForeignKey(ProductCardModel, verbose_name="Карточка товара", related_name="prod_img", on_delete=models.CASCADE)
    image = ResizedImageField(
        size = [640, 480], verbose_name="", crop = ['middle', 'center'],
        help_text="Изображение товара (640x480 px)",
        quality=100, force_format='WEBP', upload_to='img/c/product/',
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return self.product.name