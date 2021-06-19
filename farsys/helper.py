from .models import Attribute, Match, Product

def get_account(self):
    return Match.objects.get(user=self).account
    

def update_stock(id, quantity):
    update = Attribute.objects.get(id=id)
    update.stock = update.stock + quantity
    update.save()

