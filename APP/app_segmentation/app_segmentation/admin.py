from django.contrib import admin
from app_segmentation.models import *

class ImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Image, ImageAdmin)