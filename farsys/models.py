from django.db import models
from django import forms
from django.forms import ModelForm, TextInput, NumberInput, Select, HiddenInput
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Utils
class Date(forms.DateInput):
    input_type = 'date'


# Models for Master Data
class User(AbstractUser):
    pass

    def current_account(self):
        return Match.objects.get(user=self).account

class Account(models.Model):
    account = models.CharField(max_length=30)

    def __str__(self):
        return self.account

    def current(self):
        return Match.objects.get(user=self).account


class Match(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account')

    def __str__(self):
        return self.account.account


class Category(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name    = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Product(models.Model):
    code     = models.IntegerField(blank=True, null=True, default=0)
    name     = models.CharField(max_length=100)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    editable = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["name"]
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Attribute(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_1 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, default=0.0)
    price_2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, default=0.0)
    price_3 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, default=0.0)
    unit_1  = models.IntegerField(blank=True, null=True, default=1)
    unit_2  = models.IntegerField(blank=True, null=True, default=0)
    unit_3  = models.IntegerField(blank=True, null=True, default=0)
    stock   = models.IntegerField(blank=True, null=True, default=0)
    obs     = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.product.name

    class Meta:
        ordering = ["product"]

    def serialize(self):
        return {
            "id": self.id,
            "account": self.account.id,
            "name": self.product.name,
            "price_1": self.price_1,
            "price_2": self.price_2,
            "price_3": self.price_3,
            "unit_1": self.unit_1,
            "unit_2": self.unit_2,
            "unit_3": self.unit_3,
            "stock": self.stock,
            "obs": self.obs,
        }


class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ['editable', 'code']


class AttributeForm(ModelForm):
    class Meta:
        model = Attribute
        exclude = ['account', 'product']


class Vendor(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    proveedor  = models.CharField(max_length=30)

    def __str__(self):
        return self.proveedor


class Client(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    cliente  = models.CharField(max_length=30)

    def __str__(self):
        return self.cliente


class Sucursal(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    sucursal  = models.CharField(max_length=30)

    def __str__(self):
        return self.sucursal


# Models for Sale
class Sale(models.Model):
    account     = models.ForeignKey(Account, on_delete=models.CASCADE)
    fecha       = models.DateField(default=timezone.now)
    cliente     = models.ForeignKey(Client, default="1", on_delete=models.PROTECT, related_name='invoices')
    sucursal    = models.ForeignKey(Sucursal, default="1", on_delete=models.PROTECT)
    total       = models.DecimalField(max_digits=6, decimal_places=2)

class SaleForm(ModelForm):
    class Meta:
        model = Sale
        exclude = ['account']
        widgets = {
            'fecha': Date(),
            'total': NumberInput(attrs={'class': 'form-control total','disabled':'disabled'}),
        }

class SaleItem(models.Model):
    orden       = models.ForeignKey(Sale,null=True, on_delete=models.CASCADE, related_name='order_items')
    producto    = models.ForeignKey(Attribute,null=True, on_delete=models.PROTECT)
    cantidad    = models.IntegerField()
    unidad      = models.CharField(max_length=15)
    precio      = models.DecimalField(max_digits=6, decimal_places=2)
    total       = models.DecimalField(max_digits=6, decimal_places=2)

class SaleItemForm(forms.ModelForm):
    stock = forms.IntegerField(widget= forms.NumberInput(attrs={'style': 'display: none' }))
    
    class Meta:
        model= SaleItem
        fields = '__all__'

SaleFormSet  = inlineformset_factory(
    Sale,
    SaleItem,
    fields=('producto',
            'cantidad', 
            'unidad',
            'precio',
            'total',
            ),
    widgets={
        'producto': Select(attrs={'class': 'form-control','disabled':'disabled'}) ,
        'cantidad': NumberInput(attrs={'class': 'form-control quantity'}), 
        'unidad': Select(attrs={'class': 'form-control unit'}, choices=[('unit_1', 'unidad'), ('unit_2', 'tira'), ('unit_3', 'caja')]),
        'precio': NumberInput(attrs={'class': 'form-control price'}),
        'total': NumberInput(attrs={'class': 'form-control'}),
    },
    extra=0,
    form=SaleItemForm,
)


# Models for Purchase
class Purchase(models.Model):
    account     = models.ForeignKey(Account, on_delete=models.CASCADE)
    fecha       = models.DateField(default=timezone.now)
    proveedor   = models.ForeignKey(Vendor, default="1", on_delete=models.PROTECT, related_name='invoices')
    sucursal    = models.ForeignKey(Sucursal, default="1", on_delete=models.PROTECT)
    total       = models.DecimalField(max_digits=6, decimal_places=2)

class PurchaseForm(ModelForm):
    class Meta:
        model = Purchase
        exclude = ['account']
        widgets = {
            'fecha': Date(),
            'total': NumberInput(attrs={'class': 'form-control total', 'disabled':'disabled'}),
        }

class Find(forms.Form):
    Find = forms.ModelChoiceField(widget=
        Select(attrs={
            'class': 'form-control selectpicker', 
            'data-live-search': 'true', 
            'title': 'Seleccionar producto', 
            'data-none-results-text':'No existe el producto'
            }), 
        queryset=Attribute.objects.all(), 
        empty_label=None)

class PurchaseItem(models.Model):
    orden       = models.ForeignKey(Purchase,null=True, on_delete=models.CASCADE, related_name='order_items')
    producto    = models.ForeignKey(Attribute,null=True, on_delete=models.PROTECT)
    cantidad    = models.IntegerField()
    unidad      = models.CharField(max_length=15)
    precio      = models.DecimalField(max_digits=6, decimal_places=2)
    total       = models.DecimalField(max_digits=6, decimal_places=2)

class PurchaseItemForm(forms.ModelForm):
    stock = forms.IntegerField(widget= forms.NumberInput(attrs={'style': 'display: none' }))
    
    class Meta:
        model= PurchaseItem
        fields = '__all__'

PurchaseFormSet  = inlineformset_factory(
    Purchase,
    PurchaseItem,
    fields=('producto',
            'cantidad', 
            'unidad',
            'precio',
            'total',
            ),
    widgets={
        'producto': Select(attrs={'class': 'form-control','disabled':'disabled'}) ,
        'cantidad': NumberInput(attrs={'class': 'form-control quantity'}), 
        'unidad': Select(attrs={'class': 'form-control unit'}, choices=[('unit_1', 'unidad'), ('unit_2', 'tira'), ('unit_3', 'caja')]),
        'precio': NumberInput(attrs={'class': 'form-control price'}),
        'total': NumberInput(attrs={'class': 'form-control'}),
    },
    extra=0,
    form= PurchaseItemForm
)
