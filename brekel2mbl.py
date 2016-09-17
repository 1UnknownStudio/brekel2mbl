# SUMMARY: Generates Brekel Pro Face 2 compatible shape keys for
# models created in Manuel Bastioni Lab. This addon was designed
# to work in conjunction with Gregory Bond's Brekel Kinect Face Pro 2
# drivers addon:
# https://github.com/gwbond/blender/blob/master/Brekel-Kinect-Face-Pro-2-Drivers-Add-On

# COMPATIBILITY: Tested with Blender 2.77a, Brekel Pro Face 2.190,
# and Manuel Bastioni Lab 1.3.0.

# DOWNLOAD: Go to:
# https://github.com/tofarley/brekel2mbl/blob/master/brekel2mbl.py
# and right-click on the 'Raw' button and select 'Save link as...' to
# download the file to your PC/Mac/Linux machine. Save the file as
# "brekel2mbl.py"

# INSTALLATION: Install this add-on the usual way via User Preferences
# Addons "Install from File". Select the file you downloaded in the
# previous step. Once installed, this add-on is listed as "Create
# Brekel Kinect Face Pro 2 Shapekeys" in the "Animation" category.

# USAGE: Select a character mesh generated using Manuel Bastioni Lab.
# To create the shape keys and prepare the mesh for an armature exported
# from Brekel, invoke this add-on via the operator search dialog (press
# spacebar and search for "Create Brekel Shapekeys"). Any existing
# shapekeys created using the same naming convention will be destroyed.

# BUGS/ENHANCEMENTS: Feel free report bugs, suggest enhancements or,
# even better, contribute changes to the code. It's on github!

# LICENSE: GPL v2 or later

bl_info = {
    "name": "Create Brekel Kinect Face Pro 2 Shapekeys",
    "version": (1, 0),
    "location": 'Press spacebar and search for: "Create Brekel Shapekeys"',
    "category": "Animation",
}

import bpy

class CreateBrekelShapekeys(bpy.types.Operator):
    """"Create Brekel Kinect Face Pro 2 Shapekeys"""

    # Unique internal identifier
    bl_idname = "object.create_brekel_shapekeys"
    # Interface display name.
    bl_label = "Create Brekel Shapekeys"
    # Enable "undo".
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.object

        skey = [
            ['Jaw_Open', 'Expressions_mouth10_max', False],
            ['Jaw_R', 'Expressions_mouth06_min', False],
            ['Jaw_L', 'Expressions_mouth05_min', False],
            ['Frown', 'Expressions_mouth02_min', True],             #split into two
            ['Smile_R', 'Expressions_mouth06_max', False],
            ['Smile_L', 'Expressions_mouth05_max', False],
            ['Lip_Lower_Down', 'Expressions_mouth12_min', True],    #split into two
            ['Lip_Stretch', 'Expressions_mouth03_min', True],       #split into two
            ['Lips_Pucker', 'Expressions_mouth07_min', False],
            ['Cheek_Puffed', 'Expressions_mouth11_max', True],      #split into two
            ['Eye_Closed_R', 'Expressions_eye01R_max', False],
            ['Eye_Closed_L', 'Expressions_eye01L_max', False],
            ['Brow_Down', 'Expressions_brow01_min', True],          #split into two
            ['Brow_Up_R', 'Expressions_brow03R_max', False],
            ['Brow_Up_L', 'Expressions_brow03L_max', False]
         ]

        # Cleanup... Reset and remove any existing vertex groups and shape keys.
        for shape in skey:
            try:
                obj.data.shape_keys.key_blocks[shape[1]].value = obj.data.shape_keys.key_blocks[shape[1]].slider_min
            except BaseException:
                pass
            
            try:    
                obj.data.shape_keys.key_blocks[shape[0]].value = obj.data.shape_keys.key_blocks[shape[0]].slider_min
                obj.active_shape_key_index = obj.data.shape_keys.key_blocks.keys().index(shape[0])
                bpy.ops.object.shape_key_remove()
            except BaseException:
                pass
            
            try:
                obj.data.shape_keys.key_blocks[shape[0]+"_R"].value = obj.data.shape_keys.key_blocks[shape[0]+"_R"].slider_min
                obj.active_shape_key_index = obj.data.shape_keys.key_blocks.keys().index(shape[0]+"_R")
                bpy.ops.object.shape_key_remove()
            except BaseException:
                pass
            
            try: 
                obj.data.shape_keys.key_blocks[shape[0]+"_L"].value = obj.data.shape_keys.key_blocks[shape[0]+"_L"].slider_min
                obj.active_shape_key_index = obj.data.shape_keys.key_blocks.keys().index(shape[0]+"_L")
                bpy.ops.object.shape_key_remove()
            except BaseException:
                pass
            
            try:
                obj.vertex_groups.remove(obj.vertex_groups.get('Left'))
                obj.vertex_groups.remove(obj.vertex_groups.get('Right'))
            except BaseException:
                pass

        # Center gets added to both groups at weight 0.5
        left_group = obj.vertex_groups.new("Left")
        right_group = obj.vertex_groups.new("Right")


        # Let's find out how wide the head is.
        # We will decide how to apply vertex group weights based on a percentage of this.
        max_x = 0
        selVerts = [v for v in obj.data.vertices]
        indexVal = obj.vertex_groups['head'].index
        for v in selVerts: #loop over all verts
            for n in v.groups: #loop over all groups with each vert
                if n.group == indexVal: #check if the group val is the same as the index value of the required vertex group
                    if v.co.x > max_x:
                        max_x = v.co.x

        # Assign vertex group weighting.
        for vert in obj.data.vertices:
            pct = vert.co.x / max_x
            
            if pct > 0.15:
                left_group.add([vert.index], 1.0, "ADD")
                right_group.add([vert.index], 0.0, "ADD")
            elif pct > 0.00:
                left_group.add([vert.index], 0.75, "ADD")
                right_group.add([vert.index], 0.25, "ADD")
            elif pct == 0.0:
                left_group.add([vert.index], 0.50, "ADD")
                right_group.add([vert.index], 0.50, "ADD")
            elif pct < -0.15:
                left_group.add([vert.index], 0.0, "ADD")
                right_group.add([vert.index], 1.0, "ADD")
            elif pct < 0.00:
                left_group.add([vert.index], 0.25, "ADD")
                right_group.add([vert.index], 0.75, "ADD")


        for shape in skey:
            block = obj.data.shape_keys.key_blocks

            skey_value = block[shape[1]].value
            block[shape[1]].value = block[shape[1]].slider_max
            
            if shape[2]:
                obj.shape_key_add(name=shape[0]+"_R", from_mix=True)
                block[shape[0]+"_R"].vertex_group = 'Right'

                obj.shape_key_add(name=shape[0]+"_L", from_mix=True)
                block[shape[0]+"_L"].vertex_group = 'Left'
            else:
                obj.shape_key_add(name=shape[0], from_mix=True)

            obj.data.shape_keys.key_blocks[shape[1]].value = skey_value

def register():
    bpy.utils.register_class(CreateBrekelShapekeys)

def unregister():
    bpy.utils.unregister_class(CreateBrekelShapekeys)

# For manual testing.
if __name__ == "__main__":
    register()
