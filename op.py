from typing import Set
from bpy.types import Context, Operator
from .util import initialize

# -----------------------------------------------------------------------------
#   Core Operators
# -----------------------------------------------------------------------------


class SHAPEKEY_SETS_OT_reset(Operator):
    bl_idname = "object.shapekey_set_reset"
    bl_label = "Reset Default Shapekey Sets"
    bl_description = "Reset available Shapekey Sets to Default"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context) -> Set[str] | Set[int]:
        initialize(context.region, force=True)
        return {"FINISHED"}


class SHAPEKEY_SETS_OT_add(Operator):
    bl_idname = "object.shapekey_set_add"
    bl_label = "Apply Shapekey Set"
    bl_description = "Apply Shapekey Set to selected Objects"
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
