from django.test import TestCase
from .models import Producto, Venta, DetalleVenta
from decimal import Decimal

# Create your tests here.

class ProductoModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Salmón Fresco',
            unidad_medida='KG',
            precio_base=Decimal('25000.00'),
            costo_unitario_compra=Decimal('18000.00'),
            cantidad_disponible=Decimal('10.00')
        )
    
    def test_margen_ganancia(self):
        """Probar el cálculo del margen de ganancia"""
        margen = self.producto.margen_ganancia()
        self.assertAlmostEqual(margen, 38.89, places=2)


class VentaModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Trucha',
            unidad_medida='UNIDAD',
            precio_base=Decimal('15000.00'),
            costo_unitario_compra=Decimal('10000.00'),
            cantidad_disponible=Decimal('20.00')
        )
        self.venta = Venta.objects.create()
    
    def test_cancelar_venta(self):
        """Probar la cancelación de venta y reversión de stock"""
        # Crear detalle de venta
        detalle = DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=Decimal('2.00'),
            precio_unitario=self.producto.precio_base
        )
        
        # Descontar stock
        self.producto.cantidad_disponible -= detalle.cantidad
        self.producto.save()
        
        stock_antes = self.producto.cantidad_disponible
        
        # Cancelar venta
        self.venta.cancelar_venta()
        
        # Verificar que el stock fue revertido
        self.producto.refresh_from_db()
        self.assertEqual(
            self.producto.cantidad_disponible,
            stock_antes + detalle.cantidad
        )
        self.assertEqual(self.venta.estado, 'CANCELADA')
