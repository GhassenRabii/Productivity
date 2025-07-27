from django import template

register = template.Library()

@register.filter
def in_group(user, group_name):
    return bool(
        getattr(user, 'is_authenticated', False)
        and user.groups.filter(name=group_name).exists()
    )

@register.filter
def in_groups(user, group_names):
    if not getattr(user, 'is_authenticated', False):
        return False
    names = [name.strip() for name in group_names.split(',') if name.strip()]
    return user.groups.filter(name__in=names).exists()
