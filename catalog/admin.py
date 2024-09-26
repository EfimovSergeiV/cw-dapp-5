from django.contrib import admin
from catalog.models import *
from django.utils.safestring import mark_safe
from django.forms import ModelForm, TextInput, CharField
from mptt.admin import DraggableMPTTAdmin
from django_ckeditor_5.widgets import CKEditor5Widget


class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'name', 'parent',)
    list_editable = ( 'name', )


class StockInline(admin.TabularInline):
    model = StockModel
    fields = ('shop', 'latest_update', 'price', 'quantity')
    readonly_fields = ('latest_update',)
    extra = 0


class ShopAdmin(admin.ModelAdmin):
    list_display = ( 'uuid', 'city', 'adress', 'geo', )
    search_fields = ( 'uuid', 'city', 'adress', 'geo', )
    readonly_fields = ('uuid',)
    fieldsets = (
        ('', {'fields': (('uuid',),('city',),('adress',),('geo',),)}),
    )

# Переопределяем ширину поля ввода для поля name
class ProductFormsAdmin(ModelForm):
    name = CharField(label='Название', widget=TextInput(attrs={'style': 'width: 100%;'}))
    
    class Meta:
        model = ProductModel
        fields = '__all__'
    

class ShopFilter(admin.SimpleListFilter):
    title = 'Магазин'
    parameter_name = 'shop'

    def lookups(self, request, model_admin):
        shops = ShopModel.objects.all()
        return [(shop.uuid, f'{shop.city}, {shop.adress}') for shop in shops]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_uuid__shop__uuid=self.value())
        return queryset


from django.db.models import Min, Max

class ProductAdmin(admin.ModelAdmin):
    form = ProductFormsAdmin

    list_display = ( 'name', 'get_max_price' )
    search_fields = ( 'name', )
    readonly_fields = ('uuid',)

    list_filter = (ShopFilter,)
    inlines = [
        StockInline,
    ]
    fieldsets = (
        ('', {'fields': (('uuid',),('name',),)}),
    )

    def get_queryset(self, request):
        # Переопределяем queryset для добавления аннотации с максимальной стоимостью
        qs = super().get_queryset(request)
        return qs.annotate(min_price=Min('product_uuid__price'),max_price=Max('product_uuid__price'))

    def get_max_price(self, obj):
        # Возвращаем максимальную стоимость из аннотации
        result = f'{obj.max_price}' if obj.max_price == obj.min_price else f'{obj.min_price} - {obj.max_price}'
        return result

    get_max_price.short_description = 'Стоимость'



# Переопределяем ширину поля ввода для поля name
class ProductCardFormsAdmin(ModelForm):
    keywords_hepl = "* Отвечает за сопастовление карточек товаров с товарами"

    name = CharField(label='Название', widget=TextInput(attrs={'style': 'width: 100%;'}))
    keywords = CharField(label='Ключевые слова', help_text=keywords_hepl, widget=TextInput(attrs={'style': 'width: 100%;'}))
    description = CharField(label="Описание", widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"},))

    class Meta:
        model = ProductModel
        fields = '__all__'


class ProductImagesAdmin(admin.TabularInline):
    """ Изображения товара """
    model = ProductImagesModel
    readonly_fields = ('show_img', )
    extra = 0

    def show_img(self, obj):
        url_img = obj.image if obj.image else 'img/c/preview/noimage.webp'
        return mark_safe('<img style="margin-right:-10vh; background-color: white; padding: 15px; border-radius: 5px;" src="/files/%s" alt="Нет изображения" width="120" height="auto" />' % (url_img))

    show_img.short_description = 'Изображение'
    fieldsets = (
        (None, {'fields': ('show_img', 'image')}),
        )


class ProductCardAdmin(admin.ModelAdmin):
    """ Админка для карточек товаров """
    form = ProductCardFormsAdmin

    def show_img(self, obj):
        url_img = obj.image if obj.image else 'img/c/preview/noimage.webp'
        return mark_safe('<img style="margin-right:-10vh; background-color: white; padding: 15px; border-radius: 5px;" src="/files/%s" alt="Нет изображения" width="120" height="auto" />' % (url_img))
    show_img.short_description = 'Изображение'
    
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)
    readonly_fields = ('id', 'show_img',)
    inlines = [
        ProductImagesAdmin,
    ]

    fieldsets = (
        ('', {'fields': ((), ('name',), ('keywords',),)}),
        ('', {'fields': (('id', 'price', 'category',),)}),
        ('', {'fields': ((),)}),
        ('', {'fields': (('show_img', 'preview',),('description'))}),
    )



admin.site.register(CategoryModel, CategoryAdmin)
admin.site.register(ProductModel, ProductAdmin)
admin.site.register(ShopModel, ShopAdmin)
admin.site.register(ProductsTableModel)
admin.site.register(ProductCardModel, ProductCardAdmin)