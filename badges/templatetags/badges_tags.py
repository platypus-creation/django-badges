from django import template
from badges.utils import badge_count
from badges.models import LEVEL_CHOICES
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
    
class CheckNode(template.Node):
    def __init__(self, badge, check, obj, var_name):
        self.badge = template.Variable(badge)
        self.check = template.Variable(check)
        self.obj = template.Variable(obj)
        self.var_name = var_name
        
    def render(self, context):
        context[self.var_name] = getattr(self.badge.resolve(context).meta_badge, self.check.resolve(context))(self.obj.resolve(context))
        return ''

@register.tag
def check(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'([\w\s\.]+) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    args, var_name = m.groups()
    try:
        badge, check, obj = args.split(None)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments badge, check and obj" % token.contents.split()[0])
    return CheckNode(badge, check, obj, var_name)