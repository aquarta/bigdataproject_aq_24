import urllib.parse
import requests
import json
import osm2geojson
import copy as cp

CACHE = True
OVERPASS_CACHE_OUT_FILE = """overpass_out.cache"""
OVERPASS_URL = f"https://overpass-api.de/api/interpreter?data="
GEOJSON = f"overpass_out.geojson"
GEOJSON = f"filtered_overpass_out.geojson"
OVERPASS_QUERY=r"""
/*
This is an example Overpass query.
Try it out by pressing the Run button above!
You can find more examples with the Load tool.
*/
[out:json][timeout:100][bbox:40.23026664265011,17.355651855468754,40.893791536553906,18.32176208496094];
way[highway~"(primary|motorway|trunk)"][bridge][name];

        out body;
        >;
        out skel qt;

"""
query_url_encoded = urllib.parse.quote(OVERPASS_QUERY)
print(query_url_encoded)
if CACHE:
    with open(OVERPASS_CACHE_OUT_FILE) as f:
        overpass_data = json.load(f)
else:
    response = requests.request("GET",
        OVERPASS_URL+query_url_encoded,
    )

    print(response.json())
    overpass_data = response.json()
    with open(OVERPASS_CACHE_OUT_FILE,'w') as f:
        json.dump(overpass_data, f,indent=2)
print(overpass_data)

geojson = osm2geojson.json2geojson(data=overpass_data)
with open(GEOJSON,'w') as f:
    json.dump(geojson, f,indent=2)

print(f'Unfiltered len {len(geojson["features"])}')

filtered_feature_collection_geojson = []
for gfeature in geojson["features"]:
    feat_name = gfeature['properties']['tags'].get("name", None)
    if feat_name is not None:
        print(feat_name)
        filtered_feature_collection_geojson.append(gfeature)
print(f'filtered len {len(filtered_feature_collection_geojson)}')
print(gfeature)

bridge_template = {
    "id": "urn:ngsi-ld:Building:waybridge31061690",
    "type": "Building",
    "category": {
      "type": "Property",
      "value": [
        "bridge"
      ]
    },
    "location": {
      "type": "GeoProperty",
      "value": {
        "type": "Point",
        "coordinates": []
      }
    },
    "name": {
      "type": "Property",
      "value": "Strada Statale 107 Silana Crotonese"
    },
    "BuildingStatus": {
      "type": "Property",
      "value": "ok"
    }
  }


buildings = []
for gfeature in filtered_feature_collection_geojson:
    bridge_template_wc = cp.deepcopy(bridge_template)
    bridge_template_wc['id']=f"urn:ngsi-ld:Building:waybridge{gfeature['properties']['id']}"
    bridge_template_wc['name']['value']=gfeature['properties']['tags']['name']
    bridge_template_wc['location']["value"]['coordinates'] = gfeature['geometry']['coordinates'][0]
    buildings.append(bridge_template_wc)

with open("buildings.json",'w') as f:
   json.dump(buildings, f,)


device_id_template = {
      "device_id": "hsensor31061690",
      "entity_name": "urn:ngsi-ld:Device:hsensor:31061690",
      "entity_type": "Device",
      "timezone": "Europe/Rome",
      "attributes": [
        {
          "object_id": "l",
          "name": "location",
          "type": "GeoProperty"
        },
        {
          "object_id": "h",
          "name": "height",
          "type": "Property",
          "metadata": {
            "unitCode": {
              "type": "Text",
              "value": "m"
            }
          }
        },
        {
          "object_id": "n",
          "name": "name",
          "type": "Property"
        },
        {
          "object_id": "b",
          "name": "batteryLevel",
          "type": "Property"
        }
      ],
      "static_attributes": [
        {
          "name": "controlledAsset",
          "type": "Relationship",
          "value": "urn:ngsi-ld:Building:waybridge31061690"
        }
      ]
    }

devices = []
for gfeature in filtered_feature_collection_geojson:
    device_id_template_wc = cp.deepcopy(device_id_template)
    device_id_template_wc['device_id']=f"hsensor{gfeature['properties']['id']}"
    device_id_template_wc['entity_name']=f"urn:ngsi-ld:Device:hsensor:{gfeature['properties']['id']}"
    for stat_attr in device_id_template_wc['static_attributes']:
        if stat_attr["name"] == "controlledAsset" and stat_attr["type"] == "Relationship":
            stat_attr['value'] = f"urn:ngsi-ld:Building:waybridge{gfeature['properties']['id']}"

    devices.append(device_id_template_wc)

with open("devices.json",'w') as f:
   json.dump(devices, f,)


