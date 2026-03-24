"""
Comando para limpiar productos con stock negativo.
Identifica ventas sin respaldo de pedidos y permite eliminarlas.
"""
from django.core.management.base import BaseCommand
from django.db.models import Sum
from productos.models import Producto
from pedidos.models import DetallePedido
from ventas.models import VentaItem


class Command(BaseCommand):
    help = 'Limpia productos con stock negativo eliminando ventas sin respaldo de pedidos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--eliminar',
            action='store_true',
            help='Elimina las ventas sin respaldo de pedidos. Sin este flag solo muestra el informe.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== ANÁLISIS DE STOCK NEGATIVO ===\n'))
        
        productos_negativos = []
        
        for producto in Producto.objects.filter(estado=True):
            stock = producto.stock
            
            if stock < 0:
                # Calcular cantidades
                recibido = DetallePedido.objects.filter(
                    producto=producto,
                    pedido__estado='REC'
                ).aggregate(total=Sum('cantidad'))['total'] or 0
                
                vendido = VentaItem.objects.filter(
                    producto=producto,
                    venta__estado='COMPLETADA'
                ).aggregate(total=Sum('cantidad'))['total'] or 0
                
                productos_negativos.append({
                    'producto': producto,
                    'stock': stock,
                    'recibido': recibido,
                    'vendido': vendido,
                    'diferencia': abs(stock),
                })
        
        if not productos_negativos:
            self.stdout.write(self.style.SUCCESS('✓ No hay productos con stock negativo'))
            return
        
        # Mostrar informe
        self.stdout.write(self.style.WARNING(f'⚠️  Encontrados {len(productos_negativos)} productos con stock negativo:\n'))
        
        for item in productos_negativos:
            self.stdout.write(
                self.style.ERROR(
                    f"  • {item['producto'].nombre}:\n"
                    f"    └─ Recibido: {item['recibido']} | Vendido: {item['vendido']} | "
                    f"Stock: {item['stock']} (Diferencia: -{item['diferencia']})\n"
                )
            )
        
        if options['eliminar']:
            self.stdout.write(self.style.WARNING('\n🗑️  Eliminando ventas sin respaldo...\n'))
            
            for item in productos_negativos:
                producto = item['producto']
                # Obtener todas las ventas COMPLETADA de este producto
                ventas_items = VentaItem.objects.filter(
                    producto=producto,
                    venta__estado='COMPLETADA'
                )
                
                cantidad_eliminada = 0
                for venta_item in ventas_items:
                    venta = venta_item.venta
                    # Eliminar el item
                    venta_item.delete()
                    cantidad_eliminada += 1
                    
                    # Recalcular totales de la venta
                    if venta.items.exists():
                        venta.recalcular_totales()
                    else:
                        # Si no hay items, eliminar la venta
                        self.stdout.write(
                            f"    Venta #{venta.id} completamente vacía, eliminada"
                        )
                        venta.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ {producto.nombre}: Eliminadas {cantidad_eliminada} ventas"
                    )
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ Limpieza completada. El stock está ahora consistente.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    '\n💡 Para ELIMINAR estas ventas, ejecuta:\n'
                    '   python manage.py limpiar_stock_negativo --eliminar\n'
                )
            )
