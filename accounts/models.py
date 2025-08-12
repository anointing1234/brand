from django.db import models

class SalesCounter(models.Model):
    soft_copy_sold = models.IntegerField(default=0)
    hard_copy_sold = models.IntegerField(default=10)