import bpy
import bmesh
import numpy as np
from scipy import ndimage
from skimage.io import imread
from skimage.transform import resize 

# Calculate the vertices and faces of a terrain and return them
def create_landscape(zdata, dsize):
    '''
    zdata - 2D array of heights (must be square)
    dsize - 3D array = (xsize, ysize, zsize)
    '''
    verts = []
    faces = []
    xsize, ysize, zsize = dsize
    xs = -(xsize/2.0)
    ys = -(ysize/2.0)
    subdiv = zdata.shape[0]
    # Walk through the rows and columns of a square plane
    # and create their vertices
    for row in range(subdiv):  # Row in x-direction 
        y = ys + ysize * row / zdata.shape[0]
        for col in range(subdiv):  # Column in y-direction
            x = xs + xsize * col / zdata.shape[1]
            if row > 0:
                if col > 0:
                    z = zdata[subdiv-row-1, col]*zsize
                    # Create a face, using indices of vertices
                    vertInd1 = (col - 1) + subdiv * row
                    vertInd2 = col + subdiv * row
                    vertInd3 = (col - 1) + subdiv * (row - 1)
                    vertInd4 = col + subdiv * (row - 1)
                    face_new = (vertInd2, vertInd1, vertInd3, vertInd4)
                    faces.append(face_new)
                # First vertex of each row
                else:
                    z = zdata[subdiv-row-1, col]*zsize
            # First edge loop
            else:
                z = zdata[subdiv-row-1, col]*zsize
            verts.append((x,y,z))
    return verts, faces
    
cdata = imread("C:\\Users\\Kyle\\Documents\\Unity Projects\\SPH_Visualization\\Assets\\Python\\Data-VisualizAR\\blender\\DTEEC_051084_1875_050939_1875_A01.ca.jpg")
data = imread("C:\\Users\\Kyle\\Documents\\Unity Projects\\SPH_Visualization\\Assets\\Python\\Data-VisualizAR\\blender\\DTEEC_051084_1875_050939_1875_A01.ca.jpg",as_gray=True)
data2 = imread("C:\\Users\\Kyle\\Documents\\Unity Projects\\SPH_Visualization\\Assets\\Python\\Data-VisualizAR\\blender\\DTEEC_051084_1875_050939_1875_A01.ab.jpg",as_gray=True)

labels, features = ndimage.label(255*data>10)
group_size = []
for i in range(features):
    group_size.append( np.sum(labels[labels==i]) )
mi = np.argmax(group_size)

mask = labels==mi
data[~mask] = 0
cdata[~mask] = (0,0,0)

dmask = mask[:, abs(mask.shape[1]-data2.shape[1]): ]
data2[~dmask] = 0

#cd = cdata[:, abs(mask.shape[1]-data2.shape[1]): ]
#alt = np.copy(data2)
alt = np.copy(data)
alt[:, abs(mask.shape[1]-data2.shape[1]): ] = data2

# down sample elevation terrain to save memory 
ds = (np.array(alt.shape)/10.).astype(int)
dds = (max(ds), max(ds))
dalt = resize(alt,dds)

verts, faces = create_landscape(dalt, (ds[1]/10.,ds[0]/10., 38.3/10.) ) 
edges = []

# Create new mesh
mesh = bpy.data.meshes.new("Landscape_Data")

# Make a mesh from a list of verts/edges/faces.
mesh.from_pydata(verts, edges, faces)

# Update mesh geometry after adding stuff.
mesh.update(calc_edges=True)

obj = bpy.data.objects.new("Landscape", mesh)  
obj.data = mesh 

# Link mesh to scene
scene = bpy.context.scene  
scene.objects.link(obj)  
obj.select = True 

def material_for_texture(fname):
    img = bpy.data.images.load(fname)

    tex = bpy.data.textures.new("imageTex", 'IMAGE')
    tex.image = img

    mat = bpy.data.materials.new("imageMat")
    mat.texture_slots.add()
    ts = mat.texture_slots[0]
    ts.texture = tex
    ts.texture_coords = 'ORCO'
    return mat

obj = bpy.data.objects['Landscape']
mat = material_for_texture("C:\\Users\\Kyle\\Documents\\Unity Projects\\SPH_Visualization\\Assets\\Python\\Data-VisualizAR\\blender\\DTEEC_051084_1875_050939_1875_A01.ca.jpg")

if len(obj.data.materials)<1:
    obj.data.materials.append(mat)
else:
    obj.data.materials[0] = mat

# exported_object = bpy.ops.export_scene.obj(filepath="C:\\Users\\Kyle\\Documents\\Unity Projects\\SPH_Visualization\\Assets\\Python\\Data-VisualizAR\\blender\\DTEEC_035690_2240_035189_2240_A01.ca.obj")

# export to gltf? ``
# add solidfy modifier? 