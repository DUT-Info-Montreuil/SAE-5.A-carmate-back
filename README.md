# Projet SAE - Carmate
## Sommaire
- [Comment lancer l'API manuellement](#comment-lancer-lapi-manuellement)
    - [Commande pour lancer l'API en mode `TEST`](#commande-pour-lancer-lapi-en-mode-test)
    - [Commande pour lancer l'API en mode `PROD`](#commande-pour-lancer-lapi-en-mode-prod)

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
