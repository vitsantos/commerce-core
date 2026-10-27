import pytest
from django.db import IntegrityError, transaction

from catalog.models import Product

@pytest.mark.django_db

def test_product_creation():
    product = Product.objects.create(
        sku = "CAM-001",
        name = "Camiseta Básica",
        description = "Camiseta de algodão",
        price = "59.90",  
    )

    assert product.id is not None
    assert product.sku == "CAM-001" 
    assert product.price == "59.90" or str(product.price) == "59.90"
    assert product.is_active is True

@pytest.mark.django_db

def test_sku_must_be_unique():
    Product.objects.create(
        sku = "CAM-001",
        name = "Camiseta azul",
        price = "59.90",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Product.objects.create(
                sku = "CAM-001",
                name = "Camiste vermelha",
                price = "69.90"
            )