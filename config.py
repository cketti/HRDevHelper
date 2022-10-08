import ida_kernwin
import ida_diskio
import os
import configparser
from plugin import PLUGIN_NAME

CFG_FILENAME = "%s.cfg" % PLUGIN_NAME

CONFIG_DEFAULT = """; Config file for HRDevHelper (https://github.com/patois/HRDevHelper)

; options
;   center:   center current node
;   zoom:     1.0 = 100%
;   dockpos:  one of the DP_... constants from ida_kernwin
[options]
center=True
zoom=1.0
dockpos=DP_RIGHT

; RGB colors in hex
[frame_palette]
default=000000
focus=32ade1
highlight=ffae1b

; RGB colors in hex
[node_palette]
loop=663333
call=202050
cit=000000
cot=222222

; SCOLOR_... constants from ida_lines
[text_palette]
default=SCOLOR_DEFAULT
highlight=SCOLOR_EXTRA
;highlight=SCOLOR_SYMBOL
"""

# -----------------------------------------------------------------------
def get_cfg_filename():
    """returns full path for config file."""
    return os.path.join(
        ida_diskio.get_user_idadir(),
        "%s" % CFG_FILENAME)

# -----------------------------------------------------------------------
def load_cfg(reload=False):
    """loads HRDevHelper configuration."""

    config = {}
    cfg_file = get_cfg_filename()
    ida_kernwin.msg("%s: %sloading %s...\n" % (PLUGIN_NAME,
        "re" if reload else "",
        cfg_file))
    if not os.path.isfile(cfg_file):
        ida_kernwin.msg("%s: default configuration (%s) does not exist!\n" % (PLUGIN_NAME, cfg_file))
        ida_kernwin.msg("Creating default configuration\n")
        try:
            with open(cfg_file, "w") as f:
                f.write("%s" % CONFIG_DEFAULT)
        except:
            ida_kernwin.msg("failed!\n")
            return config
        return load_cfg(reload=True)

    configfile = configparser.RawConfigParser()
    configfile.readfp(open(cfg_file))

    # read all sections
    try:
        for section in configfile.sections():
            config[section] = {}

            if section in ["node_palette", "frame_palette"]:
                for name, value in configfile.items(section):
                    config[section][name] = swapcol(int(value, 0x10))
            elif section == "text_palette":
                for name, value in configfile.items(section):
                    config[section][name] = getattr(globals()["ida_lines"], value)
            elif section == "options":
                for name, value in configfile.items(section):
                    if name in ["center"]:
                        config[section][name] = configfile[section].getboolean(name)
                    elif name in ["zoom"]:
                        config[section][name] = float(value)
                    elif name in ["dockpos"]:
                        config[section][name] = getattr(globals()["ida_kernwin"], value)
        ida_kernwin.msg("done!\n")
    except:
        raise RuntimeError
    return config

# -----------------------------------------------------------------------
def swapcol(x):
    return (((x & 0x000000FF) << 16) |
                (x & 0x0000FF00) |
            ((x & 0x00FF0000) >> 16))
