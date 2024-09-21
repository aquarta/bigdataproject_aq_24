


from flask import Flask, render_template, request, Response, Blueprint, url_for
from flask_assets import Environment
from flask_socketio import SocketIO, send, emit
import os
import requests
import logging

import database as db
import model.models as mdl

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from blueprints import email_actions, http_actions

app = Flask(__name__)
#socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
socketio = SocketIO(app, cors_allowed_origins="*", )
assets = Environment(app)

ORION_URL = os.environ.get("ORION_URL", "http://orion:1026")
IOTA_NORTH_URL = os.environ.get("IOTA_NORTH_URL", "http://iot-agent:14041")
LORA_IOTA_NORTH_URL = os.environ.get("LORA_IOTA_NORTH_URL", "http://iotagent-lora:4041")

HEIGHT_SENSOR_TYPE_STR = "HeightSensor"
FIWARE_SERVICE = "openiot"
NGSI_PATH = "/"
CONTEXT_URL = "http://context/ngsi-context.jsonld"

api = Blueprint('api',__name__, )
v1_api = Blueprint('v1_api', __name__,url_prefix='/v1')

TRESHOLD_VALUE = 2

def print_request(r):
    app.logger.info("-"*100)
    app.logger.info(f"request.url: {r.url}")
    app.logger.info(r.headers)
    app.logger.info(f"request.data: {r.data}")
    app.logger.info(f"request.args: {r.args}")
    app.logger.info(f"request.form: {r.form}")
    app.logger.info(f"request.values: {r.values}")
    try:
        app.logger.info(f"request.json: {r.json}")
    except Exception:
        pass
    print(r.method)
    print(r.remote_addr)
    print("="*100)
    return ''

@app.route('/')
def empty():
	return "Hello World!"


def send_http_action(bridgeid, status, building_info):
    http_acts = mdl.HttpAction({}).get_all()
    lat = building_info.get("location").get("value").get("coordinates")[1]
    lon = building_info.get("location").get("value").get("coordinates")[0]
    name = building_info.get("name").get("value")
    for http_action in http_acts:
        app.logger.info(http_action)
        json_act = http_action.get("json", None)
        if not json_act:
            qs = http_action.get("qs", None)
            for key,value in qs.items():
                key = key.format(
                    building_id=bridgeid,
                    lat=lat,
                    lon=lon,
                    name=name,
                    )
                qs[key] = value.format(
                    building_id=bridgeid,
                    lat=lat,
                    lon=lon,
                    name=name,
                    )
                app.logger.info(f"{key},{value}")
            app.logger.info(f"QS {qs}")
            req_kwargs = {"params" : qs}
        else:
            for key,value in json_act.items():
                key = key.format(
                    building_id=bridgeid,
                    lat=lat,
                    lon=lon,
                    name=name,
                    )
                json_act[key] = value.format(
                    building_id=bridgeid,
                    lat=lat,
                    lon=lon,
                    name=name,
                    )
                app.logger.info(f"{key},{value}")
            app.logger.info(f"{json_act}")
            req_kwargs = {"json" : json_act}
        try:
            res = requests.request(
                http_action.get("method", None),
                http_action.get("url", None),
                
                headers=http_action.get("headers", None),
                **req_kwargs
            )
            app.logger.info(f"HTTPACTION RESULTS status {res.status_code} response put {res.content}")
        except Exception as e:
            app.logger.exception(e)

def send_email(bridgeid, status, building_info):
    email_acts = mdl.EmailAction({}).get_all()
    for idx,email_action in enumerate(email_acts):
        app.logger.info(f"Process {idx} rule")
        msg = EmailMessage()

        msg['Subject'] = email_action.get("subject", f'Building Warning {bridgeid}: status {status}')+f" building id {bridgeid}"      
        msg['From'] = sender =  email_action.get("usernanme","antonio.quarta1+SOGEI@studenti.unisalento.it")
        msg['To'] = email_action.get("usernanme","antonio.quarta1+SOGEI@studenti.unisalento.it")
        msg.add_header('Content-Type','text/html')
        MSG_CONTENT_DEFAULT = f"""
        The bridge {bridgeid} require attention: status {status}
        """
        lat = building_info.get("location").get("value").get("coordinates")[1]
        lon = building_info.get("location").get("value").get("coordinates")[0]
        name = building_info.get("name").get("value")
        openstreetmap_template = """
        <h2>Building {name} [{bid}]  require attention</h2>
        <br/><a href="https://www.openstreetmap.org/?mlat={lat}&amp;mlon={lon}#map=14/{lat}/{lon}&amp;layers=N">View Map Marker</a>
        """
        message_text = email_action.get("message",MSG_CONTENT_DEFAULT)+openstreetmap_template.format(box_lat_min=lat-0.01,box_lon_min=lon-0.01,
        box_lat_max=lat+0.01,box_lon_max=lon+0.01,
         lat=lat, lon=lon, bid=bridgeid,name=name)

        SMTP_SERVER = email_action.get("smtp","smtp.gmail.com")
        SMTP_PORT = email_action.get("port",465)
        PASSWORD = email_action.get("password","")

        
        html_part = MIMEText(message_text, 'html')
        msg.set_content(html_part)

        if email_action.get("SSL_auth",False):
            smtp_conn = smtplib.SMTP_SSL
        else:
            smtp_conn = smtplib.SMTP
        try:
            with smtp_conn(SMTP_SERVER, SMTP_PORT) as smtp_server:
            
                smtp_server.set_debuglevel(2)
                smtp_server.login(sender, PASSWORD)
                app.logger.info(f"SEND MAIL {bridgeid} {status}")
                smtp_server.sendmail(
                    msg['From'],
                    msg['To'],
                    msg.as_string()
                    )
        except Exception as e:
            app.logger.exception(e)
            app.logger.error(f"Fail to send email {e}")

@app.route("/perseo_post",methods=['GET', 'POST', 'PUT'])
def perseo_post():
    print_request(request)
    return ''

def map_status_update(bridgeid, status):
    app.logger.info(f"UPDATE Bridge ID {bridgeid} {status}")
    building_info = get_building_info(bridgeid)
    send_email(bridgeid, status, building_info)
    send_http_action(bridgeid, status, building_info)
    emit('update_bridge_status', {'bridgeid':bridgeid, "status":status},namespace="/", broadcast=True)

@app.route('/map_update', methods=["PUT"])
def map_update():
    status = request.args['status']
    bridgeid = request.args['bridgeid']
    content_type = request.headers.get('Content-Type')
    app.logger.info(f"status {status}")
    app.logger.info(f"content_type {content_type}")
    app.logger.info(f"request-args {request.args}")
    map_status_update(bridgeid, status)

    return ""

def get_sensor_attr_from_notification(data, attr_type):
    if data is None:
        return
    for attr in data:
        if attr.get("type",None) == attr_type:
            return attr
    return None

def get_sensor_height_and_previous(height_sensor_notification_data):
    height = height_sensor_notification_data.get("height", {}).get("value", None)
    previous_value = height_sensor_notification_data.get("height", {}).get("previousValue",height)
    return height, previous_value

def get_sensor_location_and_previous(sensor_notification_data):
    height = sensor_notification_data.get("location", {}).get("value", None)
    previous_value = sensor_notification_data.get("location", {}).get("previousValue",height)
    return height, previous_value


def update_building_status_upsert_strategy(bridgeid):
    url = ORION_URL+"/ngsi-ld/v1/entityOperations/upsert/?options=update"
    app.logger.info(f"Building URL  {url}")
    res = requests.request(
        "POST",
        url,
        json=[
            {
            "@context": CONTEXT_URL,
            "id":bridgeid+"/",
                "type":"Building",
                "BuildingStatus": {
                    "type": "Property",
                    "value": "bad"
                }
            }
            ],
        headers={"Content-Type": "application/ld+json", "Accept": "application/ld+json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/"}
    )
    app.logger.info(f"response status code {bridgeid} put {res.status_code}")
    app.logger.info(f"response put {res.content}")

def update_building_status_patch_strategy(bridgeid, status):
    url = ORION_URL+f"/ngsi-ld/v1/entities/{bridgeid}/attrs/BuildingStatus"
    app.logger.info(f"Building URL  {url}")
    res = requests.request(
        "PATCH",
        url,
        json={
        "type": "Property",
        "value": status
        },
        headers={ "Accept": "application/ld+json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/","Link":f"<{CONTEXT_URL}>; rel=\"http://www.w3.org/ns/json-ld#context\"; type=\"application/ld+json\""}
    )
    app.logger.info(f"response status code {bridgeid} put {res.status_code}")
    app.logger.info(f"response patch {res.content}")

def get_building_info(bridgeid):
    url = ORION_URL+f"/ngsi-ld/v1/entities/{bridgeid}"
    app.logger.info(f"Building URL  {url}")
    res = requests.request(
        "GET",
        url,
        headers={ "Accept": "application/ld+json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/","Link":f"<{CONTEXT_URL}>; rel=\"http://www.w3.org/ns/json-ld#context\"; type=\"application/ld+json\""}
    )
    app.logger.info(f"response status code {bridgeid} get {res.status_code}")
    app.logger.info(f"response get {res.content}")
    return res.json()


def is_warning_event(height, previousheight):
    return abs(height-previousheight)>TRESHOLD_VALUE

@v1_api.route('/sens_notify', methods=["POST"])
def sens_move():
    # Expected HeightSensor
    app.logger.info(f"request {request.json}")
    notification_type = request.json.get('type',None)
    sensor_attr = get_sensor_attr_from_notification(request.json.get('data',None), HEIGHT_SENSOR_TYPE_STR)
    # if sensor_attr means that a sensorid is present
    if sensor_attr:
        sensid = sensor_attr.get('id',None)
    else:
        return Response(f"No sensor id {sensid} found.", 404)

    # device_id is internal reference for IOT agent
    device_id = sensid.split(":")[-1]
    #    height = request.json.get('data',{}).get("height",{}).get('value',None)
    data = get_sensor_attr_from_notification(
            request.json.get('data',{}),"HeightSensor"
        )
    height,previousheight = get_sensor_height_and_previous(
                                data
                            )
    if height:
        app.logger.info(f"Sensor {sensid} - height {height} - previous {previousheight}")
        iota_url = IOTA_NORTH_URL
    else:
        app.logger.info(f"No height in notification")
        location,previouslocation = get_sensor_location_and_previous(
                                        data
                                    )
        if location is None or previouslocation is None:
            app.logger.info(f"No location info")
            return Response(f"No  info to update.", 204)
        height,previousheight = location["altitude"],previouslocation["altitude"]
        app.logger.info(f"Height from altitude {height,previousheight}")
        if device_id.find("hsensor")<0:
            device_id = "hsensor"+device_id
        iota_url = LORA_IOTA_NORTH_URL


    if notification_type != "Notification" or  sensor_attr['type'] != HEIGHT_SENSOR_TYPE_STR:
        return Response(f"Wrong type, expected {HEIGHT_SENSOR_TYPE_STR}", 400)
    if not sensid:
        return Response(f"No sensor id {sensid} found.", 404)
    if not is_warning_event(height=height,previousheight=previousheight):
        return Response(f"No warning {sensid}.", 204)
    url = iota_url+"/iot/devices/"+device_id
    app.logger.info(url)
    res = requests.request(
        "GET",
        url,
        headers={"Accept": "application/ld+json","Fiware-Service":FIWARE_SERVICE,"fiware-servicepath":"/", "NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/"}
    )

    content_type = request.headers.get('Content-Type')

    app.logger.info(f"response {res.json()}")
    sattrs = res.json().get('static_attributes',None)
    if sattrs:
        bridgeid = None
        for satt in sattrs:
            if satt.get("name") == "controlledAsset" and satt.get("type") == "Relationship":
                bridgeid = satt.get("value") 
                bridgeid = bridgeid if bridgeid else satt.get("object") 
                break
        app.logger.info(f"Bridge id extracted {bridgeid}")
        if bridgeid:
            update_building_status_upsert_strategy(bridgeid)
            update_building_status_patch_strategy(bridgeid, status="bad")
            map_status_update(bridgeid,"bad")
        else:
            return Response(f"No Building id {bridgeid} found.", 404)
    return ""



@app.route('/map/')
def map_view():


    res = requests.request(
        "GET",
        ORION_URL+"/ngsi-ld/v1/entities/",
        params={
            "type":"https://github.com/smart-data-models/dataModel.Building/tree/master/Building", 
            #"type":"https://uri.fiware.org/ns/dataModels#Building", 
            "options": "keyValues",
            "limit": 200,
            },
        headers={"Accept": "application/json","NGSILD-Tenant":FIWARE_SERVICE, "NGSILD-Path":"/"}
    )


    markers=[]
    bridges = res.json()
    app.logger.info(f"Number of bridges {len(bridges)} ")
    for bridge in bridges:
        app.logger.info(bridge)
        if isinstance(bridge, dict):
            markers.append({
                'lon':bridge['location']['coordinates'][0],
                'lat':bridge['location']['coordinates'][1],
                "popup":bridge["https://schema.org/name"]+"  "+f'{bridge["id"]}',
                "status":bridge["BuildingStatus"],
                "id": bridge["id"],
            })


    return render_template('leaflet.html',  markers=markers)

# this has to be configured after definition of routes
v1_api.register_blueprint(email_actions.bp)
v1_api.register_blueprint(http_actions.bp)
api.register_blueprint(v1_api, url_prefix='/v1')
app.register_blueprint(api, url_prefix='/api')



if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=8000, debug=True)
    app.logger.setLevel(logging.DEBUG)

    socketio.run(app, allow_unsafe_werkzeug=True, host='0.0.0.0', port=8000, debug=True)