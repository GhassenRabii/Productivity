from django import template

register = template.Library()

@register.simple_tag
def in_group(user, group_name):
    """
    Returns True if the user is authenticated and belongs to the given group.
    Usage in templates:
        {% load group_tags %}
        {% if in_group request.user "users" %}
            ...
        {% endif %}
    """
    return user.is_authenticated and user.groups.filter(name=group_name).exists()

@register.simple_tag
def in_groups(user, *group_names):
    """
    Returns True if the user is authenticated and belongs to any of the given groups.
    Usage in templates:
        {% load group_tags %}
        {% if in_groups request.user "admin" "dev" %}
            ...
        {% endif %}
    """
    return (
        user.is_authenticated
        and user.groups.filter(name__in=group_names).exists()
    )
