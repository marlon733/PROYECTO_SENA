from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Proveedor


class ListaProveedoresTestCase(TestCase):
    """Tests para la vista de lista de proveedores"""
    
    def setUp(self):
        """Preparar datos para los tests"""
        self.client = Client()
        self.lista_url = reverse('proveedores:lista_proveedores')
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123'
        )
        
        # Crear proveedores de prueba
        self.proveedor1 = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900123456',
            nombre_contacto='Empresa Pescados S.A.',
            correo='empresa1@example.com',
            telefono='3101234567',
            direccion='Calle 1 #123',
            ciudad='Bogotá',
            estado=True
        )
        
        self.proveedor2 = Proveedor.objects.create(
            tipo_persona='natural',
            nit='12345678',
            nombre_contacto='Juan Pérez',
            correo='juan@example.com',
            telefono='3107654321',
            direccion='Carrera 5 #456',
            ciudad='Cali',
            estado=True
        )
        
        self.proveedor_inactivo = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='800999888',
            nombre_contacto='Empresa Inactiva',
            correo='inactiva@example.com',
            telefono='3109876543',
            direccion='Avenida Principal',
            ciudad='Medellín',
            estado=False
        )
    
    def test_lista_proveedores_requiere_login(self):
        """Verificar que la lista requiere autenticación"""
        response = self.client.get(self.lista_url)
        self.assertEqual(response.status_code, 302)  # Redirección a login
    
    def test_lista_proveedores_carga_correctamente(self):
        """Verificar que la lista carga con usuario autenticado"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.lista_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_proveedores.html')
    
    def test_lista_solo_muestra_proveedores_activos(self):
        """Verificar que solo se muestren proveedores activos"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.lista_url)
        proveedores = response.context['proveedores']
        
        # Solo debe haber 2 proveedores activos
        self.assertEqual(proveedores.count(), 2)
        self.assertIn(self.proveedor1, proveedores)
        self.assertIn(self.proveedor2, proveedores)
        self.assertNotIn(self.proveedor_inactivo, proveedores)
    
    def test_lista_orden_por_nombre_contacto(self):
        """Verificar que los proveedores se ordenen por nombre de contacto"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.lista_url)
        proveedores = list(response.context['proveedores'])
        
        # Verificar que están ordenados por nombre_contacto
        nombres = [p.nombre_contacto for p in proveedores]
        self.assertEqual(nombres, sorted(nombres))
    
    def test_busqueda_por_nombre(self):
        """Verificar búsqueda por nombre de contacto"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.lista_url, {'q': 'Juan'})
        proveedores = response.context['proveedores']
        
        self.assertEqual(proveedores.count(), 1)
        self.assertEqual(proveedores[0].nombre_contacto, 'Juan Pérez')
    
    def test_busqueda_por_nit(self):
        """Verificar búsqueda por NIT"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.lista_url, {'q': '900123456'})
        proveedores = response.context['proveedores']
        
        self.assertEqual(proveedores.count(), 1)
        self.assertEqual(proveedores[0].nit, '900123456')
    
    def test_busqueda_sin_resultados(self):
        """Verificar búsqueda que no encuentra resultados"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.lista_url, {'q': 'NoExiste'})
        proveedores = response.context['proveedores']
        
        self.assertEqual(proveedores.count(), 0)


class AgregarProveedorTestCase(TestCase):
    """Tests para agregar nuevos proveedores"""
    
    def setUp(self):
        self.client = Client()
        self.agregar_url = reverse('proveedores:agregar_proveedores')
        self.lista_url = reverse('proveedores:lista_proveedores')
        
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123'
        )
    
    def test_agregar_proveedor_requiere_login(self):
        """Verificar que agregar requiere autenticación"""
        response = self.client.get(self.agregar_url)
        self.assertEqual(response.status_code, 302)
    
    def test_agregar_proveedor_get_carga_formulario(self):
        """Verificar que GET carga el formulario"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.agregar_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agregar_proveedores.html')
        self.assertIn('form', response.context)
    
    def test_crear_proveedor_persona_juridica(self):
        """Verificar creación de proveedor persona jurídica"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.agregar_url, {
            'tipo_persona': 'juridica',
            'nit': '900123456',
            'nombre_contacto': 'Empresa Pescados S.A.',
            'correo': 'empresa@example.com',
            'telefono': '3101234567',
            'direccion': 'Calle 1 #123',
            'departamento': 'Cundinamarca',
            'ciudad': 'Bogotá',
            'estado': True
        }, follow=True)
        
        # Verificar que fue creado
        proveedor = Proveedor.objects.filter(nit='900123456').first()
        self.assertIsNotNone(proveedor)
        self.assertEqual(proveedor.tipo_persona, 'juridica')
        self.assertEqual(proveedor.nombre_contacto, 'Empresa Pescados S.A.')
    
    def test_crear_proveedor_persona_natural(self):
        """Verificar creación de proveedor persona natural"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.agregar_url, {
            'tipo_persona': 'natural',
            'nit': '12345678',
            'nombre_contacto': 'Juan Pérez',
            'correo': 'juan@example.com',
            'telefono': '3107654321',
            'direccion': 'Carrera 5 #456',
            'ciudad': 'Cali',
            'estado': True
        }, follow=True)
        
        proveedor = Proveedor.objects.filter(nit='12345678').first()
        self.assertIsNotNone(proveedor)
        self.assertEqual(proveedor.tipo_persona, 'natural')
    
    def test_crear_proveedor_nit_duplicado(self):
        """Verificar que no se permite NIT duplicado"""
        # Crear primer proveedor
        Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900123456',
            nombre_contacto='Empresa 1',
            correo='empresa1@example.com',
            telefono='3101111111',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.agregar_url, {
            'tipo_persona': 'juridica',
            'nit': '900123456',  # NIT duplicado
            'nombre_contacto': 'Empresa 2',
            'correo': 'empresa2@example.com',
            'telefono': '3102222222',
            'direccion': 'Calle 2',
            'ciudad': 'Bogotá'
        })
        
        # Debe fallar validación
        self.assertEqual(response.status_code, 200)
        count = Proveedor.objects.filter(nit='900123456').count()
        self.assertEqual(count, 1)
    
    def test_crear_proveedor_email_duplicado(self):
        """Verificar que no se permite email duplicado"""
        Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900111111',
            nombre_contacto='Empresa 1',
            correo='test@example.com',
            telefono='3101111111',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.agregar_url, {
            'tipo_persona': 'juridica',
            'nit': '900222222',
            'nombre_contacto': 'Empresa 2',
            'correo': 'test@example.com',  # Email duplicado
            'telefono': '3102222222',
            'direccion': 'Calle 2',
            'ciudad': 'Bogotá'
        })
        
        count = Proveedor.objects.filter(correo='test@example.com').count()
        self.assertEqual(count, 1)
    
    def test_crear_proveedor_telefono_duplicado(self):
        """Verificar que no se permite teléfono duplicado"""
        Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900111111',
            nombre_contacto='Empresa 1',
            correo='empresa1@example.com',
            telefono='3101111111',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.agregar_url, {
            'tipo_persona': 'juridica',
            'nit': '900222222',
            'nombre_contacto': 'Empresa 2',
            'correo': 'empresa2@example.com',
            'telefono': '3101111111',  # Teléfono duplicado
            'direccion': 'Calle 2',
            'ciudad': 'Bogotá'
        })
        
        count = Proveedor.objects.filter(telefono='3101111111').count()
        self.assertEqual(count, 1)
    
    def test_crear_proveedor_email_invalido(self):
        """Verificar validación de email"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.agregar_url, {
            'tipo_persona': 'juridica',
            'nit': '900123456',
            'nombre_contacto': 'Empresa',
            'correo': 'email-invalido',  # Email inválido
            'telefono': '3101234567',
            'direccion': 'Calle 1',
            'ciudad': 'Bogotá'
        })
        
        count = Proveedor.objects.all().count()
        self.assertEqual(count, 0)
    
    def test_crear_proveedor_campos_requeridos(self):
        """Verificar validación de campos requeridos"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.agregar_url, {
            'tipo_persona': 'juridica',
            'nit': '900123456',
            # Faltan campos requeridos
        })
        
        count = Proveedor.objects.all().count()
        self.assertEqual(count, 0)


class DetalleProveedorTestCase(TestCase):
    """Tests para ver detalle de proveedor"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123'
        )
        
        self.proveedor = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900123456',
            nombre_contacto='Empresa Pescados',
            correo='empresa@example.com',
            telefono='3101234567',
            direccion='Calle 1 #123',
            ciudad='Bogotá'
        )
        
        self.detalle_url = reverse('proveedores:detalle_proveedores', args=[self.proveedor.id])
    
    def test_detalle_requiere_login(self):
        """Verificar que detalle requiere autenticación"""
        response = self.client.get(self.detalle_url)
        self.assertEqual(response.status_code, 302)
    
    def test_detalle_carga_correctamente(self):
        """Verificar que el detalle carga correctamente"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.detalle_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detalle_proveedores.html')
        self.assertEqual(response.context['proveedor'], self.proveedor)
    
    def test_detalle_proveedor_no_existe(self):
        """Verificar que retorna 404 para proveedor inexistente"""
        self.client.login(username='testuser', password='TestPassword123')
        url = reverse('proveedores:detalle_proveedores', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ModificarProveedorTestCase(TestCase):
    """Tests para modificar proveedores"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123'
        )
        
        self.proveedor = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900123456',
            nombre_contacto='Empresa Original',
            correo='original@example.com',
            telefono='3101234567',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        self.modificar_url = reverse('proveedores:modificar_proveedores', args=[self.proveedor.id])
    
    def test_modificar_requiere_login(self):
        """Verificar que modificar requiere autenticación"""
        response = self.client.get(self.modificar_url)
        self.assertEqual(response.status_code, 302)
    
    def test_modificar_carga_formulario(self):
        """Verificar que el formulario carga con los datos actuales"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.modificar_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'modificar_proveedores.html')
    
    def test_modificar_nombre_contacto(self):
        """Verificar modificación del nombre de contacto"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.modificar_url, {
            'tipo_persona': 'juridica',
            'nit': '900123456',
            'nombre_contacto': 'Empresa Modificada',
            'correo': 'original@example.com',
            'telefono': '3101234567',
            'direccion': 'Calle 1',
            'ciudad': 'Bogotá',
            'estado': True
        }, follow=True)
        
        self.proveedor.refresh_from_db()
        self.assertEqual(self.proveedor.nombre_contacto, 'Empresa Modificada')
    
    def test_modificar_ciudad(self):
        """Verificar modificación de ciudad"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.modificar_url, {
            'tipo_persona': 'juridica',
            'nit': '900123456',
            'nombre_contacto': 'Empresa Original',
            'correo': 'original@example.com',
            'telefono': '3101234567',
            'direccion': 'Calle 1',
            'ciudad': 'Medellín',  # Ciudad modificada
            'estado': True
        }, follow=True)
        
        self.proveedor.refresh_from_db()
        self.assertEqual(self.proveedor.ciudad, 'Medellín')
    
    def test_modificar_estado(self):
        """Verificar cambio de estado (activo/inactivo)"""
        self.client.login(username='testuser', password='TestPassword123')
        
        # Desactivar
        response = self.client.post(self.modificar_url, {
            'tipo_persona': 'juridica',
            'nit': '900123456',
            'nombre_contacto': 'Empresa Original',
            'correo': 'original@example.com',
            'telefono': '3101234567',
            'direccion': 'Calle 1',
            'ciudad': 'Bogotá',
            'estado': False
        }, follow=True)
        
        self.proveedor.refresh_from_db()
        self.assertFalse(self.proveedor.estado)
    
    def test_modificar_proveedor_no_existe(self):
        """Verificar 404 para proveedor inexistente"""
        self.client.login(username='testuser', password='TestPassword123')
        url = reverse('proveedores:modificar_proveedores', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class EliminarProveedorTestCase(TestCase):
    """Tests para eliminar proveedores"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123'
        )
        
        self.proveedor = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900123456',
            nombre_contacto='Empresa a Eliminar',
            correo='eliminar@example.com',
            telefono='3101234567',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        self.eliminar_url = reverse('proveedores:eliminar_proveedores', args=[self.proveedor.id])
        self.lista_url = reverse('proveedores:lista_proveedores')
    
    def test_eliminar_requiere_login(self):
        """Verificar que eliminar requiere autenticación"""
        response = self.client.get(self.eliminar_url)
        self.assertEqual(response.status_code, 302)
    
    def test_eliminar_get_carga_confirmacion(self):
        """Verificar que GET muestra página de confirmación"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.eliminar_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'eliminar_proveedores.html')
    
    def test_eliminar_post_elimina_proveedor(self):
        """Verificar que POST elimina el proveedor"""
        self.client.login(username='testuser', password='TestPassword123')
        
        # Verificar que existe
        self.assertTrue(Proveedor.objects.filter(id=self.proveedor.id).exists())
        
        # Eliminar
        response = self.client.post(self.eliminar_url, follow=True)
        
        # Verificar que fue elimina más de un campo
        self.assertFalse(Proveedor.objects.filter(id=self.proveedor.id).exists())
    
    def test_eliminar_redirige_a_lista(self):
        """Verificar que redirige a lista después de eliminar"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(self.eliminar_url, follow=True)
        
        # Verificar que se redirigió y la respuesta es exitosa
        self.assertEqual(response.status_code, 200)
        # Verificar que estamos en la página de lista
        self.assertTemplateUsed(response, 'lista_proveedores.html')
    
    def test_eliminar_proveedor_no_existe(self):
        """Verificar 404 para proveedor inexistente"""
        self.client.login(username='testuser', password='TestPassword123')
        url = reverse('proveedores:eliminar_proveedores', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ExportProveedoresTestCase(TestCase):
    """Tests para exportación de proveedores"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123'
        )
        
        # Crear algunos proveedores
        for i in range(3):
            Proveedor.objects.create(
                tipo_persona='juridica' if i % 2 == 0 else 'natural',
                nit=f'900{i:06d}',
                nombre_contacto=f'Proveedor {i}',
                correo=f'proveedor{i}@example.com',
                telefono=f'310{1000000 + i}',
                direccion=f'Calle {i}',
                ciudad=f'Ciudad {i}'
            )
        
        self.export_pdf_url = reverse('proveedores:export_pdf')
        self.export_excel_url = reverse('proveedores:export_excel')
    
    def test_export_pdf_requiere_login(self):
        """Verificar que exportar PDF requiere autenticación"""
        response = self.client.get(self.export_pdf_url)
        self.assertEqual(response.status_code, 302)
    
    def test_export_excel_requiere_login(self):
        """Verificar que exportar Excel requiere autenticación"""
        response = self.client.get(self.export_excel_url)
        self.assertEqual(response.status_code, 302)
    
    def test_export_pdf_genera_documento(self):
        """Verificar que exportar PDF genera el documento"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.export_pdf_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_export_excel_genera_documento(self):
        """Verificar que exportar Excel genera el documento"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.export_excel_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheet', response['Content-Type'])
    
    def test_export_pdf_incluye_todos_proveedores(self):
        """Verificar que PDF incluye los datos de proveedores"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.export_pdf_url)
        
        # Verificar que la respuesta contiene datos esperados
        self.assertIn(b'Proveedor', response.content)
    
    def test_export_pdf_tiene_headers_correctos(self):
        """Verificar headers correctos en descarga PDF"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.export_pdf_url)
        
        self.assertIn('Reporte_Proveedores', response['Content-Disposition'])


class ValidacionesProveedorTestCase(TestCase):
    """Tests para validaciones del modelo Proveedor"""
    
    def test_nit_es_unico(self):
        """Verificar que NIT debe ser único"""
        proveedor1 = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900123456',
            nombre_contacto='Empresa 1',
            correo='empresa1@example.com',
            telefono='3101111111',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        # Intentar crear otro con el mismo NIT
        with self.assertRaises(Exception):
            Proveedor.objects.create(
                tipo_persona='juridica',
                nit='900123456',
                nombre_contacto='Empresa 2',
                correo='empresa2@example.com',
                telefono='3102222222',
                direccion='Calle 2',
                ciudad='Bogotá'
            )
    
    def test_email_es_unico(self):
        """Verificar que email debe ser único"""
        proveedor1 = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900111111',
            nombre_contacto='Empresa 1',
            correo='test@example.com',
            telefono='3101111111',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        with self.assertRaises(Exception):
            Proveedor.objects.create(
                tipo_persona='juridica',
                nit='900222222',
                nombre_contacto='Empresa 2',
                correo='test@example.com',
                telefono='3102222222',
                direccion='Calle 2',
                ciudad='Bogotá'
            )
    
    def test_telefono_es_unico(self):
        """Verificar que teléfono debe ser único"""
        proveedor1 = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900111111',
            nombre_contacto='Empresa 1',
            correo='empresa1@example.com',
            telefono='3101111111',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        with self.assertRaises(Exception):
            Proveedor.objects.create(
                tipo_persona='juridica',
                nit='900222222',
                nombre_contacto='Empresa 2',
                correo='empresa2@example.com',
                telefono='3101111111',
                direccion='Calle 2',
                ciudad='Bogotá'
            )
    
    def test_str_representation(self):
        """Verificar representación en string del modelo"""
        proveedor = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900123456',
            nombre_contacto='Empresa Pescados',
            correo='empresa@example.com',
            telefono='3101234567',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        self.assertEqual(str(proveedor), 'Empresa Pescados (900123456)')
    
    def test_fecha_registro_auto(self):
        """Verificar que fecha_registro se asigna automáticamente"""
        proveedor = Proveedor.objects.create(
            tipo_persona='juridica',
            nit='900123456',
            nombre_contacto='Empresa',
            correo='empresa@example.com',
            telefono='3101234567',
            direccion='Calle 1',
            ciudad='Bogotá'
        )
        
        self.assertIsNotNone(proveedor.fecha_registro)
        # Verificar que es reciente
        diff = timezone.now() - proveedor.fecha_registro
        self.assertLess(diff.total_seconds(), 10)  # Menos de 10 segundos de diferencia
