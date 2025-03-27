from .models import Profile


def user_profile(request):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        return {
            "username": profile.user.username if profile else "",
            "coins": profile.coins if profile else 0,
        }
    return {
        "coins": 0,
        "username": "",
    }
