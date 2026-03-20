from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Pedido, DetallePedido
from .forms import PedidoForm, DetallePedidoForm
from proveedores.models import Proveedor
from productos.models import Producto


# ==========================================
# CLASE BASE REUTILIZABLE PARA TESTS
# ==========================================
class PedidoTestBase(TestCase):
    """Clase base reutilizable que crea datos de prueba en setUp()"""
    
    def setUp(self):
        """Se llama ANTES de cada método test_xxx. Crea datos de prueba en SQLite3."""
        
        # Crear un usuario para login
        self.usuario = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        
        # Crear un proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nombre_contacto='Juan Pérez',
            nit='1234567890',
            telefono='3101234567',
            correo='prueba@example.com',
            ciudad='Bogotá',
            departamento='Cundinamarca'
        )
        
        # Crear un producto de prueba
        self.producto = Producto.objects.create(
            nombre='Pez Fresco',
            descripcion='Pescado fresco importado',
            precio=Decimal('15000.00'),
            tipo_producto='PE',
            tipo_presentacion='BAN'
        )
        
        # Cliente HTTP para simular peticiones
        self.client = Client()


# ==========================================
# TEST 1: Creación correcta de un Pedido
# ==========================================
class PedidoModelTest(PedidoTestBase):
    """Pruebas unitarias para el modelo Pedido."""
    
    def test_pedido_se_crea_correctamente(self):
        """
        TEST 1: Verificar que se crea un Pedido correctamente con los campos requeridos.
        Comprueba: id, proveedor, estado predeterminado y valor_total inicial.
        """
        pedido = Pedido.objects.create(
            proveedor=self.proveedor,
            estado='PEN',
            valor_total=Decimal('15000.00')
        )
        
        # Verificaciones
        self.assertEqual(pedido.proveedor.nombre_contacto, 'Juan Pérez')
        self.assertEqual(pedido.estado, 'PEN')
        self.assertEqual(pedido.valor_total, Decimal('15000.00'))
        self.assertIsNotNone(pedido.id)
        self.assertIsNotNone(pedido.fecha)
        
    def test_str_pedido(self):
        """Verifica que el método __str__ retorna el formato correcto."""
        pedido = Pedido.objects.create(
            proveedor=self.proveedor,
            valor_total=Decimal('5000.00')
        )
        
        self.assertIn('Pedido #', str(pedido))
        self.assertIn('Juan Pérez', str(pedido))


# ==========================================
# TEST 2: Cálculo correcto del subtotal
# ==========================================
class DetallePedidoModelTest(PedidoTestBase):
    """Pruebas unitarias para el modelo DetallePedido."""
    
    def test_subtotal_se_calcula_correctamente(self):
        """
        TEST 2: Verifica que el cálculo de subtotal es correcto.
        Subtotal = cantidad × precio_unitario
        Ejemplo: 5 × 8000 = 40000
        """
        pedido = Pedido.objects.create(
            proveedor=self.proveedor,
            valor_total=Decimal('0.00')
        )
        
        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=self.producto,
            cantidad=Decimal('5'),
            precio_unitario=Decimal('8000.00'),
            presentacion='unidades'
        )
        
        # Verificar el cálculo del subtotal
        subtotal_esperado = Decimal('5') * Decimal('8000.00')
        self.assertEqual(detalle.subtotal, subtotal_esperado)
        self.assertEqual(detalle.subtotal, Decimal('40000.00'))
        
    def test_str_detalle_pedido(self):
        """Verifica el formato de __str__ en DetallePedido."""
        pedido = Pedido.objects.create(
            proveedor=self.proveedor
        )
        
        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=self.producto,
            cantidad=Decimal('3'),
            precio_unitario=Decimal('8000.00')
        )
        
        self.assertIn('Pez Fresco', str(detalle))
        self.assertIn('x3', str(detalle))


# ==========================================
# TEST 3: Validación de cantidad en formulario
# ==========================================
class DetallePedidoFormTest(PedidoTestBase):
    """Pruebas unitarias para el formulario DetallePedidoForm."""
    
    def test_cantidad_debe_ser_mayor_a_cero(self):
        """
        TEST 3: Verifica que el formulario valida que cantidad > 0.
        Si cantidad es 0 o negativa, debe dar error de validación.
        """
        datos_invalidos = {
            'producto': self.producto.id,
            'cantidad': Decimal('0'),  # INVÁLIDO
            'presentacion': 'unidades',
            'precio_unitario': Decimal('8000.00')
        }
        
        form = DetallePedidoForm(data=datos_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)
        
    def test_cantidad_valida_acepta_decimales(self):
        """Verifica que el formulario acepta cantidades con decimales válidas."""
        datos_validos = {
            'producto': self.producto.id,
            'cantidad': Decimal('2.5'),  # VÁLIDO
            'presentacion': 'libras',
            'precio_unitario': Decimal('8000.00')
        }
        
        form = DetallePedidoForm(data=datos_validos)
        self.assertTrue(form.is_valid())


# ==========================================
# TEST 4: Vista lista_pedidos retorna 200
# ==========================================
class PedidoViewTest(PedidoTestBase):
    """Pruebas unitarias para las vistas."""
    
    def test_lista_pedidos_requiere_login(self):
        """
        TEST 4: Verifica que la vista lista_pedidos requiere autenticación.
        Si no está logeado, debe redirigir al login.
        """
        response = self.client.get(reverse('pedidos:lista_pedidos'))
        # Debe redirigir (302) al login
        self.assertEqual(response.status_code, 302)
        
    def test_lista_pedidos_devuelve_200_cuando_logueado(self):
        """Verifica que cuando está logeado, la vista retorna 200."""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(reverse('pedidos:lista_pedidos'))
        self.assertEqual(response.status_code, 200)
        
    def test_lista_pedidos_muestra_pedidos_creados(self):
        """Verifica que los pedidos creados aparecen en la lista."""
        self.client.login(username='testuser', password='password123')
        
        # Crear un pedido
        pedido = Pedido.objects.create(
            proveedor=self.proveedor,
            valor_total=Decimal('10000.00')
        )
        
        response = self.client.get(reverse('pedidos:lista_pedidos'))
        self.assertContains(response, self.proveedor.nombre_contacto)


# ==========================================
# TEST 5: Mapeo correcto de URLs
# ==========================================
class PedidoURLTest(PedidoTestBase):
    """Pruebas unitarias para las URLs."""
    
    def test_url_lista_pedidos_mapea_correctamente(self):
        """
        TEST 5: Verifica que la URL 'lista_pedidos' mapea a la vista correcta.
        reverse() debe resolver a /pedidos/
        """
        url = reverse('pedidos:lista_pedidos')
        self.assertEqual(url, '/pedidos/')
        
    def test_url_crear_pedido_mapea_correctamente(self):
        """Verifica que la URL 'crear_pedido' mapea correctamente."""
        url = reverse('pedidos:crear_pedido')
        self.assertEqual(url, '/pedidos/nuevo/')
        
    def test_url_editar_pedido_con_parametros(self):
        """Verifica que URLs con parámetros se resuelven correctamente."""
        url = reverse('pedidos:editar_pedido', args=[1])
        self.assertEqual(url, '/pedidos/editar/1/')
        
    def test_url_detalle_pedido_con_parametros(self):
        """Verifica otro mapeo dinámico de URL."""
        url = reverse('pedidos:detalle_pedido', args=[5])
        self.assertEqual(url, '/pedidos/detalle/5/')
