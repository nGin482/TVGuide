from database.models.SearchItemModel import SearchItem

search_items: list['SearchItem'] = [
    SearchItem(
        "Doctor Who",
        False,
        14
    ),
    SearchItem(
        "Endeavour",
        True,
        9
    ),
    SearchItem(
        "NCIS",
        True,
        9
    )
]