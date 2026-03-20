from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from productos.models import Producto
from proveedores.models import Proveedor
import sys
class ProductoModelTests(TestCase):
    """Tests para el modelo Producto"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear un proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nit="1234567890",
            nombre_contacto="Proveedor Test",
            tipo_persona="natural",
            telefono="3001234567",
            ciudad="Bogotá",
            estado=True
        )

    def test_crear_producto_exitosamente(self):
        """Test 1: Verificar que se puede crear un producto correctamente"""
        producto = Producto.objects.create(
            proveedor=self.proveedor,
            tipo_producto='PE',
            nombre='Robalo Fresco',
            descripcion='Robalo de primera calidad',
            precio=45000.00,
            tipo_presentacion='VAC',
            estado=True
        )
        
        self.assertEqual(producto.nombre, 'Robalo Fresco')
        self.assertEqual(producto.tipo_producto, 'PE')
        self.assertEqual(producto.precio, 45000.00)
        self.assertTrue(producto.estado)
        self.assertIsNotNone(producto.id)

    def test_producto_sin_proveedor(self):
        """Test 2: Verificar que un producto puede existir sin proveedor asignado"""
        producto = Producto.objects.create(
            proveedor=None,
            tipo_producto='MA',
            nombre='Camarón Importado',
            descripcion='Camarón de origen ecuatoriano',
            precio=55000.00,
            tipo_presentacion='BAN',
            estado=True
        )
        
        self.assertIsNone(producto.proveedor)
        self.assertEqual(str(producto), 'Camarón Importado (Sin Proveedor)')

    def test_tipos_presentacion_validos(self):
        """Test 3: Verificar que se respetan los tipos de presentación"""
        tipos = ['VAC', 'BAN', 'LIB']
        
        for tipo in tipos:
            producto = Producto.objects.create(
                proveedor=self.proveedor,
                tipo_producto='PE',
                nombre=f'Producto {tipo}',
                descripcion='Descripción test',
                precio=30000.00,
                tipo_presentacion=tipo,
                estado=True
            )
            self.assertEqual(producto.tipo_presentacion, tipo)

    def test_estado_producto(self):
        """Test 4: Verificar que se puede cambiar el estado del producto"""
        producto = Producto.objects.create(
            proveedor=self.proveedor,
            tipo_producto='PO',
            nombre='Pollo Entero',
            descripcion='Pollo fresco de granja',
            precio=25000.00,
            tipo_presentacion='BAN',
            estado=True
        )
        
        # Verificar que está activo
        self.assertTrue(producto.estado)
        
        # Desactivar producto
        producto.estado = False
        producto.save()
        
        # Verificar que está inactivo
        producto_actualizado = Producto.objects.get(id=producto.id)
        self.assertFalse(producto_actualizado.estado)

    def test_str_producto_con_proveedor(self):
        """Test 5: Verificar la representación en string del producto"""
        producto = Producto.objects.create(
            proveedor=self.proveedor,
            tipo_producto='PE',
            nombre='Atún Rojo',
            descripcion='Atún de calidad premium',
            precio=65000.00,
            tipo_presentacion='VAC',
            estado=True
        )
        
        expected_str = f"Atún Rojo ({self.proveedor.nombre_contacto})"
        self.assertEqual(str(producto), expected_str)

    def test_precio_producto_valido(self):
        """Test 6: Verificar que el precio se almacena correctamente con decimales"""
        producto = Producto.objects.create(
            proveedor=self.proveedor,
            tipo_producto='MA',
            nombre='Camarón Jumbo',
            descripcion='Camarón extra grande',
            precio=125750.50,
            tipo_presentacion='VAC',
            estado=True
        )
        
        # Verificar que el precio mantiene los decimales
        self.assertEqual(producto.precio, 125750.50)
        # Verificar que es del tipo correcto
        self.assertIsInstance(float(producto.precio), float)


