from django.core.management.base import BaseCommand, CommandError
import badges

class Command(BaseCommand):
    args = ''
    help = 'Create badges in DB'

    def handle(self, *args, **options):
        for name, meta_badge in badges.registered_badges.items():
            meta_badge._keep_badge_updated()
            self.stdout.write('Badge "%s"\n' % name)
