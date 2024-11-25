from app import app, items, private


@private.get("/items/")
def inventory():
    # "items" name is already taken by the module imported above
    return app.render("items", items=items.get_all())
