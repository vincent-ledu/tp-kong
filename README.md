# TP Kong

## Source

https://docs.konghq.com/gateway/latest/install/docker/#main

## Description

TP de mise en place d'une route API avec Kong

## Lancement de Kong

- Création d'un réseau docker `kong-net` pour les communication entre la base de données et la gateway kong

```shell
docker network create  kong-net
```

- Lancement d'une base de données postgresql

```shell
docker run -d --name kong-database \
 --network=kong-net \
 -p 5432:5432 \
 -e "POSTGRES_USER=kong" \
 -e "POSTGRES_DB=kong" \
 -e "POSTGRES_PASSWORD=kongpass" \
 postgres:13
```

- Initialisation de la base de données pour kong

```shell
docker run --rm --network=kong-net \
 -e "KONG_DATABASE=postgres" \
 -e "KONG_PG_HOST=kong-database" \
 -e "KONG_PG_PASSWORD=kongpass" \
 -e "KONG_PASSWORD=test" \
kong/kong-gateway:3.5.0.3 kong migrations bootstrap
```

- Lancement de la gateway

```shell
docker run -d --name kong-gateway \
 --network=kong-net \
 -e "KONG_DATABASE=postgres" \
 -e "KONG_PG_HOST=kong-database" \
 -e "KONG_PG_USER=kong" \
 -e "KONG_PG_PASSWORD=kongpass" \
 -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
 -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
 -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
 -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
 -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
 -e "KONG_ADMIN_GUI_URL=http://localhost:8002" \
 -e KONG_LICENSE_DATA \
 -p 8000:8000 \
 -p 8443:8443 \
 -p 8001:8001 \
 -p 8444:8444 \
 -p 8002:8002 \
 -p 8445:8445 \
 -p 8003:8003 \
 -p 8004:8004 \
 kong/kong-gateway:3.5.0.3
```

- Accès à l'interface kong

http://localhost:8002

## Ecriture d'une API (en python)

### venv

Bonne pratique :

- Créer un environnement étanche d'exécution python avec `venv`

https://docs.python.org/fr/3/library/venv.html

```shell
python3 -m venv $(pwd)
```

- Activation de l'environnement virtuel

```shell
source bin/activate
```

- Afficher les dépendances

```shell
pip freeze
```

- Créer un fichier avec les dépendance du projet

```shell
pip freeze > requirements.txt
```

- Installer les dépendances d'un projet

```shell
pip install -r requirements.txt
```

### Flask

Fichier `myapi.py`

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/launcher/banana")
def banana():
    return "🍌"


@app.route("/launcher/cucumber")
def cucumber():
    return "🥒"
```

- Lancement du projet python

```shell
flask --app myapi --debug run --host=192.168.0.69
```

- Test de l'API

```shell
curl http://192.168.0.69:5000/launcher/banana
curl http://192.168.0.69:5000/launcher/cucumber
```

## Kong

### Passage par kong pour lancer des bananes !

- Définir un service
  - namespace default > Gateway services > + New Gateway Service
    - name : konglauncher
    - tags : banana, cucumber
    - Upstream url : http://192.168.0.69:5000/launcher
- Définir une route

  - namespace default > Routes > + New Route
    - name : kongroute
    - protocols : http/https
    - path : /konglauncher

- On peut maintenant appeler notre lanceur de banane via kong:

```shell
curl http://localhost:8000/konglauncher/banana
```

### Plugin ratelimit

- Plugin > Enable > Rate limiting

  - Instance name : ip_limiting
  - Limit by : ip (ou consumer)
  - minute : 10

- Test :

```shell
while true; do curl http://localhost:8000/konglauncher/banana ; done
```

### Plugin api key

- Plugin > Enable > key-auth
  - Instance name : mykey auth
  - key_names: apikey
- Consumer > + New Consumer

  - username : tp
  - credentials > key > mykey

- Test :

```shell
curl http://localhost:8000/konglauncher/banana
```

```shell
curl -H "apikey: mykey1" http://localhost:8000/konglauncher/banana
```
