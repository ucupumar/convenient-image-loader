bl_info = {
    "name": "Convenient Image Loader",
    "author": "Yusuf Umar",
    "version": (0, 1, 1),
    "blender": (2, 80, 0),
    "location": "Image Viewer > Tool Shelf > Image",
    "description": "This addon can do prev next on images on a folder",
    "wiki_url": "https://github.com/ucupumar/image-prev-next",
    "category": "Image",
}

import bpy, os, pathlib, re
from bpy.props import *

def get_first_few_numbers(line):
    m = re.search(r'\d+', line)
    if m: return int(m.group())
    return 0

def load_next_prev_image(context, prev=False):
    area = context.area
    image = area.spaces[0].image
    if image and image.packed_file or image.filepath == '':
        return {'CANCELLED'}

    unpacked_path = bpy.path.abspath(image.filepath)
    p = pathlib.Path(unpacked_path)
    folder = p.parent
    #print(image.name, p.parent)

    cur_img_name = bpy.path.basename(image.filepath)

    img_names = []
    valid_images = [".jpg",".gif",".png",".tga", ".jpeg"]
    for f in os.listdir(folder):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        img_names.append(f)

    # Sort images
    #img_names.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    #img_names.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    #img_names.sort()
    #img_names.sort(key=lambda x: int(x.split('_')[0]))

    # Check if start of the name is numbers
    digit_names = []
    non_digit_names = []
    for name in img_names:
        if name[0].isdigit():
            digit_names.append(name)
        else: non_digit_names.append(name)

    # Sort by first few numbers
    img_names = sorted(digit_names, key = get_first_few_numbers)

    # Extend the non digit names
    img_names.extend(non_digit_names)

    new_path = ''
    for i, ip in enumerate(img_names):
        img_name = bpy.path.basename(ip)
        if img_name == cur_img_name:
            new_idx = i-1 if prev else i+1

            if new_idx >= len(img_names) or new_idx < 0:
                break
            #print(new_idx)

            try: new_path = img_names[new_idx]
            except: print('Cannot get new index!')

            break

    if new_path != '':
        new_path = os.path.join(folder, new_path)

        # Check if image already loaded
        new_image = None
        for img in bpy.data.images:
            p = bpy.path.abspath(img.filepath)
            if os.path.normpath(p) == os.path.normpath(new_path):
                new_image = img
                break

        if not new_image:
            try: new_path = bpy.path.relpath(new_path)
            except: 
                pass
                #print('Cannot make path relative')
            new_image = bpy.data.images.load(new_path)

        area.spaces[0].image = new_image

    # Remove prev shown image
    #if image.users == 1:
    #    bpy.data.images.remove(image)

class YNextImageLoader(bpy.types.Operator):
    bl_idname = "image.y_load_next_image"
    bl_label = "Load Next Image"
    bl_description = "Load next image"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'IMAGE_EDITOR'

    def execute(self, context):
        load_next_prev_image(context, prev=False)
        return {'FINISHED'}

class YPrevImageLoader(bpy.types.Operator):
    bl_idname = "image.y_load_prev_image"
    bl_label = "Load Previous Image"
    bl_description = "Load previous image"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'IMAGE_EDITOR'

    def execute(self, context):
        load_next_prev_image(context, prev=True)
        return {'FINISHED'}

def set_keybind():
    wm = bpy.context.window_manager

    left_keybind_found = False
    right_keybind_found = False
    up_keybind_found = False
    down_keybind_found = False
    semicolon_keybind_found = False
    quote_keybind_found = False

    # Object non modal keybinds
    # Get object non modal keymaps
    km = wm.keyconfigs.user.keymaps.get('Image Generic')
    if not km:
        km = wm.keyconfigs.user.keymaps.new('Image Generic')

    # Search for keybinds

    for kmi in km.keymap_items:
        
        if kmi.type == 'PAGE_DOWN':
            if kmi.idname == 'image.y_load_prev_image':
                left_keybind_found = True
                kmi.active = True
            else:
                # Deactivate other F3 keybind
                kmi.active = False
                
        if kmi.type == 'PAGE_UP':
            if kmi.idname == 'image.y_load_next_image':
                right_keybind_found = True
                kmi.active = True
            else:
                # Deactivate other F4 keybind
                kmi.active = False

        if bpy.app.version >= (2, 93, 0):

            if kmi.type == 'INSERT':
                if kmi.idname == 'image.flip':
                    up_keybind_found = True
                    kmi.active = True
                else:
                    # Deactivate other F3 keybind
                    kmi.active = False

            if kmi.type == 'DEL':
                if kmi.idname == 'image.flip':
                    down_keybind_found = True
                    kmi.active = True
                else:
                    # Deactivate other F3 keybind
                    kmi.active = False

    # Set Keybinds

    if not left_keybind_found:
        new_shortcut = km.keymap_items.new('image.y_load_prev_image', 'PAGE_DOWN', 'PRESS')
        #print(new_shortcut)
    
    if not right_keybind_found:
        new_shortcut = km.keymap_items.new('image.y_load_next_image', 'PAGE_UP', 'PRESS')
        #print(new_shortcut)

    if bpy.app.version >= (2, 93, 0):
        # Set up Keybind
        if not up_keybind_found:
            new_shortcut = km.keymap_items.new('image.flip', 'INSERT', 'PRESS')
            if bpy.app.version >= (3, 00, 0):
                new_shortcut.properties.use_flip_x = False
                new_shortcut.properties.use_flip_y = True
            else:
                new_shortcut.properties.use_flip_vertical = True
                new_shortcut.properties.use_flip_horizontal = False
            #print(new_shortcut)
        
        # Set down Keybind
        if not down_keybind_found:
            new_shortcut = km.keymap_items.new('image.flip', 'DEL', 'PRESS')
            if bpy.app.version >= (3, 00, 0):
                new_shortcut.properties.use_flip_x = True
                new_shortcut.properties.use_flip_y = False
            else:
                new_shortcut.properties.use_flip_vertical = False
                new_shortcut.properties.use_flip_horizontal = True
            #print(new_shortcut)

    #km = wm.keyconfigs.user.blender.get('3D View')
    #if not km:
    #    km = wm.keyconfigs.user.blender.new('3D View')

    #for kmi in km.keymap_items:
    #    if kmi.type == 'SEMI_COLON':
    #        if kmi.idname == 'view3d.view_camera':
    #            semicolon_keybind_found = True
    #            kmi.active = True
    #        else:
    #            # Deactivate other F4 keybind
    #            kmi.active = False

    #    if kmi.type == "QUOTE":
    #        if kmi.idname == 'view3d.view_selected':
    #            quote_keybind_found = True
    #            kmi.active = True
    #        else:
    #            # Deactivate other F4 keybind
    #            kmi.active = False

    #if not semicolon_keybind_found:
    #    new_shortcut = km.keymap_items.new('view3d.view_camera', 'SEMI_COLON', 'PRESS')

    #if not quote_keybind_found:
    #    new_shortcut = km.keymap_items.new('view3d.view_selected', "QUOTE", 'PRESS')

def remove_keybind():
    wm = bpy.context.window_manager

    km = wm.keyconfigs.user.keymaps.get('Image Generic')
    if km:
        for kmi in km.keymap_items:

            if bpy.app.version >= (2, 93, 0):
                if kmi.type in {'INSERT', 'DEL'}:
                    if (
                        (kmi.type == 'INSERT' and kmi.idname == 'image.flip') or
                        (kmi.type == 'DEL' and kmi.idname == 'image.flip')
                        ):
                        km.keymap_items.remove(kmi)
                    else: kmi.active = True
                    continue

            if kmi.type in {'PAGE_DOWN', 'PAGE_UP'}:
                if (
                    (kmi.type == 'PAGE_DOWN' and kmi.idname == 'image.y_load_prev_image') or
                    (kmi.type == 'PAGE_UP' and kmi.idname == 'image.y_load_next_image')
                    ):
                    km.keymap_items.remove(kmi)
                else: kmi.active = True

class CONVIMG_PT_image_loader(bpy.types.Panel):
    bl_label = "Image Loader"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Image"

    def draw(self, context):
        c = self.layout.column()
        r = c.row(align=True)
        r.operator('image.y_load_prev_image', icon='TRIA_LEFT', text='Prev Image')
        r.operator('image.y_load_next_image', icon='TRIA_RIGHT', text='Next Image')
        if bpy.app.version >= (2, 93, 0):
            #print('aaa')
            r = c.row(align=True)
            o = r.operator('image.flip', icon='TRIA_UP', text='Flip Vertical')
            if bpy.app.version >= (3, 00, 0):
                o.use_flip_x = False
                o.use_flip_y = True
            else:
                o.use_flip_vertical = True
                o.use_flip_horizontal = False
            o = r.operator('image.flip', icon='TRIA_DOWN', text='Flip Horizontal')
            if bpy.app.version >= (3, 00, 0):
                o.use_flip_x = True
                o.use_flip_y = False
            else:
                o.use_flip_vertical = False
                o.use_flip_horizontal = True

def register():
    bpy.utils.register_class(YNextImageLoader)
    bpy.utils.register_class(YPrevImageLoader)
    bpy.utils.register_class(CONVIMG_PT_image_loader)
    set_keybind()

def unregister():
    bpy.utils.unregister_class(YNextImageLoader)
    bpy.utils.unregister_class(YPrevImageLoader)
    bpy.utils.unregister_class(CONVIMG_PT_image_loader)
    remove_keybind()
