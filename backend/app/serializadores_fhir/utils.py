def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value == "":
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False


def clean_fhir(obj):
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            cleaned_value = clean_fhir(value)
            if _is_empty(cleaned_value):
                continue
            cleaned[key] = cleaned_value
        return cleaned

    if isinstance(obj, list):
        cleaned_list = []
        for item in obj:
            cleaned_item = clean_fhir(item)
            if _is_empty(cleaned_item):
                continue
            cleaned_list.append(cleaned_item)
        return cleaned_list

    if isinstance(obj, str):
        return obj.strip()

    return obj
