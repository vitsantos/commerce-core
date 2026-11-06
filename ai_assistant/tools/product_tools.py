from catalog.models import Product
from django.db.models import Q

def search_products(query: str) -> list[dict]:
    # Busca produtos ativos pelo nome ou descrição.
    products = Product.objects.filter(
        is_active = True
    ).filter(
        name__icontains=query
    ) | Product.objects.filter(
        is_active=True,
        description__icontains=query
    )

    return [
        {
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "price": product.price,
        }
        for product in products.distinct()
    ]