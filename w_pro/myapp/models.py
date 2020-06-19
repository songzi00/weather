# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class User(models.Model):
    objects = models.Manager()
    """用户表"""

    gender = (
        ('male','男'),
        ('female','女'),
    )

    name = models.CharField(max_length = 128,unique = True)
    password = models.CharField(max_length = 256)
    email = models.EmailField(unique = True)
    sex = models.CharField(max_length = 32,choices = gender,default = "男")
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'

class Cweather(models.Model):
    area = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    get_time = models.CharField(max_length=255, blank=True, null=True)
    max_tp = models.CharField(max_length=255, blank=True, null=True)
    min_tp = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cweather'
