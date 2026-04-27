from rest_framework import serializers
from .models import Product, ProductSpec


class ProductSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpec
        fields = [
            'id', 'product', 'name', 'price', 'stock', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductSpecDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpec
        fields = [
            'id', 'name', 'price', 'stock', 'is_active'
        ]
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    specs = ProductSpecDetailSerializer(many=True, read_only=True)
    specs_count = serializers.IntegerField(read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'image', 'description', 'is_active',
            'specs', 'specs_count', 'min_price', 'total_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'specs_count', 'min_price', 'total_stock']


class ProductCreateSerializer(serializers.ModelSerializer):
    specs = ProductSpecDetailSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'image', 'description', 'is_active', 'specs'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        specs_data = validated_data.pop('specs', [])
        product = Product.objects.create(**validated_data)
        
        for spec_data in specs_data:
            ProductSpec.objects.create(product=product, **spec_data)
        
        return product
    
    def update(self, instance, validated_data):
        specs_data = validated_data.pop('specs', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if specs_data is not None:
            existing_spec_ids = [spec.id for spec in instance.specs.all()]
            new_spec_ids = [spec.get('id') for spec in specs_data if spec.get('id')]
            
            for spec_id in existing_spec_ids:
                if spec_id not in new_spec_ids:
                    ProductSpec.objects.filter(id=spec_id).delete()
            
            for spec_data in specs_data:
                spec_id = spec_data.get('id')
                if spec_id and spec_id in existing_spec_ids:
                    spec = ProductSpec.objects.get(id=spec_id)
                    for attr, value in spec_data.items():
                        if attr != 'id':
                            setattr(spec, attr, value)
                    spec.save()
                else:
                    ProductSpec.objects.create(product=instance, **spec_data)
        
        return instance


class ProductListSerializer(serializers.ModelSerializer):
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    specs_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'image', 'description', 'is_active',
            'min_price', 'specs_count', 'created_at'
        ]