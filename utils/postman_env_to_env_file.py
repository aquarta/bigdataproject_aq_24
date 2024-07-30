import json
import pathlib as pt

this_dir = pt.Path(__file__).parent

POSTMAN_ENV_FILE = this_dir/"../Dev.postman_environment.json"

postman_env = json.load(open(POSTMAN_ENV_FILE))
with open(this_dir/"postman_env", "w")as f:
    for env_var in postman_env['values']:
        f.write(f'{env_var["key"]}={env_var["value"]}\n')


