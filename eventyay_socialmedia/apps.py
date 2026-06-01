from django.utils.translation import gettext_lazy as _

from . import __version__

try:
    from eventyay.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use a later version of eventyay-tickets")


class Social Media PluginApp(PluginConfig):
    default = True
    name = "eventyay_socialmedia"
    verbose_name = _("Social Media Plugin")

    class EventyayPluginMeta:
        name = _("Social Media Plugin")
        author = "Saalim Aqueel"
        description = _("Social media automation plugin for eventyay")
        visible = True
        version = __version__
        category = "FEATURE"

    def ready(self):
        from . import signals  # NOQA
