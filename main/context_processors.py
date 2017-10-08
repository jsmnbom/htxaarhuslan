from main.models import Lan, LanProfile


def lan(request):
    return {'lan': Lan.get_next(request)}


def lp(request):
    lan = Lan.get_next(request)
    if lan:
        try:
            return {'lp': LanProfile.objects.get(lan=lan, profile=request.user.profile)}
        except (LanProfile.DoesNotExist, AttributeError):
            pass
    return {'lp': None}
