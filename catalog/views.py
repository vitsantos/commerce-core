from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse,
    OpenApiExample,
    )

from rest_framework import filters, viewsets, serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer


from .permissions import CanCreateProduct, ProductPermission


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]

    filterset_fields = ["sku", "price"]
    search_fields = ["name", "description", "sku"]


    @extend_schema(
            summary = 'Listar produtos',
            description = 'Lista os produtos ativos, com suporte a filtros, busca e paginação.',
            responses = {200: ProductSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



    @extend_schema(
            summary = 'Cadastrar produto',
            description = 'Cadastra um produto. Requer autenticação. '
            "O SKU deve ser único e o preço não pode ser negativo.",
            responses = {
                201: ProductSerializer,
                400: OpenApiResponse(
                   response=inline_serializer(
                        name="ProductValidationError",
                        fields={
                            "sku": serializers.ListField(
                                child = serializers.CharField(),
                                required = False,
                            ),
                            "price": serializers.ListField(
                                child=serializers.CharField(),
                                required = False,
                            ),
                            "name": serializers.ListField(
                            child=serializers.CharField(),
                            required=False,
                            ),
                            "description": serializers.ListField(
                                child=serializers.CharField(),
                                required=False,
                            ),
                            "non_field_errors": serializers.ListField(
                                child=serializers.CharField(),
                                required=False,
                            ),
                        },
                    ),
                    description="Dados inválidos, com o SKU duplicado ou preço negativo.",
                           
                ),
                401: OpenApiResponse(description="Não autenticado."),
                403: OpenApiResponse(description="Permissão negada."),
            },
            examples=[
                OpenApiExample(
                    "Produto Válido",
                    value={
                        "sku": "TECLADO-001",
                        "name": "Teclado mecânico",
                        "description": "Teclado USB para uso diário",
                        "price": "149.90",
                        "is_active": True,
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Cadastro realizado",
                    value={
                        "id": 1,
                        "sku": "TECLADO-001",
                        "name": "Teclado mecânico",
                        "description": "Teclado USB para uso diário",
                        "price": "149.90",
                        "is_active": True,
                        "created_at": "2026-10-27T12:00:00Z",
                        "updated_at": "2026-10-27T12:00:00Z",
                    },
                    response_only=True, 
                    status_codes=["201"],
                ),
                OpenApiExample(
                    "SKU duplicado",
                    value={
                        "sku": "product with this sku already exists.",
                    },
                    response_only=True,
                    status_codes=["400"],
                ),
                OpenApiExample(
                    "Preço negativo",
                    value={
                        "price": ["Ensure this value is greater than or equal to 0."],
                    },
                    response_only=True,
                    status_codes=["400"],
                ),
            ],
    )

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)



    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ["list", "retrieve"]:
            user = self.request.user

            is_administrator = (
                user.is_authenticated and (
                    user.is_superuser or user.groups.filter(name="Administradores").exists
                )
            )

            if not is_administrator:
                queryset = queryset.filter(is_active=True)

        return queryset




    def get_permissions(self):
        if self.action == "create":
            permission_classes = [CanCreateProduct]
        else:
            permission_classes = [ProductPermission]

        return [permission() for permission in permission_classes]


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)