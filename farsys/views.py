from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json 
from django.utils import timezone
from .helper import get_account, update_stock

from .models import *

# Create your views here.

@login_required
def home(request):
    account = get_account(request.user)

    # Calculate daily sale
    date =  timezone.now().date()
    diario = 0
    pre = Sale.objects.values_list('total', flat=True).filter(account=account).filter(fecha=date)
    for t in pre:
        diario = diario + t
    
    # Calculate monthly sale
    month = timezone.now().month
    monthly = 0
    print(month)
    pre = Sale.objects.values_list('total', flat=True).filter(account=account).filter(fecha__month=month)
    for t in pre:
        monthly = monthly + t

    # Calculate average
    days = timezone.now().day
    average = monthly/days

    return render(request, "farsys/home.html",{
        'montly': monthly,
        'diario': diario,
        'average': average,
    })

def login_view(request):
    if request.method == "POST":
        
        # Attempt to sign user in
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "farsys/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "farsys/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        name = request.POST['name']

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "farsys/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "farsys/register.html", {
                "message": "Username already taken."
            })
        # Create account
        create = Account(account=name)
        create.save()

        login(request, user)

        # Match user with account
        match = Match(user=request.user, account=create)
        match.save()

        # Create sucursal, vendor, client, category
        suc = Sucursal(account=create, sucursal=create)  
        suc.save()

        vendor = Vendor(account=create, proveedor="Genérico")  
        vendor.save()
        
        client = Client(account=create, cliente="Genérico")
        client.save()
        
        category = Category(account=create, name="Genérico")
        category.save()     

        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "farsys/register.html")


def new_product(request):
    action = "Crear"
    account = request.user.current_account
    
    if request.method == "POST":
        # Add New Drug from GenericList
        if "Find" in request.POST:
            name = Product.objects.get(pk=request.POST["Find"]) 
            newProduct, created = Attribute.objects.get_or_create(product=name, account=account())
            print(created)
            return JsonResponse({'prod': newProduct.id, 'name': newProduct.product.name})
        
        # Create New Product
        else:
            form = ProductForm(request.POST)
            form2 = AttributeForm(request.POST)
            if form.is_valid() and form2.is_valid():
                # save product
                newProduct = form.save(commit=False)
                print("1")
                newProduct.name = newProduct.name.upper()
                print("2")
                newProduct.save()

                # save attribute
                atrib = form2.save(commit=False)
                atrib.product = newProduct
                atrib.account = account()
                atrib.save()
                print("Attribute saved")

                if "modal" in request.POST:
                    return JsonResponse ({'prod': atrib.id, 'name': atrib.product.name})
                else:
                    messages.success(request, 'Se creó el producto correctamente')
                    return redirect('/')
    form = ProductForm()
    form2 = AttributeForm()
    form.fields["category"].queryset = Category.objects.filter(account=account())
    return render(request, "farsys/product.html", {
        'action': action, 
        'form': form,
        'form2': form2,
    })


def edit_product(request, prod):
    action = "Editar"
    account = request.user.current_account
    toEdit = Attribute.objects.get(pk = prod)
    nameToEdit = Product.objects.get(pk = toEdit.product.id)
    
    # Avoid to edit products from other account
    if toEdit.account != account():
        messages.error(request, 'Este producto no existe')
        return redirect('/')

    # Update product
    if request.method == "POST":
        form = ProductForm(request.POST, instance=nameToEdit)
        form2 = AttributeForm(request.POST, instance=toEdit)
        if form.is_valid() and form2.is_valid():
            form.save()
            form2.save()
            messages.success(request, 'Se actualizó el producto correctamente')
            return redirect('/')

    form = ProductForm(instance=nameToEdit)
    form2 = AttributeForm(instance=toEdit)
    form.fields["category"].queryset = Category.objects.filter(account=account())
    return render(request, "farsys/product.html", {
        'action': action, 
        'form': form,
        'form2': form2,
        'toEdit': toEdit.id,
    })


def products(request):
    if request.method == "POST":
        prod = request.POST["input"]
        return redirect('edit_product', prod)
    
    result = Attribute.objects.filter(account=get_account(request.user)).order_by('product')
    return render(request, "farsys/products.html", {
        'data': result,
    })


def report(request):
    date = timezone.now().date()
    account = get_account(request.user)
    
    if request.method == "POST":
        date = request.POST["date"]

    # Obtain data for selected day 
    pre = Sale.objects.values_list('id', flat=True).filter(fecha=date).filter(account=account)
    result = SaleItem.objects.filter(orden__in = set(pre))

    # Obatin Total 
    gTotal = 0
    for row in result:
        a = row.total
        gTotal = gTotal + a

    return render(request, 'farsys/report.html',{
        'data': result,
        'gTotal': gTotal,
        'date': date,
    })


def reportMonthly(request):
    month = timezone.now().month

    # Obtain data for selected day 
    pre = Sale.objects.filter(fecha__month=month)
    result = SaleItem.objects.filter(orden__in = set(pre))
    
    gTotal = 0
    print(result)
    for row in pre:
        a = row.Total
        gTotal = gTotal + a

    return render(request, 'farsys/report.html',{
        'data': result,
        'gTotal': gTotal,
        # 'date': date,
    })


def buy(request):
    account = request.user.current_account()
    if request.method == "POST":
        form = PurchaseForm(request.POST)
        form3 = PurchaseFormSet(request.POST)

        if form.is_valid() and form3.is_valid():
            # Save order
            order = form.save(commit=False)
            order.account = account
            order.save()

            for form in form3:
                # Save items
                item = form.save(commit=False)
                if not form.cleaned_data['DELETE']:
                    item.orden = order
                    item.save()

                    #Update Stock
                    update_stock(item.producto.id, item.cantidad)
            return redirect('/')

    form = PurchaseForm()
    form.fields["proveedor"].queryset = Vendor.objects.filter(account=account)
    form.fields["sucursal"].queryset = Sucursal.objects.filter(account=account)
    form2 = Find()
    form2.fields["Find"].queryset = Attribute.objects.filter(account=account)
    form3 = PurchaseFormSet()
    form4 = ProductForm()
    form4.fields["category"].queryset = Category.objects.filter(account=account)
    form5 = AttributeForm()
    form6 = Find()
    form6.fields["Find"].queryset = Product.objects.filter(editable=False)
    return render(request, "farsys/transaction.html", {
        'form': form,
        'form2': form2,
        'form3': form3,
        'form4': form4,
        'form5': form5,
        'form6': form6,
        'action': "Registrar compra",
    })


def editPurchase(request, purchaseId):
    account = request.user.current_account()
    toEdit = Purchase.objects.get(pk = purchaseId)
    print(toEdit)
    if request.method == "POST":
        form = PurchaseForm(request.POST, instance=toEdit)
        form3 = PurchaseFormSet(request.POST, request.FILES, instance=toEdit)
        print("before validate")
        if form.is_valid() and form3.is_valid():
            # Save order
            order = form.save()
            for form in form3:
                    # Save items
                    item = form.save(commit=False)
                    if not form.cleaned_data['DELETE']:
                        item.orden = order
                        item.save()
                    # Delete items
                    else:
                        try:
                            item.delete()
                        except:
                            print("Something")

                    # Update Stock
                    update_stock(item.producto.id, form.cleaned_data['stock'])
            return redirect('/')

    form = PurchaseForm(instance=toEdit)
    form.fields["proveedor"].queryset = Vendor.objects.filter(account=account)
    form.fields["sucursal"].queryset = Sucursal.objects.filter(account=account)
    form2 = Find()
    form2.fields["Find"].queryset = Attribute.objects.filter(account=account)
    form3 = PurchaseFormSet(instance=toEdit)
    form4 = ProductForm()
    form4.fields["category"].queryset = Category.objects.filter(account=account)
    form5 = AttributeForm()
    form6 = Find()
    form6.fields["Find"].queryset = Product.objects.filter(editable=False)
    return render(request, "farsys/transaction.html", {
        'form': form,
        'form2': form2,
        'form3': form3,
        'form4': form4,
        'form5': form5,
        'form6': form6,
        'action': "Editar compra",
        'purchaseId': purchaseId,
    })


def sell(request):
    account = request.user.current_account()
    if request.method == "POST":
        form = SaleForm(request.POST)
        form3 = SaleFormSet(request.POST)

        if form.is_valid():
            print("form validated")
            if form3.is_valid():
                print("form3 validated")
                # Save order
                order = form.save(commit=False)
                order.account = account
                order.save()

                # Save items
                for form in form3:
                    item = form.save(commit=False)
                    if not form.cleaned_data['DELETE']:
                        item.orden = order
                        item.save()

                    #Update Stock
                    update_stock(item.producto.id, -item.cantidad)
                return redirect('/')

    form = SaleForm()
    form.fields["cliente"].queryset = Client.objects.filter(account=account)
    form.fields["sucursal"].queryset = Sucursal.objects.filter(account=account)
    form2 = Find()
    form2.fields["Find"].queryset = Attribute.objects.filter(account=account)
    form3 = SaleFormSet()
    form4 = ProductForm()
    form4.fields["category"].queryset = Category.objects.filter(account=account)
    form5 = AttributeForm()
    form6 = Find()
    form6.fields["Find"].queryset = Product.objects.filter(editable=False)
    return render(request, "farsys/transaction.html", {
        'form': form,
        'form2': form2,
        'form3': form3,
        'form4': form4,
        'form5': form5,
        'form6': form6,
        'action': "Registrar venta",
    })


def editSale(request, saleId):
    account = request.user.current_account()
    toEdit = Sale.objects.get(pk = saleId)
    if request.method == "POST":
        form = SaleForm(request.POST, instance=toEdit)
        form3 = SaleFormSet(request.POST, request.FILES, instance=toEdit)
        
        if form.is_valid() and form3.is_valid():
            # Save order
            order = form.save()

            for form in form3:
                # Save items
                item = form.save(commit=False)
                if not form.cleaned_data['DELETE']:
                    item.orden = order
                    item.save()

                else:
                    try:
                        item.delete()
                    except:
                        print("Something")
                
                # Update Stock
                update_stock(item.producto.id, -form.cleaned_data['stock'])
            return redirect('/')

    form = SaleForm(instance=toEdit)
    form.fields["cliente"].queryset = Client.objects.filter(account=account)
    form.fields["sucursal"].queryset = Sucursal.objects.filter(account=account)
    form2 = Find()
    form2.fields["Find"].queryset = Attribute.objects.filter(account=account).filter(stock__gt=0)
    form3 = SaleFormSet(instance=toEdit)
    form4 = ProductForm()
    form4.fields["category"].queryset = Category.objects.filter(account=account)
    form5 = AttributeForm()
    form6 = Find()
    form6.fields["Find"].queryset = Product.objects.filter(editable=False)
    return render(request, "farsys/transaction.html", {
        'form': form,
        'form2': form2,
        'form3': form3,
        'form4': form4,
        'form5': form5,
        'form6': form6,
        'action': "Editar venta",
        'saleId': saleId,
    })


def get_product(request, prod):
    product = Attribute.objects.get(id = prod)
    return JsonResponse(product.serialize())


def find_product(request):
    data = Attribute.objects.filter(account=get_account(request.user)).order_by('product')
    return JsonResponse([prod.serialize() for prod in data], safe=False)