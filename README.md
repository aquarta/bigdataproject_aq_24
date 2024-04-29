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