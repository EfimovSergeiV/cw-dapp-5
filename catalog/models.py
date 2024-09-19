import uuid
from django.db import models
from django.utils import timezone
from django_resized import ResizedImageField
from mptt.models import MPTTModel, TreeForeignKey


class ProductModel(models.Model):
    """
        Товары каталога, которые есть в наличии.
        Заносятся при парсинге
    """
    uuid = models.UUIDField(verbose_name="Идентификатор", primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(verbose_name="Название", unique=True, max_length=100)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "1.2 Товары"
        ordering = ['name',]

    def __str__(self):
        return self.name


class ShopModel(models.Model):
    """ Магазины """

    uuid = models.UUIDField(verbose_name="Идентификатор", primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    city = models.CharField(verbose_name="Город", max_length=100, null=True, blank=True)
    adress = models.CharField(verbose_name="Адрес", max_length=100, null=True, blank=True)
    geo = models.CharField(verbose_name="Координаты", max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "1.1 Магазины"
        ordering = ['-city',]

    def __str__(self):
        return f'{self.city}, {self.adress}'



class StockModel(models.Model):
    """ Наличие, остаток товаров и стоимость """
   
    shop = models.ForeignKey(ShopModel, verbose_name="Магазин", related_name="shop_uuid", on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, verbose_name="Товар", related_name="product_uuid", on_delete=models.CASCADE)

    price = models.PositiveIntegerField(verbose_name="Стоимость", null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество", null=True, blank=True)
    latest_update = models.DateTimeField(verbose_name="Последнее обновление", auto_now=True)

    class Meta:
        verbose_name = "Остаток товара"
        verbose_name_plural = "Остатки товаров"

    def __str__(self):
        return self.product.name
    



import pandas as pd
from django.db.models import Q

from time import sleep

class ProductsTableModel(models.Model):
    """ Таблица c товарами, которые есть в наличии """

    shop = models.ForeignKey(ShopModel, related_name="shops_xls", on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateField(verbose_name="Дата выгрузки", auto_now=True)
    file = models.FileField(verbose_name="Файл xls", upload_to='c/import-1c/')

    class Meta:
        verbose_name = "XLS Таблица товаров"
        verbose_name_plural = "1.3 XLS Таблицы товаров"
    
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
                print(f"{ index }, { price } руб, { quantity } шт.")

                tokens = str(index).split()
                conditions = Q()
                for token in tokens:
                    conditions &= Q(name__icontains=token)

                prod = prods_qs.filter(conditions)

                if prod.exists() and len(prod) == 1:
                    stock_qs.update_or_create(
                        shop = self.shop,
                        product = prod[0],
                        price = price,
                        quantity = quantity,
                    )

                elif prod.exists() and len(prod) > 1:
                    # дополнительный фильтр на полное совпадение

                    prod = prod.filter(name=str(index))

                    stock_qs.update_or_create(
                        shop = self.shop,
                        product = prod[0],
                        price = price,
                        quantity = quantity,
                    )

                # else:
                #     # СПОРНОЕ: ПЕРЕПРОВЕРИТЬ
                #     prod_qs = prods_qs.create(
                #         name=str(index),
                #     )

                #     prods_updated.append(stat.id)

                
        # Удаляем товары которых нет в обновлённых или созданных
        # objects_to_delete = prods_qs.exclude(id__in=prods_updated)
        # objects_to_delete.delete()




"""
    Карточки товаров могут существовать независимо от товаров

"""

class CategoryModel(MPTTModel):
    """ 
        Категории карточек товаров
    """
    image = ResizedImageField(
        size = [120, 85],
        verbose_name="",
        crop = ['middle', 'center'],
        upload_to='img/c/preview/',
        help_text="Миниатира категории, только первого уровня (120x85 px)",
        quality=100,
        null=True,
        blank=True,
        force_format='WEBP',
    )
    name = models.CharField(verbose_name="Название", max_length=100)
    parent = TreeForeignKey('self', verbose_name="Вложенность", on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    visible = models.BooleanField(verbose_name="Отображать в категориях", default=True)
    related = models.ManyToManyField('self', verbose_name='Связанные категории', blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "1.4 Категории"
        
    class MPTTMeta:
        order_insertion_by = ['name',]

    def __str__(self):
        return str(self.id) + '. ' + self.name



class ProductCardModel(models.Model):
    """
        Карточка товара
    """

    name = models.CharField(verbose_name="Название", max_length=100)
    keywords = models.CharField(verbose_name="Ключевые слова", max_length=100, null=True, blank=True)
    price = models.PositiveIntegerField(verbose_name="Стоимость", null=True, blank=True)
    category = models.ForeignKey(CategoryModel, verbose_name="Категория", on_delete=models.SET_NULL, null=True, blank=True)
    product_uuid = models.UUIDField(verbose_name="Идентификатор товара", null=True, blank=True)
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    preview = ResizedImageField(
        size = [235, 177],
        verbose_name="",
        crop = ['middle', 'center'],
        upload_to='img/c/preview/',
        help_text="Миниатира товара (235x177 px)",
        quality=100,
        default='img/c/preview/noimage.webp',
        force_format='WEBP',
    )

    class Meta:
        verbose_name = "Карточка товара"
        verbose_name_plural = "1.5 Карточки товаров"
        ordering = ['name',]

    def __str__(self):
        return self.product.name