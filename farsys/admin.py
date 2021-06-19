from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User),
admin.site.register(Account),
admin.site.register(Match),
admin.site.register(Category),
admin.site.register(Product),
admin.site.register(Attribute),
admin.site.register(Sucursal),
admin.site.register(Client),
admin.site.register(Vendor),
admin.site.register(Purchase),
admin.site.register(PurchaseItem),
admin.site.register(Sale),
admin.site.register(SaleItem),


