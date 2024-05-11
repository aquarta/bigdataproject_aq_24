from time import sleep
from dotenv import load_dotenv
from invoke import task
import os
#loading the .env file in dir
load_dotenv()

dockerCmd="docker-compose"
onlydocker_cmd = "docker"
IS_GITPOD_WORKSPACE = os.environ.get("GITPOD_REPO_ROOT", None) is not None

@task
def create_ld(c, dfile="orion-wilma-perseo"):
    build(c, dfile=dfile)
    step2_ld(c)

@task
def set_gitpod_public_ports(c,):
    if IS_GITPOD_WORKSPACE:
        # Make orion ports accessible from remote
        c.run(f"gp ports visibility 1026:public", echo=True)
        c.run(f"gp ports visibility 14041:public", echo=True)
        c.run(f"gp ports visibility 13005:public", echo=True)
        c.run(f"gp ports visibility 7896:public", echo=True)


@task
def build(c, dfile="orion-wilma-perseo"):
    set_gitpod_public_ports(c)
    c.run(f"{dockerCmd} -f docker-compose/{dfile}.yml up -d --remove-orphans", echo=True)

@task
def start_docker_compose(c, dfile="orion-wilma-perseo"):
    set_gitpod_public_ports(c)
    c.run(f"{dockerCmd} -f docker-compose/{dfile}.yml start", echo=True)


@task
def pepproxy_build(c, dfile="wilma"):
    c.run(f"{dockerCmd} -f docker-compose/{dfile}.yml up -d", echo=True)
    


def waitFor(c,cname="db-mongo", comment="MongoDB"):
    print(fr"⏳ Waiting for \033[1m{comment}\033[0m to be available")
    healthy = False
    for i in range(100):
        res = c.run(onlydocker_cmd + " inspect --format='{{.State.Health.Status}}' " + cname, echo=True)
        # avoid unealthy match
        if res.stdout.find("healthy")==0:
            healthy=True
            break
        sleep(1)
    if not healthy:
        raise ValueError
    print(fr"✅ Done for \033[1m{comment}\033[0m to be available")

	
	
@task
def step2(c):
    waitFor(c,cname="fiware-keyrock", comment="KeyRock")
    waitFor(c,"db-mongo", "MongoDB")
    os.environ["ORION_URL"]="http://orion:"+os.environ["ORION_PORT"]
    first_cmd = """ exec db-mongo mongosh --eval '
	conn = new Mongo();db.createCollection("orion");
	db = conn.getDB("orion");
	db.createCollection("entities");
	db.entities.createIndex({"_id.servicePath": 1, "_id.id": 1, "_id.type": 1}, {unique: true});
	db.entities.createIndex({"_id.type": 1}); 
	db.entities.createIndex({"_id.id": 1});'"""
    #c.run(onlydocker_cmd + first_cmd)

    second_cmd = """ exec db-mongo mongosh --eval '
	conn = new Mongo();db.createCollection("orion-openiot");
	db = conn.getDB("orion-openiot");
	db.createCollection("entities");
	db.entities.createIndex({"_id.servicePath": 1, "_id.id": 1, "_id.type": 1}, {unique: true});
	db.entities.createIndex({"_id.type": 1}); 
	db.entities.createIndex({"_id.id": 1});' """
    c.run(onlydocker_cmd + second_cmd)


    waitFor(c,cname="fiware-orion", comment="ORION")
    

@task
def step2_ld(c):
    waitFor(c,cname="fiware-keyrock", comment="KeyRock")
    waitFor(c,"db-mongo", "MongoDB")

    first_cmd = """ exec db-mongo mongo --eval '
	conn = new Mongo();db.createCollection("orion");
	db = conn.getDB("orion");
	db.createCollection("entities");
	db.entities.createIndex({"_id.servicePath": 1, "_id.id": 1, "_id.type": 1}, {unique: true});
	db.entities.createIndex({"_id.type": 1}); 
	db.entities.createIndex({"_id.id": 1});'"""

    second_cmd = """ exec db-mongo mongo --eval '
	conn = new Mongo();db.createCollection("orion-openiot");
	db = conn.getDB("orion-openiot");
	db.createCollection("entities");
	db.entities.createIndex({"_id.servicePath": 1, "_id.id": 1, "_id.type": 1}, {unique: true});
	db.entities.createIndex({"_id.type": 1});
	db.entities.createIndex({"_id.id": 1});'"""

    third_cmd = """ exec db-mongo mongo --eval '
	conn = new Mongo();
	db = conn.getDB("iotagentul");
	db.getCollectionNames().forEach(c=>db[c].drop());
	db.createCollection("devices");
	db.devices.createIndex({"_id.service": 1, "_id.id": 1, "_id.type": 1});
	db.devices.createIndex({"_id.type": 1});
	db.devices.createIndex({"_id.id": 1});
	db.createCollection("groups");
	db.groups.createIndex({"_id.resource": 1, "_id.apikey": 1, "_id.service": 1});
	db.groups.createIndex({"_id.type": 1});'"""

    for cmd in [first_cmd, second_cmd, third_cmd]:
        c.run(onlydocker_cmd + cmd)

@task
def import_data(c):
    """ use newman to import data with postman collection """
    c.run('newman run -e pman_env.json --folder "Add Bridges to Orion" --folder "Add service to IOT Agent" --folder "Add devices to IOT Agent" 0_BData_project.postman_collection.json')

@task
def setup_orion_perseo_subs(c):
    ...


@task
def remove_db_volumes(c):
    c.run(onlydocker_cmd+ " volume rm fiware_mysql-db",echo=True)
    c.run(onlydocker_cmd+ " volume rm fiware_mongo-db",echo=True)
    c.run(onlydocker_cmd+ " volume rm fiware_mqtt_data",echo=True)
     

@task
def down(c, dfile="orion-wilma-perseo"):
    c.run(onlydocker_cmd+f" compose -f docker-compose/{dfile}.yml down", echo=True)

@task
def rem_network(c, net="fiware_default"):
    c.run(onlydocker_cmd+f"  network rm {net}")

@task
def purge(c):
    down(c)
    remove_db_volumes(c)
    rem_network(c)



@task
def start(c, dfile="orion-wilma-perseo"):
    c.run(f"{dockerCmd} -f docker-compose/{dfile}.yml start ", echo=True)
