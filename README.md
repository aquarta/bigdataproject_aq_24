# Antonio Quarta Big Data Project

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/aquarta/bigdataproject_aq_24/tree/big_data_test)

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
invoke -c services build step2-ld
```


## Newman (postman) api call to setup

setup orion
```
newman run -e Dev.postman_environment.json --folder "Add Bridges to Orion" --folder "Add service to IOT Agent" --folder "Add devices to IOT Agent WITH RELATIONSHP ATTR" 0_BData_project.postman_collection.json
```

add subscription
```
newman run -e Dev.postman_environment.json --folder "Subscribe flaskdash to orion sensors Height changes" --folder "Subscribe flaskdash to orion building changes"  0_BData_project.postman_collection.json
```

add apps id to keyrock


```
newman run  -e Dev.postman_environment.json --folder "Keyrock_login" --folder "get token info" --folder "Add application" --folder "Create new pep proxy" --folder "Create new IOT Agent" 0_BData_project.postman_collection.json  --reporters cli,json   --reporter-json-export outputfile.json --verbose --export-environment Dev.postman_environment_with_runtime_tokens.json
```
## Create PEP Proxy with IDs create on keyrock


```
invoke -c services pepproxy-build
```

## Add authenticated measure


```
newman run  -e Dev.postman_environment_with_runtime_tokens.json --folder "IOT sensor request Access Token from Keyrock" --folder "Add authenticate measure with sensor"  0_BData_project.postman_collection.json  --reporters cli,json   --reporter-json-export outputfile.json --verbose 
```


## Starting FlaskDash application

```
invoke -c services flaskdash-build
```


## Restart services after a reboot

You can start services after a reboot with:

```
invoke -c services docker-start-compose
```

