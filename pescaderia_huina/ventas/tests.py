from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from ventas.models import Venta, VentaItem
from productos.models import Producto
from proveedores.models import Proveedor


class VentaModelTests(TestCase):
    """Tests para el modelo Venta"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            nit="9876543210",
            nombre_contacto="Proveedor Ventas",
            tipo_persona="juridica",
            telefono="3109876543",
            ciudad="Cali",
            estado=True
        )

        # Crear producto de prueba
        self.producto = Producto.objects.create(
            proveedor=self.proveedor,
            tipo_producto='PE',
            nombre='Robalo Fresco',
            descripcion='Robalo de excelente calidad',
            precio=Decimal('45000.00'),
            tipo_presentacion='VAC',
            estado=True
        )

    def test_crear_venta_exitosamente(self):
        """Test 1: Verificar que se crea una venta correctamente"""
        venta = Venta.objects.create(
            nombre_cliente='Juan García',
            documento_cliente='1234567890',
            producto=self.producto,
            cantidad=Decimal('2.00'),
            precio_unitario=Decimal('45000.00'),
            tipo_presentacion='EMPACADO_VACIO',
            subtotal=Decimal('90000.00'),
            estado='COMPLETADA'
        )
        
        self.assertEqual(venta.nombre_cliente, 'Juan García')
        self.assertEqual(venta.cantidad, Decimal('2.00'))
        self.assertEqual(venta.precio_unitario, Decimal('45000.00'))
        self.assertEqual(venta.estado, 'COMPLETADA')
        self.assertIsNotNone(venta.id)
        self.assertIsNotNone(venta.fecha_venta)

    def test_recalcular_totales_con_iva(self):
        """Test 2: Verificar que se calcula correctamente IVA (19%) y totales"""
        venta = Venta.objects.create(
            nombre_cliente='María López',
            documento_cliente='9876543210',
            producto=self.producto,
            cantidad=Decimal('3.00'),
            precio_unitario=Decimal('50000.00'),
            tipo_presentacion='BANDEJA',
            estado='COMPLETADA'
        )
        
        # Recalcular totales manualmente
        venta.recalcular_totales()
        
        # Verificar cálculos:
        # Subtotal: 3 * 50000 = 150000
        # IVA: 150000 * 0.19 = 28500
        # Total: 150000 + 28500 = 178500
        self.assertEqual(venta.subtotal, Decimal('150000.00'))
        self.assertEqual(venta.iva_monto, Decimal('28500.00'))
        self.assertEqual(venta.total, Decimal('178500.00'))

    def test_venta_item_subtotal_automatico(self):
        """Test 3: Verificar que VentaItem calcula subtotal automáticamente"""
        venta = Venta.objects.create(
            nombre_cliente='Carlos Pérez',
            documento_cliente='5555555555',
            estado='PENDIENTE'
        )
        
        # Crear un VentaItem
        item = VentaItem.objects.create(
            venta=venta,
            producto=self.producto,
            tipo_presentacion='POR_LIBRA',
            cantidad=Decimal('5.50'),
            precio_unitario=Decimal('12000.00')
        )
        
        # Verificar subtotal: 5.50 * 12000 = 66000
        self.assertEqual(item.subtotal, Decimal('66000.00'))
        self.assertEqual(item.cantidad, Decimal('5.50'))
        self.assertEqual(str(item), 'Robalo Fresco x 5.50')

    def test_cancelar_venta(self):
        """Test 4: Verificar que se puede cancelar una venta con motivo"""
        venta = Venta.objects.create(
            nombre_cliente='Pedro Sánchez',
            documento_cliente='1111111111',
            producto=self.producto,
            cantidad=Decimal('1.00'),
            precio_unitario=Decimal('45000.00'),
            subtotal=Decimal('45000.00'),
            estado='COMPLETADA'
        )
        
        # Cambiar estado a cancelada
        venta.estado = 'CANCELADA'
        venta.motivo_cancelacion = 'Producto defectuoso'
        venta.fecha_cancelacion = timezone.now()
        venta.save()
        
        # Verificar cambios
        venta_actualizada = Venta.objects.get(id=venta.id)
        self.assertEqual(venta_actualizada.estado, 'CANCELADA')
        self.assertEqual(venta_actualizada.motivo_cancelacion, 'Producto defectuoso')
        self.assertIsNotNone(venta_actualizada.fecha_cancelacion)

    def test_cambiar_estado_venta(self):
        """Test 5: Verificar que se puede cambiar entre diferentes estados"""
        venta = Venta.objects.create(
            nombre_cliente='Ana Martín',
            documento_cliente='2222222222',
            producto=self.producto,
            cantidad=Decimal('2.50'),
            precio_unitario=Decimal('30000.00'),
            subtotal=Decimal('75000.00'),
            estado='PENDIENTE'
        )
        
        # Verificar estado inicial
        self.assertEqual(venta.estado, 'PENDIENTE')
        
        # Cambiar a COMPLETADA
        venta.estado = 'COMPLETADA'
        venta.save()
        venta_completada = Venta.objects.get(id=venta.id)
        self.assertEqual(venta_completada.estado, 'COMPLETADA')
        
        # Cambiar a CANCELADA
        venta.estado = 'CANCELADA'
        venta.save()
        venta_cancelada = Venta.objects.get(id=venta.id)
        self.assertEqual(venta_cancelada.estado, 'CANCELADA')

    def test_venta_cliente_anonimo(self):
        """Test 6: Verificar que una venta puede ser de cliente anónimo"""
        venta = Venta.objects.create(
            nombre_cliente=None,
            documento_cliente=None,
            producto=self.producto,
            cantidad=Decimal('1.00'),
            precio_unitario=Decimal('45000.00'),
            subtotal=Decimal('45000.00'),
            estado='COMPLETADA'
        )
        
        self.assertIsNone(venta.nombre_cliente)
        self.assertEqual(venta.get_cliente_display(), 'Cliente anónimo')
        self.assertIn('Anónimo', str(venta))


class VentaItemTests(TestCase):
    """Tests para el modelo VentaItem"""

    def setUp(self):
        """Configuración para tests de VentaItem"""
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            nit="5555555555",
            nombre_contacto="Proveedor Items",
            tipo_persona="natural",
            telefono="3005555555",
            ciudad="Barranquilla",
            estado=True
        )

        # Crear productos
        self.producto1 = Producto.objects.create(
            proveedor=self.proveedor,
            tipo_producto='MA',
            nombre='Camarón Jumbo',
            descripcion='Camarón extra grande',
            precio=Decimal('65000.00'),
            tipo_presentacion='VAC',
            estado=True
        )

        self.producto2 = Producto.objects.create(
            proveedor=self.proveedor,
            tipo_producto='PO',
            nombre='Pollo Premium',
            descripcion='Pollo de corral',
            precio=Decimal('25000.00'),
            tipo_presentacion='BAN',
            estado=True
        )

        # Crear venta
        self.venta = Venta.objects.create(
            nombre_cliente='Restaurante El Sabor',
            documento_cliente='8888888888',
            estado='PENDIENTE'
        )

   