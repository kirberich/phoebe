import importlib

from django.conf import settings

from core.decorators import classproperty


class Plugin:
    # Name and friendly-name can be overwritten per plugin for something more human-readable.
    @classproperty
    def name(cls):
        return cls.__name__
    friendly_name = name

    def run(self, plugin_instance, event_sender, event_type, zone, user, data):
        """Callback called whenever an event is triggered.

        As there can be many, it's important for plugins to bail as soon as they know they don't care about an event.
        """
        raise NotImplementedError("Please overrwrite run() in plugin '{}'.".format(self.name))


def get_plugins():
    for plugin_path in settings.PLUGINS:
        module_name, plugin_class = plugin_path.split(".")
        module = importlib.import_module('core.plugins.{}'.format(module_name))
        yield getattr(module, plugin_class)


def get_plugin(name):
    for plugin in get_plugins():
        if plugin.name == name:
            return plugin
