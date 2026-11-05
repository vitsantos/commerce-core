from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse,
    OpenApiExample,
    )

from rest_framework import filters, viewsets, serializers
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer


from .permissions import CanCreateProduct, ProductPermission


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer


    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]

    filterset_fields = ["sku", "price"]
    search_fields = ["name", "description", "sku"]


    @extend_schema(
            summary = 'Listar produtos',
            description = ("Lista os produtos com suporte a filtros, busca e paginação. "
            "Usuários públicos e operadores visualizam apenas produtos ativos. "
            "Administradores e superusuários podem visualizar todos os produtos, "
            "inclusive os inativos."),
            auth=[],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



    @extend_schema(
        summary="Consultar produto",
        description=(
            "Retorna os detalhes de um produto. Usuários públicos e operadores "
            "podem consultar apenas produtos ativos. Administradores e "
            "superusuários podem consultar também produtos inativos."
        ),
        responses={200: ProductSerializer},
        auth=[],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)



    @extend_schema(
            summary = 'Cadastrar produto',
            description = (
                "Cadastra um produto. Requer autenticação e participação no grupo "
                "'Operadores' ou 'Administradores', ou acesso de superusuário. "
                "O campo created_by é preenchido automaticamente com o usuário "
                "autenticado. O SKU deve ser único e o preço não pode ser negativo."
            ),
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
                        "created_by": 1,
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
                    user.is_superuser or user.groups.filter(name="Administradores").exists()
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



    @extend_schema(
        summary="Atualizar produto",
        description=(
            "Atualiza todos os campos editáveis do produto. "
            "A operação é permitida ao criador do produto, "
            "aos administradores e aos superusuários. "
            "Operadores não podem editar produtos de outros usuários. "
        ),
        responses={200: ProductSerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


    @extend_schema(
        summary="Atualizar parcialmente produto",
        description=(
            "Atualiza parcialmente os campos editáveis de um produto. "
            "A operação é permitida ao criador do produto, "
            "aos administradores e aos superusuários. "
            "Operadores não podem editar produtos de outros usuários. "
        )
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


    @extend_schema(
        summary="Excluir produto",
        description=(
            "Exclui permanentemente um produto. "
            "A operação é permitida aos administradores "
            "e superusuários. Operadores e usuários comuns "
            "não possuem permissão para excluir produtos."
        ),
        responses={
            204: OpenApiResponse(
                description="Produto excluído com sucesso."
            ),
            403: OpenApiResponse(
                description="Permissão negada."
            ),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)