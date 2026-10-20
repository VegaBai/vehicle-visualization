"""One-time native asset creation; all runtime shading is an editable node graph."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()==D+'/Maps/Studio_YU7_TunnelFlow.Studio_YU7_TunnelFlow'
assert not E.does_directory_exist(D+'/Meshes')
opt=unreal.FbxImportUI();opt.set_editor_properties({'automated_import_should_detect_type':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_STATIC_MESH,'import_as_skeletal':False,'import_mesh':True,'import_materials':False,'import_textures':False})
opt.static_mesh_import_data.set_editor_properties({'combine_meshes':False,'auto_generate_collision':False,'generate_lightmap_u_vs':False,'convert_scene':True,'convert_scene_unit':True,'force_front_x_axis':False,'import_uniform_scale':1.,'transform_vertex_to_absolute':True,'build_nanite':False,'normal_import_method':unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS})
task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(R/'art/YU7_TUNNEL_FLOW/prepared/YU7_TunnelEffects_v01.fbx'),'destination_path':D+'/Meshes','automated':True,'replace_existing':False,'save':True,'factory':unreal.FbxFactory(),'options':opt})
flag=unreal.SystemLibrary.get_console_variable_bool_value('Interchange.FeatureFlags.Import.FBX');unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
try:T.import_asset_tasks([task])
finally:unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX '+('1' if flag else '0'))
meshes=[unreal.load_asset(p) for p in task.imported_object_paths];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)];assert len(meshes)==5
SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for mesh in meshes:
    s=SM.get_lod_build_settings(mesh,0);s.set_editor_properties({'recompute_normals':False,'recompute_tangents':False,'use_full_precision_u_vs':True,'use_high_precision_tangent_basis':True,'generate_lightmap_u_vs':False});SM.set_lod_build_settings(mesh,0,s)
    E.set_metadata_tag(mesh,'Attribution',(R/'CREDITS.txt').read_text().strip());E.save_loaded_asset(mesh)
assert not E.does_asset_exist(D+'/Materials/MPC_TunnelFlow')
mpc=T.create_asset('MPC_TunnelFlow',D+'/Materials',unreal.MaterialParameterCollection,unreal.MaterialParameterCollectionFactoryNew())
p=unreal.CollectionScalarParameter();p.set_editor_properties({'parameter_name':'ShotTime','default_value':0.})
mpc.set_editor_property('scalar_parameters',[p]);E.save_loaded_asset(mpc)

class Graph:
    def __init__(self,name,additive=False):
        assert not E.does_asset_exist(D+'/Materials/'+name)
        self.m=T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());self.n=0
        if additive:self.m.set_editor_properties({'shading_model':unreal.MaterialShadingModel.MSM_UNLIT,'blend_mode':unreal.BlendMode.BLEND_ADDITIVE,'two_sided':True,'disable_depth_test':False})
    def node(self,kind,**properties):
        n=M.create_material_expression(self.m,getattr(unreal,'MaterialExpression'+kind),-1600+(self.n%8)*190,(self.n//8)*190);self.n+=1
        if properties:n.set_editor_properties(properties)
        return n
    def val(self,x):
        if isinstance(x,(float,int)):return self.node('Constant',r=float(x))
        if isinstance(x,tuple):return self.node('Constant3Vector',constant=unreal.LinearColor(*x,1.))
        return x
    def link(self,x,n,p):assert M.connect_material_expressions(self.val(x),'',n,p),(n.get_name(),p)
    def op(self,k,a,b=None):
        n=self.node(k);self.link(a,n,'A' if b is not None else '')
        if b is not None:self.link(b,n,'B')
        return n
    def add(self,a,b):return self.op('Add',a,b)
    def sub(self,a,b):return self.op('Subtract',a,b)
    def mul(self,a,b):return self.op('Multiply',a,b)
    def div(self,a,b):return self.op('Divide',a,b)
    def sat(self,a):return self.op('Saturate',a)
    def inv(self,a):return self.op('OneMinus',a)
    def smooth(self,lo,hi,x):
        n=self.node('SmoothStep');self.link(lo,n,'Min');self.link(hi,n,'Max');self.link(x,n,'Value');return n
    def pow(self,x,p):
        n=self.node('Power');self.link(x,n,'Base');self.link(p,n,'Exp');return n
    def bell(self,d,width):
        z=self.div(d,width);return self.op('Exponential2',self.mul(self.mul(z,z),-2.5))
    def out(self,x,prop):assert M.connect_material_property(self.val(x),'',getattr(unreal.MaterialProperty,'MP_'+prop))
    def time(self):return self.node('CollectionParameter',collection=mpc,parameter_name='ShotTime')
    def uv(self):
        uv=self.node('TextureCoordinate',coordinate_index=0);x=self.node('ComponentMask',r=True,g=False,b=False,a=False);y=self.node('ComponentMask',r=False,g=True,b=False,a=False);self.link(uv,x,'');self.link(uv,y,'');return x,y
    def save(self):M.layout_material_expressions(self.m);M.recompile_material(self.m);assert E.save_loaded_asset(self.m)

g=Graph('M_TunnelGrid',True);t=g.time();p,lane=g.uv();progress=g.div(g.sub(t,5.05),3.95);d=g.sub(progress,p)
revealed=g.smooth(-.014,.014,d);peak=g.bell(d,.075)
brightness=g.node('ScalarParameter',parameter_name='Brightness',default_value=210.)
fade=g.inv(g.smooth(g.add(10.2,g.mul(p,1.1)),g.add(10.65,g.mul(p,1.1)),t))
energy=g.mul(g.mul(revealed,g.add(.15,g.mul(.85,peak))),fade)
g.out(g.mul(g.mul(energy,brightness),(.24,.83,1.)),'EMISSIVE_COLOR');g.out(1.,'OPACITY');g.save()
g=Graph('M_TunnelSurfaceFlow',True);t=g.time();p,lane=g.uv()
def pulse(start,duration):
    d=g.sub(g.add(g.div(g.sub(t,start),duration),g.mul(lane,.22)),p)
    tail=g.mul(g.smooth(-.012,.012,d),g.pow(g.sat(g.sub(1.,g.div(d,.32))),2.))
    return g.mul(g.add(g.mul(g.bell(d,.035),.7),g.mul(tail,.5)),g.smooth(start,start+.15,t))
first=g.mul(pulse(1.5,2.8),g.inv(g.smooth(4.5,4.8,t)));second=pulse(4.7,3.95)
energy=g.mul(g.add(first,second),g.inv(g.smooth(9.3,10.1,t)))
brightness=g.node('ScalarParameter',parameter_name='Brightness',default_value=520.)
g.out(g.mul(g.mul(energy,brightness),(.42,.86,1.)),'EMISSIVE_COLOR');g.out(1.,'OPACITY');g.save()
g=Graph('M_TunnelWorldWake',True);t=g.time();birth,lane=g.uv();age=g.sub(t,birth)
life=g.add(.22,g.mul(.26,g.smooth(7.7,9.6,t)));tail=g.pow(g.sat(g.sub(1.,g.div(age,life))),2.)
energy=g.mul(g.mul(tail,g.smooth(-.004,.008,age)),g.mul(g.smooth(3.1,4.,t),g.inv(g.smooth(10.1,11.6,t))))
brightness=g.node('ScalarParameter',parameter_name='Brightness',default_value=300.)
g.out(g.mul(g.mul(energy,brightness),(.26,.72,1.)),'EMISSIVE_COLOR');g.out(1.,'OPACITY');g.save()
for name,color,rough,metal,emission in [('M_TunnelWall',(.055,.068,.085),.34,.65,0),('M_TunnelRibs',(.09,.11,.14),.25,.8,0),('M_TunnelRoad',(.025,.032,.043),.32,.15,0),('M_TunnelStrip',(.55,.77,1.),.3,0,65),('M_TunnelCyan',(.025,.4,.65),.3,0,40),('M_TunnelLane',(.19,.23,.27),.65,0,0)]:
    g=Graph(name);g.out(color,'BASE_COLOR');g.out(rough,'ROUGHNESS');g.out(metal,'METALLIC')
    if emission:g.out(g.mul(color,emission),'EMISSIVE_COLOR')
    if name=='M_TunnelRoad':
        noise=g.node('Noise',scale=.6,quality=1,levels=2,output_min=0.,output_max=1.)
        g.out(g.mul(color,g.add(.72,g.mul(noise,.28))),'BASE_COLOR');g.out(g.add(.30,g.mul(noise,.13)),'ROUGHNESS')
    g.save()
RESULT={'meshes':[{'path':m.get_path_name(),'triangles':m.get_num_triangles(0)} for m in meshes],'mpc':mpc.get_path_name(),'materials':list(E.list_assets(D+'/Materials')),'no_runtime_python':True,'all_native_material_nodes':True}
(O/'assets.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
