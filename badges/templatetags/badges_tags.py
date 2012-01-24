from django import template
from badges.utils import badge_count
from badges.models import LEVEL_CHOICES, Badge
import re
level_choices = dict(LEVEL_CHOICES)

register = template.Library()

@register.filter
def is_in(value,arg):
    return value in arg

@register.filter
def level_count(badges, level):
    return badges.filter(level=level).count()

@register.filter
def level_title(level):
    return level_choices[level]

@register.filter('badge_count')
def _badge_count(user_or_qs):
    return badge_count(user_or_qs)

@register.filter
def number_awarded(badge, user_or_qs=None):
    return badge.number_awarded(user_or_qs)
 
@register.filter
def progress_start(badge):
    return badge.meta_badge.progress_start
 
@register.filter
def progress_finish(badge):
    return badge.meta_badge.progress_finish
 
@register.filter
def progress(badge, user):
    return badge.meta_badge.get_progress(user)
 
@register.filter
def is_in_progress(badge, user):
    return 0 < badge.meta_badge.get_progress(user) < progress_finish(badge) 

@register.filter
def progress_percentage(badge, user):
    prog = badge.meta_badge.get_progress_percentage(user=user)
    return max(min(prog, 100), 0)
 
REGEXP = re.compile(r'([\w\s]+) as (\w+)')
class GetBadge(template.Node):
    badges = list(Badge.objects.all())
    def __init__(self, group, level, var_name):
        self.group = template.Variable(group)
        self.level = template.Variable(level)
        self.var_name = var_name

    def render(self, context):
        group = self.group.resolve(context)
        level = str(self.level.resolve(context))
        for badge in self.badges:
            if badge.meta_badge.level == level and badge.meta_badge.group == group:
                context[self.var_name] = badge
                return ''

@register.tag
def get_badge(parser, token):
    """
    {% get_badge group level as badge %}
    {% get_badge "member" 2 as badge %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    matches = REGEXP.search(arg)
    if not matches:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    args, var_name = matches.groups()
    try:
        group, level = args.split(None)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments group and level" % token.contents.split()[0])
    return GetBadge(group, level, var_name)
    