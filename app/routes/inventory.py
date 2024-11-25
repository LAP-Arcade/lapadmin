from app import app, items, private


@private.get("/items/")
def inventory():
    return app.render("inventory", items=items.get_all())
