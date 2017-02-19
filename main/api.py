from rest_framework import serializers, viewsets

from main.models import FoodOrder


class FoodSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FoodOrder
        fields = ('pk', 'time', 'order', 'price', 'paid')


class FoodViewSet(viewsets.ModelViewSet):
    queryset = FoodOrder.objects.all().order_by('-time')
    serializer_class = FoodSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)
