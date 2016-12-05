import os
import runpy as rp
import sys


# Get absolute path of current executable
if getattr(sys, 'frozen', False):
    # frozen
    basepath = os.path.dirname(sys.executable)
else:
    # unfrozen
    basepath = os.path.dirname(os.path.realpath(__file__))


def getGlobalPluginDirectory():
    return os.path.join(basepath, 'plugins')


def getPluginPath(pluginName):
    if pluginName[-3:] == '.py':
        pluginPath = pluginName
    else:
        pluginPath = os.path.join(
            basepath, 'plugins', '%s.py' % pluginName)

    return pluginPath


def empty():
    pass


def loadPluginsFromConfig(config):
    """ Load plugin from config file """
    pluginList = [name for name in config.keys() if name != 'main']
    pluginFuncDict = {}

    initialDirectory = os.getcwd()
    initialPath = sys.path[:]

    for pluginName in pluginList:
        pluginSettings = {'settings': config[pluginName]}

        print('Loading plugin %s...' % pluginName)

        # real python name
        pluginPath = getPluginPath(pluginName)

        try:
            pluginDir, _ = os.path.split(pluginPath)
            if pluginDir and pluginDir not in sys.path:
                sys.path.append(os.path.abspath(pluginDir))

            pluginDict = rp.run_path(pluginPath, pluginSettings, pluginName)

            if pluginDict:
                onPluginStart = pluginDict.get('onPluginStart', empty)
                beforeTriggerExec = pluginDict.get('beforeTriggerExec', empty)
                afterTriggerExec = pluginDict.get('afterTriggerExec', empty)
                pluginFuncDict[pluginName] = (
                    onPluginStart,
                    beforeTriggerExec,
                    afterTriggerExec
                )

        except (KeyboardInterrupt, SystemExit):
            raise

        except Exception:
            raise RuntimeError('Error loading plugin "%s"' % pluginName)

        finally:
            os.chdir(initialDirectory)
            sys.path[:] = initialPath[:]

    return pluginList, pluginFuncDict
