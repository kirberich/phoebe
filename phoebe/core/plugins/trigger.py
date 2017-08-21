from core.plugins import Plugin


class Trigger(Plugin):
    """A simple IFTTT-style trigger plugin - you can also just use IFTTT, but this might be a bit faster.

    This is mostly just an example to show how plugins can work.
    """
    name = 'trigger'
    friendly_name = 'Trigger'

    def run(self, plugin_instance, event_sender, event_type, zone, user, data):
        print("hello world!")
