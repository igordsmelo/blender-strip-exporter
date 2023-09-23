

bl_info = {
    "name": "Strips Exporter",
    "author": "Igor Melo - @igordoodles",
    "version": (0, 0, 3),
    "blender": (3, 4, 1),
    "location": "Render > Export/Render Individual Strips",
    "description": "Exports individual strips from video edits made on Blender.",
    "warning": "It will freeze when exporting.",
    "doc_url": "",
    "category": "Render Animation",
}

import os

import bpy  # Blender python integration


def strips_list() -> list:
    """
        Returns a list of strips in the current Blender scene.
        Only includes strips that are within the preview range if preview range is turned on.
        Returns:
            list: A list of strips in the current Blender scene.
    """
    strips = []
    video = bpy.context.scene

    for strip in bpy.context.sequences:
        add = True
        # in case preview range is turned on. Will make sure only videos in range will be rendered.
        if video.use_preview_range:
            # checks if its in range. Both "more than preview start" as "less than preview end"
            in_range = (video.frame_preview_start <= strip.frame_final_start) and \
                       (strip.frame_final_end <= video.frame_preview_end + 1)
            # blender for some reason shows preview as being one less frame than strip. maybe a bug.
            # render inherits in_range condition. If one is True(that is, it is in range), so will be the other.
            add = in_range
        if add:
            strips.append(strip)
    return strips


def main(context: object) -> None:
    """
        Exports each strip in the current Blender scene as a separate video.

        Sets the start and end frames for rendering to match the start and end frames of each strip
        and then renders the animation. The resulting videos are saved to the same directory as the Blender file.

        Args:
            context: The current Blender context.
    """
    video = bpy.context.scene
    video_strips = strips_list()
    # path where file will be saved. Change to whatever works best for you.
    save_path = os.path.dirname(video.render.filepath) + '\\'

    for strip in video_strips:
        # makes render limit itself to the start/end of a specific strip.
        video.frame_start, video.frame_end = strip.frame_final_start, strip.frame_final_end

        file_counter = 0
        video_file_name = f'{save_path}{strip.name}.mp4'

        # avoids overwriting an existing video.
        while os.path.exists(video_file_name):
            file_counter += 1
            video_file_name = f'{save_path}{strip.name}({file_counter}).mp4'

            if not os.path.exists(video_file_name):
                pass

        video.render.filepath = video_file_name

        # runs but only one video
        ## bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
        # write_still avoids a bug. it isn't ideal but for now it works.
        # TODO: find a way to render as Blender would natively. (No bugs, animation during render, etc.)
        bpy.ops.render.render(animation=True, write_still=True)
        video.render.filepath = os.path.dirname(video.render.filepath) + '\\'

    # opens export directory once rendering has ended.
    os.startfile(save_path)


class ExportStrips(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.export_strips"
    bl_label = "Export Strips"

    def execute(self, context) -> set:
        main(context)
        return {'FINISHED'}


class Addon_ExportStrips(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Export Strips"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Creates a simple row.
        layout.label(text=" Render Range:")

        col = layout.column()
        row = layout.row(align=True)

        col.prop(scene, "use_preview_range", text="Limit Render Range")
        row.prop(scene, "frame_preview_start", text="Start Frame:")
        row.prop(scene, "frame_preview_end", text="End Frame:")

        # Creates two columns, by using a split layout.
        layout.label(text="")
        split = layout.split()
        col = split.column()

        col.prop(scene.render, "filepath")
        col.prop(scene.render, "use_overwrite")

        # for the sake of spacing
        layout.label(text="")
        layout.label(text="Note: Blender FREEZES when exporting.")

        # Big render button
        render_button = layout.row()
        render_button.scale_y = 3.0
        ## render button showing number of videos to be rendered in range.
        render_button.operator("object.export_strips", text=f"Render all videos ({len(strips_list())})")


def register():
    """
    Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
    """
    bpy.utils.register_class(ExportStrips)
    bpy.utils.register_class(Addon_ExportStrips)


def unregister():
    """Unregistering it from menus."""
    bpy.utils.unregister_class(ExportStrips)
    bpy.utils.unregister_class(Addon_ExportStrips)


if __name__ == "__main__":
    register()
