#-*- coding:utf-8 -*-
from django.db import models

# Create your models here.

class News(models.Model):
    date = models.DateTimeField(u"Дата")
    title = models.CharField(u"Заголовок", max_length=255)
    smalltext = models.TextField(u"Вводный абзац")
    text = models.TextField(u"Текст")
    class Meta:
        verbose_name = u"новость"
        verbose_name_plural = u"Новости"
    def __unicode__(self):
        return "%s" % (self.date)
    @classmethod
    def getlast(cls, c=4):
        n = cls.objects.order_by("-date")
        if n:
            n = n[0:c]
        return n
