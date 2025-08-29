import bpy
from bpy import data as D
from bpy import context as C
import random
import math
from textwrap import wrap


def generate_annot_id():
    _id = str(random.randrange(1, 1_000_000)).zfill(7)
    return _id


def get_existing_annot_ids(strip):
    return [annot.annot_id for annot in strip.custom_annotations]


def create_annot_id(strip):
    annot_id = generate_annot_id()
    annot_ids = get_existing_annot_ids(strip)
    if annot_id in annot_ids:
        return create_annot_id(strip)
    return annot_id


def add_custom_annotation(context, text_to_add):
    strip = context.active_strip
    annot_id = create_annot_id(strip)
    annot = strip.custom_annotations.add()
    annot.text = text_to_add
    annot.annot_id = annot_id


def remove_custom_annotation(context, annot_id):
    strip = context.active_strip
    for i, annot in enumerate(strip.custom_annotations[:]):
        if annot.annot_id == annot_id:
            strip.custom_annotations.remove(i)


def format_annot_text(text):
    return wrap(text, 25)


def force_redraw(context):
    for area in context.screen.areas:
        area.tag_redraw()


def get_annot_to_edit(strip, annot_id):
    for annot in strip.custom_annotations:
        if annot.annot_id == annot_id:
            return annot


class STRIP_OT_add_custom_annotation(bpy.types.Operator):
    """Add custom annotations"""

    bl_idname = "strip.add_custom_annotation"
    bl_label = "Add Annotation"
    bl_options = {"REGISTER", "UNDO"}

    annot_text: bpy.props.StringProperty(
        name="Annotation Text", default="", options={"SKIP_SAVE"}
    )

    @classmethod
    def poll(cls, context):
        return context.active_strip is not None

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene

        add_custom_annotation(context, self.annot_text)
        force_redraw(context)
        return {"FINISHED"}


class STRIP_OT_edit_custom_annotation(bpy.types.Operator):
    """Edit custom annotations"""

    bl_idname = "strip.edit_custom_annotation"
    bl_label = "Edit Annotation"
    bl_options = {"REGISTER", "UNDO"}

    new_annot_text: bpy.props.StringProperty(name="Annotation Text")
    annot_id: bpy.props.StringProperty(name="Annotation ID")

    @classmethod
    def poll(cls, context):
        return context.active_strip is not None

    def invoke(self, context, event):
        strip = context.active_strip
        self.annot_to_edit = get_annot_to_edit(strip, self.annot_id)
        self.new_annot_text = self.annot_to_edit.text
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        self.annot_to_edit.text = self.new_annot_text
        force_redraw(context)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        prop = layout.prop(self, "new_annot_text")


class STRIP_OT_remove_custom_annotation(bpy.types.Operator):
    """Remove custom annotations"""

    bl_idname = "strip.remove_custom_annotation"
    bl_label = "Remove Annotation"
    bl_options = {"REGISTER", "UNDO"}

    annot_id: bpy.props.StringProperty(name="Annotation Id")

    @classmethod
    def poll(cls, context):
        return context.active_strip is not None

    def execute(self, context):
        remove_custom_annotation(context, self.annot_id)
        return {"FINISHED"}


class OBJECT_PT_CustomStripAnnotations(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Strip"
    bl_label = "Custom Strip Annotations"
    bl_idname = "OBJECT_PT_CustomStripAnnotations"

    @classmethod
    def poll(cls, context):
        return context.active_strip is not None

    def draw(self, context):
        layout = self.layout
        strip = context.active_strip
        layout.operator_context = "INVOKE_DEFAULT"
        op = layout.operator("strip.add_custom_annotation")
        for annot in strip.custom_annotations:

            if annot.text:
                box = layout.box()

                annot_text = wrap(annot.text, 35)
                for i, text_row in enumerate(annot_text):
                    row = box.row(align=True)
                    row.scale_y = 0.8
                    if i == 0:
                        spl = row.split()

                        lbl = spl.label(text=text_row)
                        spl = row.split()
                        spl.alignment = "RIGHT"
                        op = spl.operator(
                            "strip.edit_custom_annotation", text="", icon="GREASEPENCIL"
                        )
                        op.annot_id = annot.annot_id
                        spl = row.split()
                        spl.alignment = "RIGHT"
                        op = spl.operator(
                            "strip.remove_custom_annotation", text="", icon="X"
                        )
                        op.annot_id = annot.annot_id
                    else:

                        row.alignment = "LEFT"
                        lbl = row.label(text=text_row)


class StripAnnotationItem(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty(name="Annotation", default="Unknown")
    annot_id: bpy.props.StringProperty(
        name="AnnotId",
    )
