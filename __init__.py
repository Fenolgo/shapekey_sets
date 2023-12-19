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


class SHAPEKEY_SETS_PT_ui(bpy.types.Panel):
    bl_label = __package__
    bl_udname = "ShapekeySetsUI"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.shapekey_set_add")


class SHAPEKEY_SETS_OT_add(bpy.types.Operator):
    bl_label = "Apply Shapekey Set"
    bl_idname = "object.shapekey_set_add"

    arkit_face_blendshapes = [
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

    def execute(self, context):
        for object in context.selected_objects:
            if object.type == 'MESH':
                for key_name in self.arkit_face_blendshapes:
                    if (object.data.shape_keys is None
                            or not key_name in object.data.shape_keys.key_blocks):
                        object.shape_key_add(name=key_name)
        return {"FINISHED"}


classes = (
    SHAPEKEY_SETS_PT_ui,
    SHAPEKEY_SETS_OT_add,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
