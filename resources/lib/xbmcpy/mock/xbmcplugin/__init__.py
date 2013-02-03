__all__ = ['xbmcplugin']
try:
    import xbmcplugin
except:
    from _plugin import plugin as xbmcplugin