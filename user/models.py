from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Person(models.Model):
    firstname= models.CharField(max_length=120)
    lastname = models.CharField(max_length=120)
    gender = models.CharField(max_length=120, choices=[('M','Male'),("F","Female")])
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    date_created = models.DateTimeField(_('date created'), auto_now_add=True)
    date_updated = models.DateTimeField(_('date updated'), auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname)
