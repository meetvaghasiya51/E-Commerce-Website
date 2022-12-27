from django.db import models

# Create your models here.
class Seller(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    passwd = models.CharField(max_length=50)
    pic = models.FileField(upload_to='sellet_profile', default='default.jpg')
    gst_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.first_name

class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(default=0.0)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    pic = models.FileField(upload_to='products', default='default.jpg')

    def __str__(self) -> str:
        return self.name