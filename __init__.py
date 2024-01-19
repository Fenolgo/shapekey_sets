import bpy

from bpy.types import PropertyGroup, AddonPreferences, Scene
from bpy.props import StringProperty, BoolProperty, CollectionProperty, IntProperty

from .default_sets import default_sets
from .op import SHAPEKEY_SETS_OT_reset, SHAPEKEY_SETS_OT_add
from .ui import (
    SHAPEKEY_SETS_OT_base_list_actions,
    SHAPEKEY_SETS_OT_data_set_list_actions,
    SHAPEKEY_SETS_OT_data_key_list_actions,
    SHAPEKEY_SETS_MT_data_set_list_context_menu,
    SHAPEKEY_SETS_MT_data_key_list_context_menu,
    SHAPEKEY_SETS_OT_prefs_set_list_actions,
    SHAPEKEY_SETS_OT_prefs_key_list_actions,
    SHAPEKEY_SETS_MT_prefs_set_list_context_menu,
    SHAPEKEY_SETS_MT_prefs_key_list_context_menu,
    SHAPEKEY_SETS_UL_set_list_items,
    SHAPEKEY_SETS_UL_key_list_items,
    SHAPEKEY_SETS_PT_base_ui,
    SHAPEKEY_SETS_PT_data_ui
)

bl_info = {
    "name": "Shapekey Sets",
    "author": "Fenolgo",
    "description": "Automatically adds a list of empty shape keys to selected meshes.",
    "blender": (2, 80, 0),
    "version": (1, 1, 2),
    "location": "Properties > Data > Shapekey Sets",
    "warning": "",
    "category": "Mesh",
    "support": "COMMUNITY"
}

# -----------------------------------------------------------------------------
#   Addon Types
# -----------------------------------------------------------------------------


class Shapekey(PropertyGroup):
    name: StringProperty()
    enabled: BoolProperty(default=True)


class ShapekeySet(PropertyGroup):
    name: StringProperty()
    shapekeys: CollectionProperty(type=Shapekey)
    active_shapekey_index: IntProperty()


class ShapekeySetsPreferences(AddonPreferences, SHAPEKEY_SETS_PT_base_ui):
    bl_idname = __package__

    shapekey_sets: CollectionProperty(type=ShapekeySet)
    active_shapekey_set_index: IntProperty()
    is_initialized: BoolProperty(default=False)

    def register_default_sets(self):
        shapekey_set_prefs = self.shapekey_sets

        shapekey_set_prefs.clear()

        for set_name, shapekeys in default_sets.items():
            shapekey_set = shapekey_set_prefs.add()
            shapekey_set.name = set_name
            for name in shapekeys:
                item = shapekey_set.shapekeys.add()
                item.name = name

    def draw(self, context):
        layout = self.layout
        layout.label(
            text="Here you can set the default Shapekey Sets that load into new projects.")
        self._draw(context, self, SHAPEKEY_SETS_OT_prefs_set_list_actions, SHAPEKEY_SETS_MT_prefs_set_list_context_menu,
                   SHAPEKEY_SETS_OT_prefs_key_list_actions, SHAPEKEY_SETS_MT_prefs_key_list_context_menu)


# -----------------------------------------------------------------------------
#   Setup
# -----------------------------------------------------------------------------


classes = (
    Shapekey,
    ShapekeySet,
    ShapekeySetsPreferences,
    SHAPEKEY_SETS_OT_reset,
    SHAPEKEY_SETS_OT_add,
    SHAPEKEY_SETS_OT_base_list_actions,
    SHAPEKEY_SETS_OT_data_set_list_actions,
    SHAPEKEY_SETS_OT_data_key_list_actions,
    SHAPEKEY_SETS_MT_data_set_list_context_menu,
    SHAPEKEY_SETS_MT_data_key_list_context_menu,
    SHAPEKEY_SETS_OT_prefs_set_list_actions,
    SHAPEKEY_SETS_OT_prefs_key_list_actions,
    SHAPEKEY_SETS_MT_prefs_set_list_context_menu,
    SHAPEKEY_SETS_MT_prefs_key_list_context_menu,
    SHAPEKEY_SETS_UL_set_list_items,
    SHAPEKEY_SETS_UL_key_list_items,
    SHAPEKEY_SETS_PT_data_ui,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    scene = Scene

    scene.shapekey_sets = CollectionProperty(
        type=ShapekeySet)
    scene.active_shapekey_set_index = IntProperty()
    scene.is_shapekey_sets_initialized = BoolProperty(
        default=False)

    prefs = bpy.context.preferences.addons[__package__].preferences
    if not prefs.is_initialized:
        prefs.register_default_sets()
        prefs.is_initialized = True


def unregister():
    scene = Scene

    del scene.shapekey_sets
    del scene.active_shapekey_set_index
    del scene.is_shapekey_sets_initialized

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
