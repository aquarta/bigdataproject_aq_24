# Antonio Quarta Big Data Project

## Contents

This project implements docker compose and postman collection
for  an information system capable of providing real-time
information on buildings and infrastructure during emergencies, with the aim of improving the
management of people transportation and ensuring population safety.

This system employ several FIWARE tecnologies.

It use:

- Fiware Orion
- Fiware Keyrock
- Fiware IOTAgent UL
- Fiware IOTAgent lora
- Fiware Wilma
- Fiware perseo

## starting docker compose

The project require, python, invoke python package and python-loadenv python package.

then type:

```
invoke -c services up-docker-compose step2-ld
```


## Newman (postman) api call to setup

setup orion
```
newman run -e pman_env.json --folder "Add Bridges to Orion" --folder "Add service to IOT Agent" --folder "Add devices to IOT Agent" 0_BData_project.postman_collection.json
```

add subscription
```
newman run -e pman_env.json --folder "Subscribe perseo to orion sensors elevation changes" --folder "Subscribe perseo to orion Bridge Status" --folder "[DBG] GET Subscription" 0_BData_project.postman_collection.json
```

setup perseo actions

```
newman run -e pman_env.json --folder "Add Bridge status rule to perseo" --folder "Subscribe perseo to orion Bridge Status"  0_BData_project.postman_collection.json
```


add apps id to keyrock


```
newman run  -e pman_env.json --folder "Keyrock_login" --folder "get token info" --folder "Add application" 0_BData_project.postman_collection.json
 -reporters cli,json   --reporter-json-export outputfile.json 
 
```
## Create PEP Proxy with IDs create on keyrock


```
invoke -c services pepproxy-build
```