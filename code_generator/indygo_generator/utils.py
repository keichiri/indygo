def to_camel_case(snake_case):
    words = snake_case.split('_')
    new_items = [words[0]]
    new_items.extend([word.title() for word in words[1:]])
    return ''.join(new_items)