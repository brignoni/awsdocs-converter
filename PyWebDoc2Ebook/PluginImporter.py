import glob
import re


def get_plugin_by_url(url):
    plugins = list(map(get_plugin, glob.glob("plugins/*Plugin.py")))

    for plugin in plugins:
        if re.search(plugin.domain, url):
            return plugin

    raise Exception('Plugin not found for this URL')


def get_plugin(name):
    plugin_name = name[8:-3]
    module = __import__(f'plugins.{plugin_name}')
    inner_module = getattr(module, plugin_name)
    return getattr(inner_module, plugin_name)()
