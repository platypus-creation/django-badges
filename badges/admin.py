from django.contrib import admin

from badges.models import Badge, BadgeToUser

class BadgeAdmin(admin.ModelAdmin):
    fields = ('icon',)
    list_display = ('name','level')

admin.site.register(Badge, BadgeAdmin)


class BadgeToUserAdmin(admin.ModelAdmin):
    list_display = ('badge', 'user', 'created')
    list_filter = ('badge', 'user',)
    date_hierarchy = 'created'

admin.site.register(BadgeToUser, BadgeToUserAdmin)