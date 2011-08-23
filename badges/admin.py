from django.contrib import admin

from badges.models import Badge

class BadgeAdmin(admin.ModelAdmin):
    fields = ('icon',)
    list_display = ('name','level')

admin.site.register(Badge, BadgeAdmin)