from django.contrib import admin
from .models import Search
from .models import Cartoon
from .models import Job

# Register models here.
admin.site.register(Search)
admin.site.register(Cartoon)
admin.site.register(Job)
