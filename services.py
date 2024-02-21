from time import sleep
from dotenv import load_dotenv
from invoke import task
import os
#loading the .env file in dir
load_dotenv()

dockerCmd="podman-compose"
onlydocker_cmd = "podman"

@task
def up_service(c, dfile="orion-wilma-perseo"):
    c.run(f"{dockerCmd} -f docker-compose/{dfile}.yml up -d --remove-orphans", echo=True)


def waitFor(c,cname="db-mongo", comment="MongoDB"):
    print(fr"⏳ Waiting for \033[1m{comment}\033[0m to be available")
    healty = False
    for i in range(100):
        res = c.run(onlydocker_cmd + " inspect --format='{{.State.Health.Status}}' " + cname, echo=True)
        # avoid unealthy match
        if res.stdout.find("healthy")==0:
            healty=True
            break
        sleep(1)
    if not healty:
        raise ValueError
    print(fr"✅ Done for \033[1m{comment}\033[0m to be available")

	
	
@task
def step2(c):
    waitFor(c,cname="fiware-keyrock", comment="KeyRock")
    #waitFor(c,"db-mongo", "MongoDB")
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
def import_data(c):

    first_command = """ run --rm -v $(pwd)/import-data:/import-data \
        --network fiware_default \
        -e ORION_PORT="${ORION_PORT}" \
        -e TUTORIAL_APP_PORT="${TUTORIAL_APP_PORT}" \
        --entrypoint /bin/ash quay.io/curl/curl /import-data"""
    c.run(onlydocker_cmd + first_command)
    waitFor(c,cname="fiware-iot-agent",comment="IOT Agent")
    second_cmd = """ run --rm -v $(pwd)/provision-devices:/provision-devices \
        --network fiware_default \
        -e ORION_PORT="${ORION_PORT}" \
        -e TUTORIAL_APP_PORT="${TUTORIAL_APP_PORT}" \
        -e TUTORIAL_DUMMY_DEVICE_PORT="${TUTORIAL_DUMMY_DEVICE_PORT}" \
        -e IOTA_NORTH_PORT="${IOTA_NORTH_PORT}" \
        --entrypoint /bin/ash quay.io/curl/curl /provision-devices """
    c.run(onlydocker_cmd + second_cmd)



@task
def remove_db_volumes(c):
    c.run(onlydocker_cmd+ " volume rm fiware_mysql-db",echo=True)
    c.run(onlydocker_cmd+ " volume rm fiware_mongo-db",echo=True)

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
