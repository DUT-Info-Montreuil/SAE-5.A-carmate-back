# Endroit pratique pour le development
## Sommaire
- [Structure du projet](#structure-du-projet)
    - [Aperçu général](#aperçu-général)
    - [Description](#description)
- [Comment lancer l'API manuellement](#comment-lancer-lapi-manuellement)
    - [Commande pour lancer l'API en mode `TEST`](#commande-pour-lancer-lapi-en-mode-test)
    - [Commande pour lancer l'API en mode `PROD`](#commande-pour-lancer-lapi-en-mode-prod)
- [Image Docker](#image-docker)
    - [Variable d'environment](#variable-denvironment)
    - [Comment execute l'image](#comment-execute-limage)
- [Lancer une base de données local](#lancer-une-base-de-données-local)
    - [Vierge](#vierge)
    - [Avec fixtures](#avec-fixtures)
- [Lancer les tests unitaire](#lancer-les-tests-unitaire)

## Structure du projet
### Aperçu général
```
📁 - src
^
| 📄 - requirements.txt
| 📁 - api
|  ^
|  | 📄 - exceptions.py
|  | 📄 - __init__.py
|  | 📁 - controller
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📁 - user
|  |  |  ^ 
|  |  |  | 📄 - __init__.py
|  |  |  | 📄 - user.py
|  |
|  | 📁 - worker
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📁 - user
|  |  |  ^
|  |  |  | 📄 - __init__.py
|  |  |  | 📁 - models
|  |  |  |  ^
|  |  |  |  | 📄 - __init__.py
|  |  |  |  | 📄 - user_dto.py
|  |  |  |
|  |  |  | 📁 - use_case
|  |  |  |  ^
|  |  |  |  | 📄 - __init__.py
|  |  |  |  | 📄 - get_user.py
|
| 📁 - database
|  ^
|  | 📄 - __init__.py
|  | 📄 - schemas.py
|  | 📁 - interfaces
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📄 - user_repository_interface.py
|  |  | 📄 - ...
|  | 📁 - repositories
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📄 - user_repository.py
|  |  | 📄 - ...
|
| 📁 - mocks
|  ^
|  | 📄 - __init__.py
|  | 📁 - user
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📄 - in_memory_user_repository.py
|
📁 - test
^
| 📄 - __init__.py
| 📁 - user
|  ^
|  | 📄 - __init__.py
|  | 📄 - test_send_message.py
|  | 📄 - ...
|
📄 - .gitignore
📄 - Dockerfile
📄 - README.md
```

### Description :
- `📁 - src`: Un dossier qui contient le code source de l'API
- `📄 - requirements.txt`: Un fichier qui contient les dépendances du projet
- `📁 - api`: Un dossier qui contient uniquement le code qui concerne l'API, toute trace de DB doit être enlevé !
    - `📄 - exceptions.py`: Un fichier qui contient les exceptions que le module peut remonter
    - `📁 - controller`: Un dossier qui contient uniquement les déclarations des routes.
    Les routes doivent traduire les erreurs qui proviennent du worker en code d'erreur HTTP
    - `📁 - worker`: Un dossier qui contient uniquement le côté logique de l'API, il est dans l'obligation de traduire les erreurs de la base de données avec ses propres exceptions
        - `📁 - <nom-module>`: Un dossier qui portera un nom logique en relation avec votre service
            - `📁 - models`: Un dossier qui contient uniquement les DTO (Data transfert object)
            - `📁 - use_case`: Un dossier qui contient la partie logique de l'API
- `📁 - database`: Un dossier qui contient uniquement le code qui permet de faire des requêtes vers la base de données
    - `📄 - schemas.py`: Un fichier qui contient uniquement des dataclasses où les données correspondent aux tables SQL
    - `📁 - interfaces`: Un dossier qui permet d'avoir la possibilité de recoder les fonctions selon les environnements.
    - `📁 - repositories`: Un dossier qui contient uniquement le code qui permet les requêtes vers la base de données
- `📁 - mocks`: Un dossier qui contient uniquement des classes qui se comportent comme une base de données
- `📁 - test`: Un dossier qui contient le code des tests unitaire de l'API
    - `📁 - <nom-module>`: Un dossier qui portera un nom logique en relation avec la partie que vous tester

## Comment lancer l'API manuellement
Vous devez vous placez a la racine du projet, la base de la commande sera :
```
PYTHONPATH=`pwd` python3 src/main.py
```
Mais cette base ne permet pas de faire fonctionner l'API, vous devez set des variables d'environnement supplémentaires :
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
```
PYTHONPATH=`pwd` \
API_MODE=TEST \
API_PORT=5000 \
python3 src/main.py
```
### Commande pour lancer l'API en mode `PROD`
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

## Image Docker
### Variable d'environment 
- `API_NAME`
- `API_PORT`
- `API_MODE`, valeurs possibles :
    - `PROD`
    - `TEST`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PWD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
### Comment execute l'image ?
Pour lancer l'image Docker à partir de votre machine, vous devez tout d'abord `pull` l'image :
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

## Lancer une base de données local
### Vierge
Nous avons notre propre repo sur Github qui contient un package où il y a une image docker heberger. Il contient un script d'initialisation et des données de test dès l'initialisation de la base de données (Vous avez rien à faire en quelque sorte).

Il vous suffit d'un premier temps de pull l'image docker sur votre machine :
```
docker pull ghcr.io/dut-info-montreuil/sae-5.a-carmate-database:latest
```
et d'ensuite run l'image
```
docker run \
    -p 5432:5432 \
    ghcr.io/dut-info-montreuil/sae-5.a-carmate-database:latest
```
### Avec fixtures
Au sein du projet, il y a un dossier du nom de `postman` qui contient un `docker-compose`.
Vous pouvez utiliser celui-ci pour avoir les fixtures dans la base de donnée
```
docker compose -f "postman/docker-compose.yaml" up db
```

Le nom de la base de données héberger correspond au nom d'utilisateur par defaut.
Le `POSTGRES_USER` par defaut est postgres et son password est postgres

## Lancer les tests unitaire
Placez-vous dans le dossier `src` et faite cette commande
```
API_MODE=TEST python -m unittest discover -s ../test
```
