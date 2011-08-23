from django.test import TestCase
from django.contrib.auth.models import User

from badges.utils import MetaBadge, registered_badges, RequiresUserOrProgress
from badges.utils import register as register_badge
from badges.signals import badge_awarded
from badges.models import Badge
from badges.templatetags.badges_tags import badge_count, level_title, \
    level_count, number_awarded

class BadgeTests(TestCase):
    def setUp(self):
        registered_badges.clear()
        class YouveGotMail(MetaBadge):
            name = 'youve-got-mail'
            model = User
            one_time_only = True
            
            title = "You've got mail"
            description = "Filled in your E-mail address"
            level = "1"
            
            def get_user(self, instance):
                return instance
            
            def check_email(self, instance):
                return bool(instance.email)
            
        self.meta_badge = YouveGotMail
    
    def test_badge_creation(self):
        badge = Badge.objects.get(name=self.meta_badge.name)
        self.assertTrue(isinstance(badge.meta_badge, self.meta_badge))
        
    def test_badge_registration(self):
        meta_badge_instance = registered_badges[self.meta_badge.name]
        self.assertTrue(isinstance(meta_badge_instance, self.meta_badge))
        
    def test_badge_registration_only_happens_once(self):
        meta_badge = register_badge(self.meta_badge)
        meta_badge_instance = registered_badges[meta_badge.name]
        register_badge(self.meta_badge)
        
        self.assertTrue(registered_badges[meta_badge.name] is meta_badge_instance)

    def test_badge_progress(self):
        badge = Badge.objects.get(name=self.meta_badge.name)

        user = User(username='zodiac', first_name='john', last_name='doe')
        user.save()

        self.assertEqual(badge.meta_badge.get_progress(user), 0)
        self.assertEqual(badge.meta_badge.get_progress_percentage(user=user), 0.0)
        self.assertRaises(RequiresUserOrProgress, badge.meta_badge.get_progress_percentage)

        user.email = "icanhasemailz@example.com"
        user.save()

        self.assertEqual(badge.meta_badge.get_progress(user), 1)
        self.assertEqual(badge.meta_badge.get_progress_percentage(user=user), 100.0)        
        
    def test_badge_earned_signal(self):
        test_self = self
        
        signal_handler_kwargs = {}
        def signal_handler(**kwargs):
            signal_handler_kwargs.update(kwargs)
        badge_awarded.connect(signal_handler)
        
        user = User(username='tester', first_name='john', last_name='doe')
        user.save()
        
        # signal didn't fire because email was blank
        self.assertFalse(signal_handler_kwargs)
        
        user.email = 'woot@example.com'
        user.save()
        
        # make sure the signal fired and the kwargs were correct
        self.assertTrue( isinstance(signal_handler_kwargs.get('sender'), self.meta_badge) )
        self.assertEqual(signal_handler_kwargs.get('user'), user)
        self.assertEqual(signal_handler_kwargs.get('badge'), Badge.objects.all()[0])

    def test_template_tags(self):
        badge = Badge.objects.get(name=self.meta_badge.name)

        self.assertEqual(level_count(Badge.objects.all(), '1'), 1)
        self.assertEqual(level_count(Badge.objects.all(), '2'), 0)

        self.assertEqual(level_title(badge.level), "Bronze")

        user = User(username='headcase', first_name='head', last_name='case')
        user.save()
        
        self.assertEqual(badge_count(user), [{'count': 0, 'badge__level': '1'}, {'count': 0, 'badge__level': '2'}, {'count': 0, 'badge__level': '3'}, {'count': 0, 'badge__level': '4'}])

        user.email = "oops@example.com"
        user.save()

        self.assertEqual(badge_count(user), [{'count': 1, 'badge__level': '1'}, {'count': 0, 'badge__level': '2'}, {'count': 0, 'badge__level': '3'}, {'count': 0, 'badge__level': '4'}])        
        
        
        
                
