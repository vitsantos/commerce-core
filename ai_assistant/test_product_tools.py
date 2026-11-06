from django.test import TestCase

from catalog.models import Product
from ai_assistant.tools.product_tools import search_products

class SearchProductsTests(TestCase):
    def setUp(self):
        Product.objects.create(
            sku="TEC001",
            name="Teclado Mecânico",
            description="Teclado para jogos",
            price="150.00",
            is_active=True,
        )

        Product.objects.create(
            sku="MOU001",
            name="Mouse Gamer",
            description="Mouse com iluminação RGB",
            price="80.00",
            is_active=True,
        )

        Product.objects.create(
            sku="TEC002",
            name="Teclado Antigo",
            description="Modelo descontinuado",
            price="100.00",
            is_active=False,
        )

    def test_search_by_name(self):
        results = search_products("teclado")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["sku"], "TEC001")


    def test_search_by_description(self):
        results = search_products("iluminação")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["sku"], "MOU001")


    def test_does_not_return_nactive_product(self):
        results = search_products("teclado antigo")

        self.assertEqual(len(results), 0)