from django.contrib import admin
from catalog.models import *
from mptt.admin import DraggableMPTTAdmin



class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'name', 'parent',)
    list_editable = ( 'name', )


class StockInline(admin.TabularInline):
    model = StockModel
    extra = 0


class ShopAdmin(admin.ModelAdmin):
    list_display = ( 'uuid', 'city', 'adress', 'geo', )
    search_fields = ( 'uuid', 'city', 'adress', 'geo', )
    readonly_fields = ('uuid',)
    fieldsets = (
        ('', {'fields': (('uuid',),('city',),('adress',),('geo',),)}),
    )


class ProductAdmin(admin.ModelAdmin):
    list_display = ( 'uuid', 'name', )
    search_fields = ( 'uuid', 'name', )
    readonly_fields = ('uuid',)
    inlines = [
        StockInline,
    ]
    fieldsets = (
        ('', {'fields': (('uuid',),('name',),)}),
    )




admin.site.register(CategoryModel, CategoryAdmin)
admin.site.register(ProductModel, ProductAdmin)
admin.site.register(ShopModel, ShopAdmin)
admin.site.register(ProductCardModel)