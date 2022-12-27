bl_info = {
    "name": "Strips Exporter",
    "author": "Igor Melo - @igordoodles",
    "version": (0, 0, 1),
    "blender": (3, 4, 1),
    "location": "Render > Export/Render Individual Strips",
    "description": "Exports individual strips from video edits made on Blender.",
    "warning": "It will freeze when exporting.",
    "doc_url": "",
    "category": "Render Animation",
}


import bpy
import os



def strips_list():
    strips = []
    video = bpy.context.scene
    
    for strip in bpy.context.sequences:
        add = True
        # in case preview range is turned on. Will make sure only videos in range will be rendered.
        if video.use_preview_range:
            # checks if its in range. Both "more than preview start" as "less than preview end"
            in_range = (video.frame_preview_start <= strip.frame_final_start)\
                        and \
                       (strip.frame_final_end <= video.frame_preview_end+1) # blender for some reason shows preview as being one less frame than strip. maybe a bug.
            # render inherits in_range condition. If one is True(that is, it is in range), so will be the other.
            add = in_range
        if add:
            strips.append(strip)
    return strips


def main(context):
    video = bpy.context.scene
    video_strips = strips_list()
    # path where file will be saved. Change to whatever works best for you.
    save_path = os.path.dirname(video.render.filepath) + '\\'
    
    for strip in video_strips:
        # to make render limit itself to the start/end of a specific strip.
        video.frame_start, video.frame_end = strip.frame_final_start, strip.frame_final_end

        file_counter = 0
        videofile_name = f'{save_path}{strip.name}.mp4'
    
        # to avoid overwriting
        while os.path.exists(videofile_name):
            file_counter += 1
            videofile_name = f'{save_path}{strip.name}({file_counter}).mp4'
            
            if not os.path.exists(videofile_name):
                pass

        video.render.filepath = videofile_name
        
        # runs but only one vid
        ## bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
        bpy.ops.render.render(animation=True, write_still=True) # adding eeee just to avoid running
        video.render.filepath = os.path.dirname(video.render.filepath) + '\\'
    
    # THIS OPENS FOLDER WHEN EDITING HAS FINISHED. DELETE IF IT DOESNT WORK (OR IF U FIND IT CREEPY)
    os.startfile(save_path)
        

class ExportStrips(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.export_strips"
    bl_label = "Export Strips"

    def execute(self, context):
        main(context)
        return {'FINISHED'}



class addon_ExportStrips(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Export Strips"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        
        layout = self.layout
        scene = context.scene

        # Create a simple row.
        layout.label(text=" Render Range:")
        
        col = layout.column()
        row = layout.row(align=True)
        
        col.prop(scene, "use_preview_range", text = "Limit Render Range")
        row.prop(scene, "frame_preview_start", text = "Start Frame:")
        row.prop(scene, "frame_preview_end", text = "End Frame:")
        
        # Create two columns, by using a split layout.
        layout.label(text="")
        # layout.label(text=" Path:")
        split = layout.split()
        col = split.column()
        
        col.prop(scene.render, "filepath")
        col.prop(scene.render, "use_overwrite")
        
        ##for the sake of spacing
        layout.label(text="")
        layout.label(text=" Note: Blender FREEZES when exporting. It'll be fixed someday.")
        
        # Big render button
        render_button = layout.row()
        render_button.scale_y = 3.0
        ## render button showing the number of render-able videos in range. Not workin still.
        render_button.operator("object.export_strips", text=f"Render all videos ({len(strips_list())})")





# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(ExportStrips)
    bpy.utils.register_class(addon_ExportStrips)

def unregister():
    bpy.utils.unregister_class(ExportStrips)
    bpy.utils.unregister_class(addon_ExportStrips)


if __name__ == "__main__":
    register()
