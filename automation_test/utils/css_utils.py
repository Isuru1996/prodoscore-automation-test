def class_to_color_name(class_str: str | None) -> str:
    """
    Map a CSS class string to a color name.
    Example: 'bg-primary-red' -> 'red', 'bg-primary-blue' -> 'blue', etc.
    Extend this mapping as needed for your color scheme.
    """
    if not class_str:
        return "unknown"
    color_map = {
        # Text color classes
        "text-ds-gray-600": "gray",
        "text-ds-gray-950": "gray",
        "text-ds-gray-800": "gray",
        "text-ds-red-500": "red",
        "text-ds-blue-500": "blue",
        "text-black": "black",
        # Background color classes
        "bg-primary-red": "red",
        "bg-primary-blue": "blue",
        "bg-ds-gray-800": "gray",
        "bg-warning-100": "yellow",
        "bg-success-100": "green",
        "text-primary-blue": "blue",
        "text-primary-red": "red",
        "text-primary-gray": "gray",
    }
    for cls in class_str.split():
        if cls in color_map:
            return color_map[cls]
    return "unknown"
