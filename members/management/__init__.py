from django.core.management.base import BaseCommand
from django.db import transaction
from members.models import Product, Order, OrderItem, Customer, Shopkeeper, DeliveryPartner

class Command(BaseCommand):
    help = 'Safely delete records with foreign key constraints'

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str, help='Model name to delete from')
        parser.add_argument('--ids', type=str, help='Comma-separated IDs to delete')
        parser.add_argument('--cascade', action='store_true', help='Delete related records')

    def handle(self, *args, **options):
        model_name = options['model']
        ids = options['ids'].split(',') if options['ids'] else []
        cascade = options['cascade']

        models_map = {
            'product': Product,
            'order': Order,
            'customer': Customer,
            'shopkeeper': Shopkeeper,
            'deliverypartner': DeliveryPartner,
        }

        if model_name.lower() not in models_map:
            self.stdout.write(
                self.style.ERROR(f"Invalid model: {model_name}. Available: {list(models_map.keys())}")
            )
            return

        model = models_map[model_name.lower()]
        
        try:
            with transaction.atomic():
                queryset = model.objects.filter(id__in=ids)
                count = queryset.count()
                
                if count == 0:
                    self.stdout.write(self.style.WARNING("No records found with given IDs"))
                    return

                if model_name.lower() == 'product' and cascade:
                    # Handle product deletion with cascade
                    for product in queryset:
                        # Delete related order items
                        OrderItem.objects.filter(product=product).delete()
                        # Delete orders that only have this product
                        Order.objects.filter(product=product).delete()
                    
                    queryset.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully deleted {count} product(s) and related orders")
                    )
                else:
                    # Check for dependencies
                    if model_name.lower() == 'product':
                        products_with_orders = []
                        for product in queryset:
                            if product.has_orders():
                                products_with_orders.append(str(product.id))
                        
                        if products_with_orders:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Cannot delete products: {','.join(products_with_orders)} - they have existing orders. "
                                    f"Use --cascade flag to delete with related records."
                                )
                            )
                            return
                    
                    queryset.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully deleted {count} {model_name}(s)")
                    )
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error deleting records: {str(e)}"))
