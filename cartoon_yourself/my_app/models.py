
from django.db import models

class Search(models.Model):
    search = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.search)

    class Meta:
        verbose_name_plural = 'Searches'


class Job(models.Model):
    title = models.CharField(max_length=300)
    employer = models.CharField(max_length=300)
    requirements = models.CharField(max_length=500)
    description = models.CharField(max_length=700)
    salary = models.CharField(max_length=19)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} {self.employer} {self.salary} {self.created}'


class Cartoon(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    cartoon_image = models.ImageField(upload_to='images/', blank=True, null=True)
    
    def __str__(self):
        return f'{self.name}'
