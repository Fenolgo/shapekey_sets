from typing import Set, Type
import bpy
import functools

from bpy.types import Context, Event, Menu, PropertyGroup, AddonPreferences, Operator, UIList, Panel, Region, Scene
from bpy.props import StringProperty, BoolProperty, CollectionProperty, IntProperty, EnumProperty

bl_info = {
    "name": "Shapekey Sets",
    "author": "Fenolgo",
    "description": "Automatically adds a list of empty shape keys to selected meshes.",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "location": "Properties > Data > Shapekey Sets",
    "warning": "",
    "category": "Mesh",
    "support": "COMMUNITY"
}

# -----------------------------------------------------------------------------
#   Types
# -----------------------------------------------------------------------------


class Shapekey(PropertyGroup):
    name: StringProperty()
    enabled: BoolProperty(default=True)


class ShapekeySet(PropertyGroup):
    name: StringProperty()
    shapekeys: CollectionProperty(type=Shapekey)
    active_shapekey_index: IntProperty()


class ShapekeySetsPreferences(AddonPreferences):
    bl_idname = __package__

    shapekey_sets: CollectionProperty(type=ShapekeySet)
    active_shapekey_set_index: IntProperty()

    def register_default_sets(self):
        shapekey_set_prefs = self.shapekey_sets

        shapekey_set_prefs.clear()

        shapekey_set = shapekey_set_prefs.add()
        shapekey_set.name = "default"
        for name in default_shapekeys:
            item = shapekey_set.shapekeys.add()
            item.name = name

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our add-on")
        layout.template_list("UI_UL_list", "shapekey_sets_preferences_list",
                             self, "shapekey_sets", self, "active_shapekey_set_index")


default_shapekeys = [
    "browInnerUp",
    "browDownLeft",
    "browDownRight",
    "browOuterUpLeft",
    "browOuterUpRight",
    "eyeLookUpLeft",
    "eyeLookUpRight",
    "eyeLookDownLeft",
    "eyeLookDownRight",
    "eyeLookInLeft",
    "eyeLookInRight",
    "eyeLookOutLeft",
    "eyeLookOutRight",
    "eyeBlinkLeft",
    "eyeBlinkRight",
    "eyeSquintRight",
    "eyeSquintLeft",
    "eyeWideLeft",
    "eyeWideRight",
    "cheekPuff",
    "cheekSquintLeft",
    "cheekSquintRight",
    "noseSneerLeft",
    "noseSneerRight",
    "jawOpen",
    "jawForward",
    "jawLeft",
    "jawRight",
    "mouthFunnel",
    "mouthPucker",
    "mouthLeft",
    "mouthRight",
    "mouthRollUpper",
    "mouthRollLower",
    "mouthShrugUpper",
    "mouthShrugLower",
    "mouthClose",
    "mouthSmileLeft",
    "mouthSmileRight",
    "mouthFrownLeft",
    "mouthFrownRight",
    "mouthDimpleLeft",
    "mouthDimpleRight",
    "mouthUpperUpLeft",
    "mouthUpperUpRight",
    "mouthLowerDownLeft",
    "mouthLowerDownRight",
    "mouthPressLeft",
    "mouthPressRight",
    "mouthStretchLeft",
    "mouthStretchRight",
    "tongueOut"
]


# -----------------------------------------------------------------------------
#   Operators
# -----------------------------------------------------------------------------

class SHAPEKEY_SETS_OT_reset(Operator):
    bl_label = "Restore Default Shapekey Sets"
    bl_idname = "object.shapekey_set_reset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context) -> Set[str] | Set[int]:
        initialize(context.region, force=True)
        return {"FINISHED"}


class SHAPEKEY_SETS_OT_add(Operator):
    bl_label = "Apply Shapekey Set"
    bl_idname = "object.shapekey_set_add"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context) -> Set[str] | Set[int]:
        scene = context.scene

        if len(scene.shapekey_sets) > 0:
            active_shapekey_set = scene.shapekey_sets[scene.active_shapekey_set_index]
            for object in context.selected_objects:
                if object.type == 'MESH':
                    for shapekey in active_shapekey_set.shapekeys:
                        if shapekey.enabled:
                            name = shapekey.name
                            if (object.data.shape_keys is None
                                    or not name in object.data.shape_keys.key_blocks):
                                object.shape_key_add(name=name)
        return {"FINISHED"}


class SHAPEKEY_SETS_OT_base_list_actions(Operator):
    """
    Move items up and down, add, remove, dedupe, and clear
    """
    bl_idname = "shapekey_sets.base_list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
            ('CLEAR', "CLEAR", ""),
            ('DEDUPE', "DEDUPE", "")))

    def find_duplicates(self, items):
        """
        Find all duplicates by name
        """
        name_lookup = {}
        for c, i in enumerate(items):
            name_lookup.setdefault(i.name, []).append(c)
        duplicates = set()
        for name, indices in name_lookup.items():
            for i in indices[1:]:
                duplicates.add(i)
        return sorted(list(duplicates))

    def list_actions(self, root_obj: object, list_name: str, index_name: str):
        """
        Generic manipulations for a UI list. Subclasses are responsible for
        providing a parent object for the list through their invoke()
        implementation, along with keys for accessing the parent object's
        list and index properties.

        :param root_obj: The parent object where the list is stored
        :param list_name: The name of the list property
        :param index_name: The name of the active index property
        """
        obj = root_obj
        list = getattr(obj, list_name)
        index = getattr(obj, index_name)

        try:
            item = list[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(list)-1:
                list.move(index, index+1)
                setattr(obj, index_name, index+1)
                info = 'Item "%s" moved to position %d' % (
                    item.name, index + 1)
                return info

            elif self.action == 'UP' and index >= 1:
                list.move(index, index-1)
                setattr(obj, index_name, index-1)
                info = 'Item "%s" moved to position %d' % (
                    item.name, index + 1)
                return info

            elif self.action == 'REMOVE':
                item = list[index]
                list.remove(index)
                info = 'Item %s removed from scene' % (item)
                if index > 0:
                    setattr(obj, index_name, index-1)
                return info

        if self.action == 'ADD':
            item = list.add()
            item.id = len(list)
            item.name = "New Item"
            setattr(obj, index_name, len(list)-1)
            info = '%s added to list' % (item.name)
            return info

        elif self.action == 'CLEAR':
            if bool(list):
                list.clear()
                setattr(obj, index_name, 0)
                return "All items removed"
            else:
                return "Nothing to remove"

        elif self.action == 'DEDUPE':
            removed_items = []
            # Reverse the list before removing the items
            for i in self.find_duplicates(list)[::-1]:
                list.remove(i)
                removed_items.append(i)
            if removed_items:
                setattr(obj, index_name, len(list)-1)
                info = ', '.join(map(str, removed_items))
                return "Removed indices: %s" % (info)
            else:
                return "No duplicates"


class SHAPEKEY_SETS_OT_data_set_list_actions(SHAPEKEY_SETS_OT_base_list_actions):
    bl_idname = "shapekey_sets.set_list_action"

    def invoke(self, context: Context, event: Event) -> Set[str] | Set[int]:
        self.list_actions(context.scene, "shapekey_sets",
                          "active_shapekey_set_index")
        return {"FINISHED"}


class SHAPEKEY_SETS_OT_data_key_list_actions(SHAPEKEY_SETS_OT_base_list_actions):
    bl_idname = "shapekey_sets.key_list_action"

    @classmethod
    def poll(cls, context):
        return (len(context.scene.shapekey_sets) > 0 and
                context.scene.shapekey_sets[context.scene.active_shapekey_set_index] is not None)

    def invoke(self, context: Context, event: Event) -> Set[str] | Set[int]:
        active_set = context.scene.shapekey_sets[context.scene.active_shapekey_set_index]

        self.list_actions(active_set, "shapekeys", "active_shapekey_index")
        return {"FINISHED"}


# -----------------------------------------------------------------------------
#   UI Components
# -----------------------------------------------------------------------------

class SHAPEKEY_SETS_MT_data_set_list_context_menu(Menu):
    bl_label = "Set List Specials"

    def draw(self, context):
        layout = self.layout

        layout.operator(SHAPEKEY_SETS_OT_data_set_list_actions.bl_idname,
                        icon="X", text="Clear List").action = 'CLEAR'
        layout.operator(SHAPEKEY_SETS_OT_reset.bl_idname,
                        icon="RECOVER_LAST", text="Restore Defaults")


class SHAPEKEY_SETS_MT_data_key_list_context_menu(Menu):
    bl_label = "Key List Specials"

    def draw(self, context):
        layout = self.layout

        layout.operator(SHAPEKEY_SETS_OT_data_key_list_actions.bl_idname,
                        icon="X", text="Clear List").action = 'CLEAR'
        layout.operator(SHAPEKEY_SETS_OT_data_key_list_actions.bl_idname,
                        icon="GHOST_ENABLED", text="Delete Duplicates").action = 'DEDUPE'


class SHAPEKEY_SETS_UL_set_list_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon="GROUP")
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SHAPEKEY_SETS_UL_key_list_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.enabled = item.enabled

            row.prop(item, "name", text="", emboss=False, icon='SHAPEKEY_DATA')

            icon = 'CHECKBOX_HLT' if item.enabled else 'CHECKBOX_DEHLT'
            layout.prop(item, "enabled", text="", icon=icon, emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SHAPEKEY_SETS_PT_base_ui():
    """
    Core UI for manipulating shapekey sets. Subclasses are responsible for
    providing a parent object for addon properties through their draw()
    implementation, along with UI Element implementations that modify the
    same parent object.
    Modelled after https://github.com/blender/blender/blob/9c0bffcc89f174f160805de042b00ae7c201c40b/scripts/startup/bl_ui/properties_data_mesh.py#L290

    :param root_obj: The parent object where the list is stored
    :param set_list_actions_class: Operator class that handles set list manipulation
    :param set_context_menu_class: Menu class that draw special actions for the set list
    :param key_list_actions_class: Operator class that handles key list manipulation
    :param key_context_menu_class: Menu class that draw special actions for the key list
    """

    def _draw(self, context, root_obj, set_list_actions_class: Type, set_context_menu_class: Type, key_list_actions_class: Type, key_context_menu_class: Type):
        layout = self.layout

        # Sets List
        rows = 3
        if len(root_obj.shapekey_sets) > 0:
            rows = 5
        row = layout.row()

        row.template_list(SHAPEKEY_SETS_UL_set_list_items.__name__, "shapekey_sets_list",
                          root_obj, "shapekey_sets", root_obj, "active_shapekey_set_index", rows=rows)

        col = row.column(align=True)

        col.operator(set_list_actions_class.bl_idname,
                     icon='ADD', text="").action = 'ADD'
        col.operator(set_list_actions_class.bl_idname,
                     icon='REMOVE', text="").action = 'REMOVE'

        col.separator()

        col.menu(set_context_menu_class.__name__,
                 icon='DOWNARROW_HLT', text="")

        if len(root_obj.shapekey_sets) > 0:
            col.separator()

            col.operator(set_list_actions_class.bl_idname,
                         icon='TRIA_UP', text="").action = 'UP'

            col.operator(set_list_actions_class.bl_idname,
                         icon='TRIA_DOWN', text="").action = 'DOWN'

        # Keys List
        if len(root_obj.shapekey_sets) > 0:
            active_shapekey_set = root_obj.shapekey_sets[root_obj.active_shapekey_set_index]

            row = layout.row()

            rows = 3
            if len(active_shapekey_set.shapekeys) > 0:
                rows = 5
            row = layout.row()

            row.template_list(SHAPEKEY_SETS_UL_key_list_items.__name__, "shapekeys_list",
                              active_shapekey_set, "shapekeys", active_shapekey_set, "active_shapekey_index", rows=rows)

            col = row.column(align=True)

            col.operator(key_list_actions_class.bl_idname,
                         icon='ADD', text="").action = 'ADD'
            col.operator(key_list_actions_class.bl_idname,
                         icon='REMOVE', text="").action = 'REMOVE'

            col.separator()

            col.menu(key_context_menu_class.__name__,
                     icon='DOWNARROW_HLT', text="")

            if len(active_shapekey_set.shapekeys) > 0:
                col.separator()

                col.operator(key_list_actions_class.bl_idname,
                             icon='TRIA_UP', text="").action = 'UP'
                col.operator(key_list_actions_class.bl_idname,
                             icon='TRIA_DOWN', text="").action = 'DOWN'

                row = layout.row(align=True)
                row.operator(SHAPEKEY_SETS_OT_add.bl_idname)


class SHAPEKEY_SETS_PT_data_ui(SHAPEKEY_SETS_PT_base_ui, Panel):
    bl_label = "Shapekey Sets"
    bl_udname = "ShapekeySetsUI"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
        # Initialize Scene state from user prefs on first draw
        if not context.scene.is_shapekey_sets_initialized:
            bpy.app.timers.register(
                functools.partial(initialize, context.region))

        self._draw(context, context.scene, SHAPEKEY_SETS_OT_data_set_list_actions,
                   SHAPEKEY_SETS_MT_data_set_list_context_menu, SHAPEKEY_SETS_OT_data_key_list_actions, SHAPEKEY_SETS_MT_data_key_list_context_menu)

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
    SHAPEKEY_SETS_UL_set_list_items,
    SHAPEKEY_SETS_UL_key_list_items,
    SHAPEKEY_SETS_PT_data_ui,
)


def initialize(region: Region, force: bool = False):
    '''
    Executes once immediately after the first UI draw. This is the most
    reliable way I've found to access to the Scene for initilzation when
    the addon loads. Can also be run to reset defaults with force=True

    :param region: The region where the addon's primary UIList is located
    :param force: When True resets all addon state to user's preferences
    '''
    scene = bpy.context.scene
    prefs = bpy.context.preferences.addons[__package__].preferences

    if (scene.is_shapekey_sets_initialized == False or force == True):
        scene.shapekey_sets.clear()
        # Copy premade sets out of prefs and into the scene
        for pref_shapekey_set in prefs.shapekey_sets:
            shapekey_set = scene.shapekey_sets.add()
            for k, v in pref_shapekey_set.items():
                shapekey_set[k] = v

    scene.is_shapekey_sets_initialized = True

    # Force the UI to immediately draw the newly registered sets
    region.tag_redraw()

    # Cancels the timer
    return None


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
    prefs.register_default_sets()


def unregister():
    scene = Scene

    del scene.shapekey_sets
    del scene.active_shapekey_set_index
    del scene.is_shapekey_sets_initialized

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
