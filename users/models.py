#-*- coding:utf-8 -*-
from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.


class MyCustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=MyCustomUserManager.normalize_email(email),
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        u = self.create_user(username, email, password=password)
        u.is_active = u.is_staff = u.is_superuser = True
        u.save(using=self._db)
        return u


class Profile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField((u'Имя пользователя'), max_length=40, unique=True)
    email = models.EmailField('E-mail', unique=True)
    date_joined = models.DateTimeField(
        (u'Дата регистрации'), default=timezone.now)
    is_active = models.BooleanField(
        (u'Активный'), default=True,
        help_text=(u'Отметьте, если пользователь должен считаться активным. '
                    u'Уберите эту отметку вместо удаления аккаунта.'))
    is_staff = models.BooleanField(
        (u'Статус персонала'), default=False,
        help_text=(u'Отметьте, если пользователь может входить в '
                    u'административную часть сайта.'))
    class Meta:
        verbose_name = (u'Профиль')
        verbose_name_plural = (u'Профили')

    USERNAME_FIELD = 'email'

    objects = MyCustomUserManager()

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_role(self):
        """if cache.get('get_role_%s' % self.pk) is None:
            cache.set(
                'get_role_%s' % self.pk,
                [x['role'] for x in self.profilerole_set.all().values('role')] or ['client'])
        return cache.get('get_role_%s' % self.pk) or list()
        """
        return [x['role'] for x in self.profilerole_set.all().values('role')] or ['customer']

    def is_performer(self):
        performer = self.get_role()
        if 'manager' in performer:
            performer.remove('manager')
        if performer:
            return True
        return False

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        return super(Profile, self).save(*args, **kwargs)

class ProfileRole(models.Model):
    PROFILE_ROLE = (
        ('manager', (u'Менеджер')),
        ('customer', (u'клиент')),
    )

    profile = models.ForeignKey("users.Profile", verbose_name=(u'Профиль'))
    role = models.CharField((u'Роль'), choices=PROFILE_ROLE, max_length=15)

    class Meta:
        verbose_name = (u'Роль пользователя')
        verbose_name_plural = (u'Роли пользователя')
        unique_together = (('profile', 'role'),)

    def __unicode__(self):
        return self.role
