from django import template

register = template.Library()

@register.filter
def in_group(user, group_name):
    # superusers always have “in group” rights
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()

@register.filter
def in_groups(user, group_names):
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    names = [n.strip() for n in group_names.split(',') if n.strip()]
    return user.groups.filter(name__in=names).exists()
