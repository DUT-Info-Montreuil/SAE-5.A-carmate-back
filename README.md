# Projet SAE - Carmate
## Sommaire
- [Comment lancer l'API manuellement](#comment-lancer-lapi-manuellement)
    - [Commande pour lancer l'API en mode `TEST`](#commande-pour-lancer-lapi-en-mode-test)
    - [Commande pour lancer l'API en mode `PROD`](#commande-pour-lancer-lapi-en-mode-prod)
- [Image Docker](#image-docker)
    - [Variable d'environment](#variable-denvironment)
    - [Comment execute l'image](#comment-execute-limage)
- [Endroit pratique pour le development](#endroit-pratique-pour-le-development)

## Comment lancer l'API manuellement
Vous devez vous placez a la racine du projet, la base de la commande sera :
```
PYTHONPATH=`pwd` python3 src/main.py
```
Mais cette base ne permet pas de faire fonctionner l'API, vous devez set des variables d'environnement supplémentaire :
- `API_NAME` (optionnel)
- `API_PORT` (**obligatoire**)
- `API_MODE`, les valeurs possible (**obligatoire**):
    - `PROD`
    - `TEST`
- `POSTGRES_DB` (obligatoire pour un environnement de `PROD`)
- `POSTGRES_USER` (obligatoire pour un environnement de `PROD`)
- `POSTGRES_PWD` (obligatoire pour un environnement de `PROD`)
- `POSTGRES_HOST` (obligatoire pour un environnement de `PROD`)
- `POSTGRES_PORT` (obligatoire pour un environnement de `PROD`)

### Commande pour lancer l'API en mode `TEST`
#### Linux:
```
PYTHONPATH=`pwd` \
API_MODE=TEST \
API_PORT=5000 \
python3 src/main.py
```
#### Windows:
```
$env:API_MODE="TEST"
$env:API_PORT=5000
$env:PYTHONPATH="$(pwd)"
python .\src\main.py
```

### Commande pour lancer l'API en mode `PROD`
#### Linux:

```
PYTHONPATH=`pwd` \
API_MODE=PROD \
API_PORT=5000 \
POSTGRES_DB=postgres \
POSTGRES_USER=postgres \
POSTGRES_PWD=postgres \
POSTGRES_HOST=localhost \
POSTGRES_PORT=5432 \
python3 src/main.py
``` 

#### Windows:
```
$env:API_PORT=5000
$env:API_MODE="PROD"
$env:POSTGRES_DB="postgres"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PWD="postgres"
$env:PYTHONPATH="$(pwd)"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT=5432
python .\src\main.py
```

## Image Docker
### Variable d'environment 
- `API_NAME`
- `API_PORT`
- `API_MODE`, valeurs possible :
    - `PROD`
    - `TEST`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PWD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
### Comment execute l'image ?
Pour lancer l'image Docker depuis votre machine, vous devez tous d'abord `pull` l'image :
```
docker pull ghcr.io/dut-info-montreuil/sae-5.a-carmate-back:latest
```
Ensuite, lancez l'image Docker :
```
docker run \
    --env API_PORT=5000
    --env API_MODE=TEST \
    --name carmate-back \
    -p 5000:5000 \
    -d ghcr.io/dut-info-montreuil/sae-5.a-carmate-back:latest
```

## Endroit pratique pour le development
Un `CODESTYLE` est disponible [ici](/docs/CODESTYLE.md)

Un `HOWTO` est disponible [ici](/docs/HOWTO.md)

Un `DEVELOPMENT` est disponible [ici](/docs/DEVELOPMENT.md)
