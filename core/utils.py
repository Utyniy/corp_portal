from django.utils.http import url_has_allowed_host_and_scheme


def safe_next_url(request, default="index"):
    next_url = request.GET.get("next") or request.POST.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return default