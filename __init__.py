bl_info = {
    "name": "Add Custom Movie Strip Annotations",
    "author": "Jake Mobley",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Video Sequencer",
    "description": "Adds custom text annotations to active strip",
    "warning": "",
    "doc_url": "",
    "category": "Tools",
}

import bpy
from custom_strip_annotations.add_custom_strip_annotations import *


classes = [
    OBJECT_PT_CustomStripAnnotations,
    STRIP_OT_add_custom_annotation,
    StripAnnotationItem,
    STRIP_OT_remove_custom_annotation,
    STRIP_OT_edit_custom_annotation,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Strip.custom_annotations = bpy.props.CollectionProperty(
        type=StripAnnotationItem
    )


def unregister():
    del bpy.types.Strip.custom_annotations
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
