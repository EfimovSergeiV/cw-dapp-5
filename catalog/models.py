import uuid
from django.db import models
from django_resized import ResizedImageField
from mptt.models import MPTTModel, TreeForeignKey


class ProductModel(models.Model):
    """
        Товары каталога, которые есть в наличии.
        Заносятся при парсинге
    """
    uuid = models.UUIDField(verbose_name="Идентификатор", primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(verbose_name="Название", max_length=100)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "2. Товары"
        ordering = ['name',]

    def __str__(self):
        return self.name



class ShopModel(models.Model):
    """
        Магазины
    """

    uuid = models.UUIDField(verbose_name="Идентификатор", primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    city = models.CharField(verbose_name="Город", max_length=100, null=True, blank=True)
    adress = models.CharField(verbose_name="Адрес", max_length=100, null=True, blank=True)
    geo = models.CharField(verbose_name="Координаты", max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "1. Магазины"
        ordering = ['-city',]

    def __str__(self):
        return f'{self.city} {self.adress}'
    


class StockModel(models.Model):
    """
        Наличие, остаток товаров и стоимость
    """
    shop = models.ForeignKey(ShopModel, verbose_name="Магазин", related_name="shop_uuid", on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, verbose_name="Товар", related_name="product_uuid", on_delete=models.CASCADE)
    
    price = models.PositiveIntegerField(verbose_name="Стоимость", null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество", null=True, blank=True)
    latest_update = models.DateTimeField(verbose_name="Последнее обновление", auto_now=True)

    def __str__(self):
        return self.product.name



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
        verbose_name_plural = "3. Категории"
        
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
        verbose_name_plural = "4. Карточки товаров"
        ordering = ['name',]

    def __str__(self):
        return self.product.name