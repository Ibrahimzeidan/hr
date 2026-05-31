import psycopg
from psycopg import pq

# List all SSL-related options
for opt in pq.Conninfo.get_defaults():
    kw = opt.keyword.decode()
    if 'ssl' in kw or 'sni' in kw.lower():
        val = opt.val.decode() if opt.val else ''
        label = opt.label.decode() if opt.label else ''
        print(f'{kw}: val="{val}", label="{label}"')