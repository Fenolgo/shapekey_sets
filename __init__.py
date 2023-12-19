import bpy

bl_info = {
    "name": "Shapekey Sets",
    "author": "Fenolgo",
    "description": "Automatically adds a list of empty shape keys to selected meshes.",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "Properties > Data > Shapekey Sets",
    "warning": "",
    "category": "Mesh",
    "support": "COMMUNITY"
}

# -----------------------------------------------------------------------------
#   Types
# -----------------------------------------------------------------------------


class Shapekey(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()


class ShapekeySet(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    shapekeys: bpy.props.CollectionProperty(type=Shapekey)


class ShapekeySetsPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    shapekey_sets: bpy.props.CollectionProperty(type=ShapekeySet)
    active_shapekey_set_index: bpy.props.IntProperty()

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


class SHAPEKEY_SETS_OT_add(bpy.types.Operator):
    bl_label = "Apply Shapekey Set"
    bl_idname = "object.shapekey_set_add"

    def execute(self, context):
        for object in context.selected_objects:
            if object.type == 'MESH':
                for shapekey_set in context.scene.shapekey_sets:
                    for shapekey in shapekey_set.shapekeys:
                        name = shapekey.name
                        if (object.data.shape_keys is None
                                or not name in object.data.shape_keys.key_blocks):
                            object.shape_key_add(name=name)
        return {"FINISHED"}


class SHAPEKEY_SETS_OT_ui_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "shapekey_sets.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def random_color(self):
        from mathutils import Color
        from random import random
        return Color((random(), random(), random()))

    def invoke(self, context, event):
        scene = context.scene
        index = scene.active_shapekey_set_index

        try:
            item = scene.shapekey_sets[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(scene.shapekey_sets) - 1:
                scene.shapekey_sets.move(index, index+1)
                scene.active_shapekey_set_index += 1
                info = 'Item "%s" moved to position %d' % (
                    item.name, scene.active_shapekey_set_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and index >= 1:
                scene.shapekey_sets.move(index, index-1)
                scene.active_shapekey_set_index -= 1
                info = 'Item "%s" moved to position %d' % (
                    item.name, scene.active_shapekey_set_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                item = scene.shapekey_sets[scene.active_shapekey_set_index]
                scene.shapekey_sets.remove(index)
                info = 'Item %s removed from scene' % (item)
                if scene.active_shapekey_set_index == 0:
                    scene.active_shapekey_set_index = 0
                else:
                    scene.active_shapekey_set_index -= 1
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            item = scene.shapekey_sets.add()
            item.id = len(scene.shapekey_sets)
            item.name = self.random_color().r
            scene.active_shapekey_set_index = (
                len(scene.shapekey_sets)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)
        return {"FINISHED"}


# -----------------------------------------------------------------------------
#   UI Components
# -----------------------------------------------------------------------------

class SHAPEKEY_SETS_UL_matslots_example(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item
        ma = slot.material
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            if ma:
                layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
            # And now we can add other UI stuff...
            # Here, we add nodes info if this material uses (old!) shading nodes.
            # if ma and not context.scene.render.use_shading_nodes:
            #     manode = ma.active_node_material
            #     if manode:
            #         # The static method UILayout.icon returns the integer value of the icon ID "computed" for the given
            #         # RNA object.
            #         layout.label(text="Node %s" % manode.name,
            #                      translate=False, icon_value=layout.icon(manode))
            #     elif ma.use_nodes:
            #         layout.label(text="Node <none>", translate=False)
            #     else:
            #         layout.label(text="")
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SHAPEKEY_SETS_PT_ui(bpy.types.Panel):
    bl_label = __package__
    bl_udname = "ShapekeySetsUI"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
        # Initialize Scene state from user prefs on first draw
        if not context.scene.is_shapekey_sets_initialized:
            bpy.app.timers.register(initialize)

        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.template_list("UI_UL_list", "shapekey_sets_ui_list",
                          scene, "shapekey_sets", scene, "active_shapekey_set_index")

        row = layout.row()
        row.operator("object.shapekey_set_add")


# -----------------------------------------------------------------------------
#   Setup
# -----------------------------------------------------------------------------


classes = (
    SHAPEKEY_SETS_OT_ui_actions,
    SHAPEKEY_SETS_UL_matslots_example,
    Shapekey,
    ShapekeySet,
    SHAPEKEY_SETS_PT_ui,
    SHAPEKEY_SETS_OT_add,
    ShapekeySetsPreferences,
)


def initialize():
    ''' Executes once immediately after the first UI draw. This is the most
        reliable way I've found to access to the Scene for initialization.
    '''
    scene = bpy.context.scene
    prefs = bpy.context.preferences.addons[__package__].preferences

    if (scene.is_shapekey_sets_initialized == False):
        scene.shapekey_sets.clear()
        # Copy premade sets out of prefs and into the scene
        for pref_shapekey_set in prefs.shapekey_sets:
            shapekey_set = scene.shapekey_sets.add()
            for k, v in pref_shapekey_set.items():
                shapekey_set[k] = v

    scene.is_shapekey_sets_initialized = True
    bpy.app.timers.unregister(initialize)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    scene = bpy.types.Scene

    scene.shapekey_sets = bpy.props.CollectionProperty(
        type=ShapekeySet)
    scene.active_shapekey_set_index = bpy.props.IntProperty()
    scene.is_shapekey_sets_initialized = bpy.props.BoolProperty(
        default=False)

    prefs = bpy.context.preferences.addons[__package__].preferences
    prefs.register_default_sets()


def unregister():
    scene = bpy.types.Scene

    del scene.shapekey_sets
    del scene.active_shapekey_set_index
    del scene.is_shapekey_sets_initialized

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
