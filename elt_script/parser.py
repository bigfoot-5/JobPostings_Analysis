# import subprocess

# source_config = {
#     'dbname' : 'source_db',
#     'user' : 'postgres',
#     'password': 'secret',
#     'host': 'localhost',
#     'port': '5433'
# }

# subprocess_env = dict(PGPASSWORD=source_config['password'])

# subprocess.run(['psql -U postgres -h localhost -p 5433'], env=subprocess_env, check=True)