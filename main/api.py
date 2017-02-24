from rest_framework import serializers, viewsets

from main.models import FoodOrder, LanProfile


class PartialModelViewSet(viewsets.ModelViewSet):
    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)


class FoodSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FoodOrder
        fields = ('pk', 'time', 'order', 'price', 'paid')


class FoodViewSet(PartialModelViewSet):
    queryset = FoodOrder.objects.all().order_by('-time')
    serializer_class = FoodSerializer


class LanProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LanProfile
        fields = ('pk', 'paytype', 'paid')


class LanProfileViewSet(PartialModelViewSet):
    queryset = LanProfile.objects.all()
    serializer_class = LanProfileSerializer
