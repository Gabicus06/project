from django.urls import path
from . import views 


urlpatterns = [
    path("", views.home, name="home"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("product", views.new_product, name="new_product"),
    path("products", views.products, name="products"),
    path("editProduct/<int:prod>", views.edit_product, name="edit_product"),
    path("buy", views.buy, name="buy"),
    path("sell", views.sell, name="sell"),
    path("report", views.report, name="report"),
    path("reportMonthly", views.reportMonthly, name="reportMontly"),
    path("editSale/<int:saleId>", views.editSale, name="editSale"),
    path("editPurchase/<int:purchaseId>", views.editPurchase, name="editPurchase"),

    # API Routes
    # path("new_created", views.new_created, name="new_created"),
    path("get_product/<int:prod>", views.get_product, name="get_product"),
    path("find_product", views.find_product, name="find_product"),
]