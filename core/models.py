import os
import platform
import string

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser
)

from dirtyfields import DirtyFieldsMixin
from jsonfield import JSONField


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    objects = UserManager()

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(max_length=255)
    emoji = models.CharField(max_length=100, default='')
    picture_url = models.CharField(max_length=255, default='')

    slack_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    api_key = models.CharField(
        max_length=50,
        default=lambda: ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    )

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        # The user is identified by their email address
        return self.nickname

    def get_short_name(self):
        # The user is identified by their email address
        return self.nickname

    def __unicode__(self): # __unicode__ on Python 2
        return self.nickname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def is_present(self):
        return self.devices.filter(is_present=True).exists()

    def last_seen(self):
        devices = self.devices.all().order_by("-last_seen")[:1]
        if devices.count() > 0:
            return devices[0].last_seen


class Home(models.Model):
    name = models.CharField(max_length=255)
    notification_settings = JSONField(default='{}')

    is_in_vacation_mode = models.BooleanField(default=False)
    is_in_away_mode = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def should_notify(self, channel, action):
        channel_settings = self.notification_settings.get(channel)
        if not channel_settings:
            return False

        return channel_settings.get(action, False)

    def get_occupancy_count(self):
        return self.devices.filter(is_present=True).count()


class Room(models.Model):
    name = models.CharField(max_length=255)
    home = models.ForeignKey(Home)

    def __unicode__(self):
        return self.name


class Device(DirtyFieldsMixin, models.Model):
    home = models.ForeignKey(Home, related_name='devices')
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name="devices")
    mac = models.CharField(max_length=17)
    ip = models.CharField(max_length=15)
    is_present = models.BooleanField(default=False)

    last_scanned = models.DateTimeField()
    last_seen = models.DateTimeField()

    def __unicode__(self):
        return self.name

    def ping(self, timeout=1):
        if platform.system() == "Darwin":
            command = "ping -q -o -t {} {} ".format(timeout, self.ip)
        else:
            command = "arping -I wlan0 -q -f -w{} {}".format(timeout, self.ip)

        return True if os.system(command) == 0 else False


from .signals import *
