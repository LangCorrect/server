from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """A template filter used to retrieve an item from a dictionary using a given key.

    Args:
        dictionary (dict): The dictionary from which to get the item.
        key (str/int): The key to look up in the dictionary.

    Returns:
        Value or None
    """
    return dictionary.get(key)
