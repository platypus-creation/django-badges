from django.contrib import admin

from badges.models import Badge, BadgeToUser

class BadgeAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'level', 'icon')
    fields = ('icon',)
    list_filter = ('level',)

admin.site.register(Badge, BadgeAdmin)


class BadgeToUserAdmin(admin.ModelAdmin):
    list_display = ('badge', 'user', 'created')
    list_filter = ('badge', 'user',)
    date_hierarchy = 'created'

    raw_id_fields = ('user',)
    autocomplete_lookup_fields = {
        'fk': ['user'],
    }
    
admin.site.register(BadgeToUser, BadgeToUserAdmin)