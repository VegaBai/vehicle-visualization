"""Start the installed Blender MCP add-on in an isolated factory-startup session."""
import sys
import bpy
import addon_utils

addon_dir = r"C:\Users\vegab\AppData\Roaming\Blender Foundation\Blender\5.2\scripts\addons"
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)
addon_utils.enable("blender_mcp", default_set=False, persistent=False)
import blender_mcp

if not getattr(bpy.types, "blendermcp_server", None):
    bpy.types.blendermcp_server = blender_mcp.BlenderMCPServer(host="127.0.0.1", port=9876)
bpy.types.blendermcp_server.start()
bpy.context.scene.blendermcp_server_running = bpy.types.blendermcp_server.running
print("YU7 isolated Blender MCP ready", flush=True)
