from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Split a string by the given separator"""
    if value:
        return value.split(arg)
    return []

@register.filter(name='format_seconds')
def format_seconds(seconds):
    """Format seconds into a readable time string (e.g., '1m 30s' or '45s')"""
    if not seconds:
        return "0s"
    
    seconds = int(seconds)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes > 0:
        return f"{minutes}m {remaining_seconds}s"
    return f"{seconds}s"
