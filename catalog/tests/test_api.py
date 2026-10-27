import pytest
from rest_framework.test import APIClient

from catalog.models import Product

@pytest.mark.django_db

def test_list_active_products():
    Product.objects.create(
        sku="CAM-001",
        name="Camiseta",
        price="59.90",
        is_active=True,
    )
    Product.objects.create(
        sku="CAM-002",
        name="Produto desativado",
        price="39.90",
        is_active=False,
    )

    client = APIClient()
    response = client.get("/api/products/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["sku"] == "CAM-001"


@pytest.mark.django_db
def test_anonymous_user_cannot_create_product():
    client = APIClient()

    response = client.post(
        "/api/products/",
        {
            "sku": "CAM-003",
            "name": "Nova camiseta",
            "price": "49.90",
        },
        format="json",
    )

    assert response.status_code == 403
    assert not Product.objects.filter(sku="CAM-003").exists()


@pytest.mark.django_db
def test_negative_price_is_rejected_by_api():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(
        username="testuser",
        password="testpassword123",
    )


    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/products/",
        {
            "sku": "CAM-004",
            "name": "Camiseta inválida",
            "price": "-10.00",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "price" in response.data
    assert not Product.objects.filter(sku="CAM-004").exists()




@pytest.mark.django_db
def test_product_pagination():
    for i in range(3):
        Product.objects.create(
            sku = f"TEST-{i:03d}",
            name = f"Produto {i}",
            price = "29.90",
            is_active = True,
        )

    client = APIClient()

    response = client.get("/api/products/")

    assert response.status_code == 200
    assert response.data['count'] == 3
    assert len(response.data["results"]) == 2
    assert response.data["next"] is not None
    assert response.data["previous"] is None

    response = client.get("/api/products/?page=2")

    assert response.status_code == 200
    assert response.data['count'] == 3
    assert len(response.data["results"]) == 1
    assert response.data["next"] is None
    assert response.data["previous"] is not None
