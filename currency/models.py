#-*- coding:utf-8 -*-
from django.db import models

# Create your models here.

class Valuta(models.Model):
    value = models.SlugField(unique=True)
    def __unicode__(self):
        return self.value

class TypePair(models.Model):
    left = models.ForeignKey("currency.Valuta", related_name="left_right")
    right = models.ForeignKey("currency.Valuta", related_name="funds_right")
    commission = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    #decimal_places = models.PositiveIntegerField(default=8)
    def __unicode__(self):
        return u"{left}_{right}".format(**{"left": self.left, "right":self.right})
    @property
    def tpair(self):
        return u"{left}_{right}".format(**{"left": self.left, "right":self.right})
    class Meta:
        unique_together = (("left", "right",),)
