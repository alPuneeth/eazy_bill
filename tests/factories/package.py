def create_package(
    session,
    name=None,
    price=None
    ):
    import random
    from app.models.lookup.package import Package

    name = name or f"Package_{random.randint(100, 999)}"
    price = price or random.randint(100, 2000)

    package = Package(
        name=name,
        price=price
    )

    session.add(package)
    session.flush()
    return package