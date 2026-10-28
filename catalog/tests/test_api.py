import pytest
from rest_framework.test import APIClient

from catalog.models import Product

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_list_active_products(api_client):
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

    response = api_client.get("/api/products/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["sku"] == "CAM-001"


@pytest.mark.django_db
def test_anonymous_user_cannot_create_product(api_client):

    response = api_client.post(
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
def test_negative_price_is_rejected_by_api(api_client):

    User = get_user_model()
    user = User.objects.create_user(
        username="testuser",
        password="testpassword123",
    )

    operators_group, _ = Group.objects.get_or_create(
        name="Operadores"
    )
    user.groups.add(operators_group)



    api_client.force_authenticate(user=user)

    response = api_client.post(
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
def test_product_pagination(api_client):
    for i in range(3):
        Product.objects.create(
            sku = f"TEST-{i:03d}",
            name = f"Produto {i}",
            price = "29.90",
            is_active = True,
        )


    response = api_client.get("/api/products/")

    assert response.status_code == 200
    assert response.data['count'] == 3
    assert len(response.data["results"]) == 2
    assert response.data["next"] is not None
    assert response.data["previous"] is None

    response = api_client.get("/api/products/?page=2")

    assert response.status_code == 200
    assert response.data['count'] == 3
    assert len(response.data["results"]) == 1
    assert response.data["next"] is None
    assert response.data["previous"] is not None



@pytest.mark.django_db
def test_authenticated_user_without_group_cannot_create_product(api_client):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(
        username="user_sem_grupo",
        password="testspassword123",
    )

    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/products/",
        {
            "sku": "CAM-005",
            "name": "Produto do operador",
            "price": "49.90",
        },
        format="json",
    )

    assert response.status_code == 403
    assert not Product.objects.filter(sku="CAM-005").exists()


@pytest.mark.django_db
def test_operator_can_create_product(api_client):
    from django.contrib.auth import get_user_model
    from django. contrib.auth.models import Group

    User = get_user_model()
    operator = User.objects.create_user(
        username="operador",
        password="test123",
    )

    operators_group, _ = Group.objects.get_or_create(name="Operadores")
    operator.groups.add(operators_group)


    api_client.force_authenticate(user=operator)

    response = api_client.post(
        "/api/products/",
        {
            "sku": "CAM-006",
            "name": "Produto do operador",
            "price": "49.90",
        },
        format="json",
    )

    assert response.status_code ==201
    assert Product.objects.filter(sku="CAM-006").exists()

@pytest.mark.django_db
def test_administrator_can_create_product(api_client):

    User = get_user_model()
    administrator = User.objects.create_user(
        username="administrador",
        password="test123",
    )


    administrator_group, _ = Group.objects.get_or_create(
        name="Administradores"
    )

    administrator.groups.add(administrator_group)


    api_client.force_authenticate(user=administrator)

    response = api_client.post(
        "/api/products/",
        {
            "sku": "CAM-007",
            "name": "Produto do administrador",
            "price": "59.90",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Product.objects.filter(sku="CAM-007").exists()



@pytest.mark.django_db
def test_product_creator_can_edit_product(api_client):

    User = get_user_model()
    creator = User.objects.create_user(
        username="criador",
        password="test123",
    )

    operators_group, _ = Group.objects.get_or_create(
        name="Operadores"
        )
    creator.groups.add(operators_group)


    product = Product.objects.create(
        sku="EDIT-001",
        name="Nome original",
        price="50.00",
        created_by=creator,
    )

    api_client.force_authenticate(user=creator)

    response = api_client.patch(
        f"/api/products/{product.id}/",
        {"name": "Nome atualizado"},
        format="json",
    )

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.name == "Nome atualizado"



@pytest.mark.django_db
def test_operator_cannot_edit_another_creators_product(api_client):
    User = get_user_model()
    creator = User.objects.create_user(
        username="Criador2",
        password="test123",
    )
    other_operator = User.objects.create_user(
        username="outro_operador",
        password="test123",
    )

    operators_group, _ = Group.objects.get_or_create(name="Operadores")
    creator.groups.add(operators_group)
    other_operator.groups.add(operators_group)

    product = Product.objects.create(
        sku="EDIT-002",
        name="Produto original",
        price="50.00",
    )

    api_client.force_authenticate(user=other_operator)


    response = api_client.patch(
        f"/api/products/{product.id}/",
        {"name": "Tentativa de alteração"},
        format="json",
    )

    assert response.status_code == 403
    product.refresh_from_db()
    assert product.name == "Produto original"


@pytest.mark.django_db
def test_operator_cannot_delete_product(api_client):
    User = get_user_model()
    operator = User.objects.create_user(
        username="Operador_delete",
        password="test123",
    )

    operators_group, _ = Group.objects.get_or_create(name="Operadores")
    operator.groups.add(operators_group)

    product = Product.objects.create(
        sku="DEL-001",
        name="Produto protegido",
        price="30.00",
    )

    api_client.force_authenticate(user=operator)

    response = api_client.delete(f"/api/products/{product.id}/")

    assert response.status_code == 403
    assert Product.objects.filter(pk=product.pk).exists()



@pytest.mark.django_db
def test_administrator_can_list_inactive_products(api_client):

    User = get_user_model()
    admin = User.objects.create_user(
        username="admin_inactive",
        password="test123",
    )

    administrators_group, _ = Group.objects.get_or_create(name="Administradores")

    admin.groups.add(administrators_group)

    Product.objects.create(
        sku="ACTIVE-001",
        name="Produto ativo",
        price="10.00",
        is_active=True,
    )
    Product.objects.create(
        sku="INACTIVE-001",
        name="Produto inativo",
        price="20.00",
        is_active=False,
    )

    api_client.force_authenticate(user=admin)
    response = api_client.get("/api/products/")

    assert response.status_code == 200
    product_names = [product["name"] for product in response.data["results"]]
    assert "Produto ativo" in product_names
    assert "Produto inativo" in product_names


@pytest.mark.django_db
def test_anonymous_user_cannot_list_inactive_products(api_client):
    from catalog.models import Product

    Product.objects.create(
        sku="ACTIVE-002",
        name="Produto ativo",
        price="10.00",
        is_active=True,
    )
    Product.objects.create(
        sku="INACTIVE-002",
        name="Produto inativo",
        price="20.00",
        is_active=False,
    )

    response = api_client.get("/api/products/")

    assert response.status_code == 200
    product_names = [product["name"] for product in response.data["results"]]
    assert "Produto ativo" in product_names
    assert "Produto inativo" not in product_names
