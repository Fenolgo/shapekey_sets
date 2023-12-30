import bpy
from bpy.types import Region


def initialize(region: Region, force: bool = False):
    """
    Executes once immediately after the first UI draw. This is the most
    reliable way I've found to access to the Scene for initilzation when
    the addon loads. Can also be run with force=True at any time to
    reset defaults.

    :param region: The region where the addon's primary UIList is located
    :param force: When True resets all addon state to user's preferences
    """
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
