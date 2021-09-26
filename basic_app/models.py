from django.db import models


# Create your models here.

class ClientList(models.Model):
    code = models.CharField(max_length=20, unique=True)
    parent = models.CharField(max_length=10)
    currency = models.CharField(max_length=3)
    start_date = models.DateTimeField()
    name = models.CharField(max_length=100)
    portfolios = models.TextField(blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.name
