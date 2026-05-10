from src.config_loader import config
import pykx as kx

# Pull infrastructure settings dynamically
kdb_host = config.system['databases']['kdb']['host']
hdb_port = config.system['databases']['kdb']['hdb_port']

print(f"Connecting to kdb+ HDB at {kdb_host}:{hdb_port}...")
# q_conn = kx.SyncQConnection(host=kdb_host, port=hdb_port)