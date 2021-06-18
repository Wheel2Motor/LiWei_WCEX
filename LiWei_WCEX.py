bl_info = {
    "name": "LiWei_Weight Color Exchange Tool",
    "description": "Vertex weight and vertex paint exchange utilities.",
    "author": "LiWei",
    "version": (1, 0, 0),
    "blender": (2, 83, 0),
    "location": "Object Data",
    "wiki_url": "",
    "category": "Paint"
    }


import bpy


class ChannelMask:
    NONE = 0
    R = 1 << 0
    G = 1 << 1
    B = 1 << 2
    A = 1 << 3


class DataLayer:
    VERTEX_WEIGHT = "VW"
    VERTEX_COLOR = "VC"


def get_vertex_data_layer(ob, layer_type, layer_name):
    outList = {}

    if (layer_type == DataLayer.VERTEX_COLOR):
        for l in (ob.data.loops):
            i = l.vertex_index
            j = l.index
            outList[i] = ob.data.vertex_colors[layer_name].data[j].color   

    elif (layer_type == DataLayer.VERTEX_WEIGHT):
        for v in ob.data.vertices:
            try:
                weight = ob.vertex_groups[layer_name].weight(v.index)
            except:
                weight = 0
            outList[v.index] = weight

    return outList


def copy_vertex_weight_to_color(
        ob,
        weight_layer_name,
        color_layer_name,
        mask = ChannelMask.R | ChannelMask.G | ChannelMask.B,
        clean_other = False
        ):
    values = get_vertex_data_layer(ob, DataLayer.VERTEX_WEIGHT, weight_layer_name)
    for l in ob.data.loops:
        i = l.vertex_index
        val = values[i]
        org_color = ob.data.vertex_colors[color_layer_name].data[l.index].color
        r = val if (mask & ChannelMask.R) else 0 if clean_other else org_color[0]
        g = val if (mask & ChannelMask.G) else 0 if clean_other else org_color[1]
        b = val if (mask & ChannelMask.B) else 0 if clean_other else org_color[2]
        a = val if (mask & ChannelMask.A) else 0 if clean_other else org_color[3]
        ob.data.vertex_colors[color_layer_name].data[l.index].color =  (r, g, b, a)


def copy_vertex_color_to_weight(
        ob,
        color_layer_name,
        weight_layer_name,
        mask=ChannelMask.R | ChannelMask.G | ChannelMask.B
        ):
    values = get_vertex_data_layer(ob, DataLayer.VERTEX_COLOR, color_layer_name)
    for key in values:
        color = values[key]
        color_out = []
        if mask & ChannelMask.R: color_out.append(color[0])
        if mask & ChannelMask.G: color_out.append(color[1])
        if mask & ChannelMask.B: color_out.append(color[2])
        if mask & ChannelMask.A: color_out.append(color[3])
        value_out = sum(color_out) / len(color_out)
        ob.vertex_groups[weight_layer_name].add([key], value_out, 'REPLACE')



""" 
********************************************************************************************
                                 Code below are for GUI
********************************************************************************************
"""



class LIWEI_PROP_wcex(bpy.types.PropertyGroup):

 
    class Mode(object):
        ADJ = "adj"
        W2C = "w2c"
        C2W = "c2w"
        W2W = "w2w"
        C2C = "c2c"


    def callback_get_vertex_groups(self, context):
        object = context.active_object
        if object is None:
            return []
        vertex_groups = []
        vargs = object.vertex_groups.items()
        for i in range(len(vargs)):
            vertex_groups.append((vargs[i][0], vargs[i][0], "", i))
        return vertex_groups


    def callback_change_current_vertex_group_selection(self, context):
        object = bpy.context.active_object
        if object:
            vtx_grps = object.vertex_groups
            vtx_grps.active = vtx_grps[self.vertex_group]


    def callback_get_vertex_colors(self, context):
        object = context.active_object
        if object is None:
            return []
        mesh = object.data
        if (mesh is None) or (not isinstance(mesh, bpy.types.Mesh)):
            return []
        vertex_colors = []
        vargs = mesh.vertex_colors.items()
        for i in range(len(vargs)):
            vertex_colors.append((vargs[i][0], vargs[i][0], "", i))
        return vertex_colors


    def callback_change_current_vertex_color_selection(self, context):
        object = bpy.context.active_object
        if object:
            vtx_cols = object.data.vertex_colors
            vtx_cols.active = vtx_cols[self.vertex_color]


    mode : bpy.props.EnumProperty(
        items = [(Mode.ADJ, "Adjust",   "", 0),
                 (Mode.W2C, "Weight --> Color",   "", 1),
                 (Mode.C2W, "Color --> Weight",   "", 2),
                 (Mode.W2W, "Weight Shuffle",   "", 3),
                 (Mode.C2C, "Color Shuffle",    "", 4)],
        name = "Mode",
        description = "Mode."
        )


    adjust_mode : bpy.props.EnumProperty(
        items = [(DataLayer.VERTEX_WEIGHT, "Vertex Weight",   "", 0),
                 (DataLayer.VERTEX_COLOR, "Vertex Color",   "", 1)],
        name = "Adjust Mode",
        description = "Adjust Mode."
        )
    
    
    w2c_clean_other_channel : bpy.props.BoolProperty(
        name = "Clean other channel",
        description = "R channel.",
        default = True
        )


    vertex_group : bpy.props.EnumProperty(
        items = callback_get_vertex_groups,
        update = callback_change_current_vertex_group_selection,
        name = "Vertex Group",
        description = "Vertex groups of active object."
        )

 
    vertex_group_source : bpy.props.EnumProperty(
        items = callback_get_vertex_groups,
        name = "Vertex Group Source",
        description = "Vertex groups source layer."
        )


    vertex_group_target : bpy.props.EnumProperty(
        items = callback_get_vertex_groups,
        name = "Vertex Group Target",
        description = "Vertex groups target layer."
        )


    vertex_color : bpy.props.EnumProperty(
        items = callback_get_vertex_colors,
        update = callback_change_current_vertex_color_selection,
        name = "Vertex Color",
        description = "Vertex colors of active object's mesh."
        )


    vertex_color_source : bpy.props.EnumProperty(
        items = callback_get_vertex_colors,
        name = "Vertex Color Source",
        description = "Vertex colors source channel."
        )


    vertex_color_target : bpy.props.EnumProperty(
        items = callback_get_vertex_colors,
        name = "Vertex Color Target",
        description = "Vertex colors target channel."
        )


    # adjuster channel mask
    adj_channel_r : bpy.props.BoolProperty(name = "R", description = "R channel.", default = True)
    adj_channel_g : bpy.props.BoolProperty(name = "G", description = "G channel.", default = True)
    adj_channel_b : bpy.props.BoolProperty(name = "B", description = "B channel.", default = True)
    adj_channel_a : bpy.props.BoolProperty(name = "A", description = "A channel.", default = False)


    # weight to color channel mask
    w2c_channel_r : bpy.props.BoolProperty(name = "R", description = "R channel.", default = True)
    w2c_channel_g : bpy.props.BoolProperty(name = "G", description = "G channel.", default = True)
    w2c_channel_b : bpy.props.BoolProperty(name = "B", description = "B channel.", default = True)
    w2c_channel_a : bpy.props.BoolProperty(name = "A", description = "A channel.", default = False)
    w2c_clean_other_channel : bpy.props.BoolProperty(
        name = "Clean Other Channel",
        description = "Clean other channel.",
        default = True
        )


    # color to weight channel mask
    c2w_channel_r : bpy.props.BoolProperty(name = "R", description = "R channel.", default = True)
    c2w_channel_g : bpy.props.BoolProperty(name = "G", description = "G channel.", default = True)
    c2w_channel_b : bpy.props.BoolProperty(name = "B", description = "B channel.", default = True)
    c2w_channel_a : bpy.props.BoolProperty(name = "A", description = "A channel.", default = False)


    # color to color channel mask
    channel_source : bpy.props.EnumProperty(
        items = [("R", "R",   "", 0),
                 ("G", "G",   "", 1),
                 ("B", "B",   "", 2),
                 ("A", "A",   "", 3)],
        name = "Channel Source",
        description = "Channel."
        )
    channel_target : bpy.props.EnumProperty(
        items = [("R", "R",   "", 0),
                 ("G", "G",   "", 1),
                 ("B", "B",   "", 2),
                 ("A", "A",   "", 3)],
        name = "Channel Target",
        description = "Channel."
        )


class LIWEI_OT_wcex_auto_level(bpy.types.Operator):
    bl_idname = "liwei.wcex_auto_level"
    bl_label = "Auto Level"
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return bool(active_object and \
                    active_object.type == 'MESH' and \
                    active_object.vertex_groups.active and \
                    active_object.data.vertex_colors.active)
    
    def execute(self, context):
        active_object = context.active_object
        adjust_mode = context.scene.liwei_prop_wcex.adjust_mode

        if DataLayer.VERTEX_WEIGHT == adjust_mode:
            active_group_layer = context.scene.liwei_prop_wcex.vertex_group
            if active_group_layer:
                weights = get_vertex_data_layer(active_object, DataLayer.VERTEX_WEIGHT, active_group_layer)
                value_min = min(weights.values())
                value_max = max(weights.values())
                scale = value_max - value_min
                offset = value_min
                for key in weights.keys():
                    active_object.vertex_groups[active_group_layer].add([key], weights[key] / scale - offset, 'REPLACE')

        elif DataLayer.VERTEX_COLOR == adjust_mode:
            active_color_layer = context.scene.liwei_prop_wcex.vertex_color
            mask_r = ChannelMask.R if context.scene.liwei_prop_wcex.w2c_channel_r else ChannelMask.NONE
            mask_g = ChannelMask.G if context.scene.liwei_prop_wcex.w2c_channel_g else ChannelMask.NONE
            mask_b = ChannelMask.B if context.scene.liwei_prop_wcex.w2c_channel_b else ChannelMask.NONE
            mask_a = ChannelMask.A if context.scene.liwei_prop_wcex.w2c_channel_a else ChannelMask.NONE

        return {'FINISHED'}


class LIWEI_OT_wcex_copy_weight_to_color(bpy.types.Operator):
    bl_idname = "liwei.wcex_copy_weight_to_color"
    bl_label = "Copy weight to color"
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return bool(active_object and \
                    active_object.type == 'MESH' and \
                    active_object.vertex_groups.active and \
                    active_object.data.vertex_colors.active)
    
    def execute(self, context):
        active_object = context.active_object
        active_group_layer = context.scene.liwei_prop_wcex.vertex_group
        active_color_layer = context.scene.liwei_prop_wcex.vertex_color
        mask_r = ChannelMask.R if context.scene.liwei_prop_wcex.w2c_channel_r else ChannelMask.NONE
        mask_g = ChannelMask.G if context.scene.liwei_prop_wcex.w2c_channel_g else ChannelMask.NONE
        mask_b = ChannelMask.B if context.scene.liwei_prop_wcex.w2c_channel_b else ChannelMask.NONE
        mask_a = ChannelMask.A if context.scene.liwei_prop_wcex.w2c_channel_a else ChannelMask.NONE
        clean_other_channel = context.scene.liwei_prop_wcex.w2c_clean_other_channel
        if active_group_layer and active_color_layer:
            copy_vertex_weight_to_color(
                active_object,
                active_group_layer,
                active_color_layer,
                mask = mask_r | mask_g | mask_b | mask_a)
        return {'FINISHED'}



class LIWEI_OT_wcex_copy_color_to_weight(bpy.types.Operator):
    bl_idname = "liwei.wcex_copy_color_to_weight"
    bl_label = "Copy color to weight"
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return bool(active_object and \
                    active_object.type == 'MESH' and \
                    active_object.vertex_groups.active and \
                    active_object.data.vertex_colors.active)
    
    def execute(self, context):
        active_object = context.active_object
        active_group_layer = context.scene.liwei_prop_wcex.vertex_group
        active_color_layer = context.scene.liwei_prop_wcex.vertex_color
        mask_r = ChannelMask.R if context.scene.liwei_prop_wcex.c2w_channel_r else ChannelMask.NONE
        mask_g = ChannelMask.G if context.scene.liwei_prop_wcex.c2w_channel_g else ChannelMask.NONE
        mask_b = ChannelMask.B if context.scene.liwei_prop_wcex.c2w_channel_b else ChannelMask.NONE
        mask_a = ChannelMask.A if context.scene.liwei_prop_wcex.c2w_channel_a else ChannelMask.NONE
        if active_group_layer and active_color_layer:
            copy_vertex_color_to_weight(
                active_object,
                active_color_layer,
                active_group_layer,
                mask = mask_r | mask_g | mask_b | mask_a)
        return {'FINISHED'}
    


class LIWEI_PT_wcex(bpy.types.Panel):
    
    bl_label = "LiWei - Weight Color Exchange"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        active_object = context.active_object if context.selected_objects else None

        layout = self.layout
        if active_object and active_object.type == 'MESH':
            row = layout.row()
            row.label(text = "Active : ")
            row.label(text = active_object.name if object else "")
            row = layout.row()
            row.prop(bpy.context.scene.liwei_prop_wcex, "mode")
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            
            mode = bpy.context.scene.liwei_prop_wcex.mode

            # ADJ
            if (LIWEI_PROP_wcex.Mode.ADJ == mode):
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "adjust_mode")
                adjust_mode = bpy.context.scene.liwei_prop_wcex.adjust_mode
                if DataLayer.VERTEX_WEIGHT == adjust_mode:
                    row = layout.row()
                    row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_group")
                    row = layout.row()
                    row.operator("liwei.wcex_auto_level")
                elif DataLayer.VERTEX_COLOR == adjust_mode:
                    row = layout.row()
                    row.label(text="WIP")
                    """
                    row = layout.row()
                    row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_color")
                    row = layout.row()
                    row.prop(bpy.context.scene.liwei_prop_wcex, "adj_channel_r")
                    row.prop(bpy.context.scene.liwei_prop_wcex, "adj_channel_g")
                    row.prop(bpy.context.scene.liwei_prop_wcex, "adj_channel_b")
                    row.prop(bpy.context.scene.liwei_prop_wcex, "adj_channel_a") 
                    """

            # W2C
            elif (LIWEI_PROP_wcex.Mode.W2C == mode):
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_group")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_color")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "w2c_channel_r")
                row.prop(bpy.context.scene.liwei_prop_wcex, "w2c_channel_g")
                row.prop(bpy.context.scene.liwei_prop_wcex, "w2c_channel_b")
                row.prop(bpy.context.scene.liwei_prop_wcex, "w2c_channel_a")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "w2c_clean_other_channel")
                row = layout.row()
                row.operator("liwei.wcex_copy_weight_to_color")

            # C2W
            elif (LIWEI_PROP_wcex.Mode.C2W == mode):
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_color")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "c2w_channel_r")
                row.prop(bpy.context.scene.liwei_prop_wcex, "c2w_channel_g")
                row.prop(bpy.context.scene.liwei_prop_wcex, "c2w_channel_b")
                row.prop(bpy.context.scene.liwei_prop_wcex, "c2w_channel_a")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_group")
                row = layout.row()
                row.operator("liwei.wcex_copy_color_to_weight")

            # W2W
            elif (LIWEI_PROP_wcex.Mode.W2W == mode):
                row = layout.row()
                row.label(text="WIP")
                """
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_group_source")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_group_target")
                """

            # C2C
            elif (LIWEI_PROP_wcex.Mode.C2C == mode):
                row = layout.row()
                row.label(text="WIP")
                """
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_color_source")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "channel_source")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "vertex_color_target")
                row = layout.row()
                row.prop(bpy.context.scene.liwei_prop_wcex, "channel_target")
                """
                
        else:
            row = layout.row()
            row.label(text = "Activate one object please")




""" 
********************************************************************************************
                                 Initialization
********************************************************************************************
"""



def register():
    bpy.utils.register_class(LIWEI_PROP_wcex)
    bpy.utils.register_class(LIWEI_PT_wcex)
    bpy.types.Scene.liwei_prop_wcex = bpy.props.PointerProperty(type=LIWEI_PROP_wcex)
    bpy.utils.register_class(LIWEI_OT_wcex_auto_level)
    bpy.utils.register_class(LIWEI_OT_wcex_copy_weight_to_color)
    bpy.utils.register_class(LIWEI_OT_wcex_copy_color_to_weight)


def unregister():
    bpy.utils.unregister_class(LIWEI_PROP_wcex)
    bpy.utils.unregister_class(LIWEI_PT_wcex)
    del bpy.types.Scene.liwei_prop_wcex
    bpy.utils.unregister_class(LIWEI_OT_wcex_auto_level)
    bpy.utils.unregister_class(LIWEI_OT_wcex_copy_weight_to_color)
    bpy.utils.unregister_class(LIWEI_OT_wcex_copy_color_to_weight)


if __name__ == "__main__":
    register()
