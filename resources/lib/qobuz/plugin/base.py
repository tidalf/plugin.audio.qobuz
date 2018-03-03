class PluginBase(object):
    def __init__(self, plugin_id):
        self.plugin_id = plugin_id

    def get_version(self):
        raise NotImplementedError()

    def get_addon_id(self):
        raise NotImplementedError()

    def get_addon_path(self):
        raise NotImplementedError()

    def get_lib_path(self):
        raise NotImplementedError()

    def get_qobuz_path(self):
        raise NotImplementedError()

    def __str__(self):
        return '<{plugin_class} id={plugin_id} addon_id={addon_id} version={version}>'\
            .format(plugin_class=__name__,
                    plugin_id=self.plugin_id,
                    addon_id=self.get_addon_id(),
                    version=self.get_version())
