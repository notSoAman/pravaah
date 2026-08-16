from django.contrib import admin

from .models import *

admin.site.register(Member)
admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(Movie)
admin.site.register(Journal)
admin.site.register(JournalImport)
admin.site.register(HeroSlide)