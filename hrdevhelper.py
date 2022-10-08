import ida_idaapi
import ida_hexrays
import ida_kernwin
import re
from plugin import PLUGIN_NAME
from config import load_cfg, get_cfg_filename
from show_graph import show_ctree_graph
from show_context import context_viewer

__author__ = "https://github.com/patois/"


# -----------------------------------------------------------------------
class hotkey_handler_t(ida_kernwin.action_handler_t):
    def __init__(self, func):
        ida_kernwin.action_handler_t.__init__(self)
        self.func = func

    def activate(self, ctx):
        self.func()
        return 1

    def update(self, ctx):
        return ida_kernwin.AST_ENABLE_FOR_WIDGET if ctx.widget_type == ida_kernwin.BWN_PSEUDOCODE else ida_kernwin.AST_DISABLE_FOR_WIDGET

# ----------------------------------------------------------------------------
class ui_event_handler_t(ida_kernwin.UI_Hooks):
    def __init__(self, actions):
        ida_kernwin.UI_Hooks.__init__(self)
        self.actions = actions

    def finish_populating_widget_popup(self, widget, popup_handle):
        if ida_kernwin.get_widget_type(widget) == ida_kernwin.BWN_PSEUDOCODE:
            class menu_handler_t(ida_kernwin.action_handler_t):
                def __init__(self, func):
                    ida_kernwin.action_handler_t.__init__(self)
                    self.func = func

                def activate(self, ctx):
                    func()
                    return 1

                def update(self, ctx):
                    return ida_kernwin.AST_ENABLE_FOR_WIDGET

            for actname, data, func in self.actions.items():
                desc, hotkey = data
                action_desc = ida_kernwin.action_desc_t(
                    actname,
                    desc,
                    menu_handler_t(func),
                    hotkey,
                    None,
                    -1)
                ida_kernwin.attach_dynamic_action_to_popup(widget, popup_handle, action_desc, "%s/" % PLUGIN_NAME)

# -----------------------------------------------------------------------
class HRDevHelper(ida_idaapi.plugin_t):
    comment = ""
    help = ""
    wanted_name = PLUGIN_NAME
    wanted_hotkey = ""
    flags = ida_idaapi.PLUGIN_DRAW | ida_idaapi.PLUGIN_HIDE
    act_show_ctree = "show ctree"
    act_show_sub_tree = "show sub-tree"
    act_show_context = "show context"

    @staticmethod
    def get_action_name(desc):
        return "%s:%s" % (PLUGIN_NAME, desc)

    def _register_action(self, hotkey, desc, func):
        actname = HRDevHelper.get_action_name(desc)
        print(actname)
        if ida_kernwin.register_action(ida_kernwin.action_desc_t(
            actname,
            desc,
            hotkey_handler_t(func),
            hotkey,
            None,
            -1)):
            self._registered_actions[actname] = (desc, hotkey, func)
        else:
            ida_kernwin.warning("%s: failed registering action" % PLUGIN_NAME)

    def _install(self, config):
        context_viewer = context_viewer()
        self._register_action("Ctrl-.", HRDevHelper.act_show_ctree, lambda: show_ctree_graph(config))
        self._register_action("Ctrl-Shift-.", HRDevHelper.act_show_sub_tree, lambda: show_ctree_graph(config, create_subgraph=True))
        self._register_action("V", HRDevHelper.act_show_context, lambda: context_viewer.show_context())
        self.ui_hooks = ui_event_handler_t(self._registered_actions)
        self.ui_hooks.hook()

    def _uninstall(self):
        self.ui_hooks.unhook()
        for desc in self._registered_actions:
            ida_kernwin.unregister_action(desc)

    def init(self):
        self._registered_actions = {}
        result = ida_idaapi.PLUGIN_SKIP
        if ida_hexrays.init_hexrays_plugin():
            try:
                config = load_cfg()
            except:
                ida_kernwin.warning(("%s failed parsing %s.\n"
                    "If fixing this config file manually doesn't help, please delete the file and re-run the plugin.\n\n"
                    "The plugin will now terminate." % (PLUGIN_NAME, get_cfg_filename())))
            else:
                self._install(config)
                result = ida_idaapi.PLUGIN_KEEP
        return result

    def run(self, arg):
        pass

    def term(self):
        self._uninstall()

# -----------------------------------------------------------------------
def PLUGIN_ENTRY():
    return HRDevHelper()
