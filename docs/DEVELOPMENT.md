# Endroit pratique pour le development
## Sommaire
- [Structure du projet](#structure-du-projet)
- [Lancer une base de données local](#lancer-une-base-de-données-local)
- [Lancer les tests unitaire](#lancer-les-tests-unitaire)

## Structure du projet
```
📁 - src
^
| 📄 - requirements.txt
| 📁 - api
|  ^
|  | 📄 - __init__.py
|  | 📁 - controller
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📄 - user.py
|  |  | 📄 - driver.py
|  |
|  | 📁 - worker
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📁 - user
|  |  |  ^
|  |  |  | 📄 - __init__.py
|  |  |  | 📄 - exceptions.py
|  |  |  | 📁 - interfaces
|  |  |  |  ^
|  |  |  |  | 📄 - __init__.py
|  |  |  |  | 📄 - ...
|  |  |  | 📁 - models
|  |  |  |  ^
|  |  |  |  | 📄 - __init__.py
|  |  |  |  | 📄 - user_dto.py
|  |  |  |
|  |  |  | 📁 - use_case
|  |  |  |  ^
|  |  |  |  | 📄 - __init__.py
|  |  |  |  | 📄 - user.py
|  |  |
|  |  | 📁 - driver
|  |  |  ^
|  |  |  | 📄 - __init__.py
|  |  |  | ...
|
| 📁 - database
|  ^
|  | 📄 - __init__.py
|  | 📄 - schemas.py
|  | 📁 - repositories
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📄 - user_repository.py
|  |  | 📄 - message_repository.py
|  |  | 📄 - ...
|
📁 - test
^
| 📄 - __init__.py
| 📁 - mock
|  ^
|  | 📄 - __init__.py
|  | 📁 - user
|  |  ^
|  |  | 📄 - __init__.py
|  |  | 📄 - in_memory_user_repository.py
|  | 
|  | 📁 - driver
|  |  ^
|  |  | 📄 - __init__.py
|  |  | ...
| 📁 - user
|  ^
|  | 📄 - __init__.py
|  | 📄 - test_send_message.py
|  | 📄 - ...
| 📁 - driver
|  ^
|  | 📄 - __init__.py
|  | 📄 - ...
|
📄 - .gitignore
📄 - Dockerfile
📄 - README.md
```

- `📁 - src`: Un dossier qui contient le code source de l'API
- `📄 - requirements.txt`: Un fichier qui contient les dépendances du projet
- `📁 - api`: Un dossier qui contient uniquement le code qui concerne l'API, toute trace de DB doit être enlevé !
- `📁 - controller`: Un dossier qui contient uniquement les déclarations des routes.
Les routes doivent traduire les erreurs qui proviennent du worker en code d'erreur HTTP
- `📁 - worker`: Un dossier qui contient uniquement le côté logique de l'API, il est dans l'obligation de traduire les erreurs de la base de données avec ses propres exceptions
  - `📁 - <nom-module>`: Un dossier qui portera un nom logique en relation avec votre service
    - `📄 - exceptions.py`: Un fichier qui contient les exceptions que le module peut remonter
    - `📁 - interfaces`: Un dossier qui permets d'avoir la possibilité de recoder les fonctions selon les environnements.
    - `📁 - models`: Un dossier qui contient uniquement les DTO (Data transfert object)
    - `📁 - use_case`: Un dossier qui contient la partie logique de l'API
- `📁 - database`: Un dossier qui contient uniquement le code qui permet de faire des requêtes vers la base de données
    - `📄 - schemas.py`: Un fichier qui contient uniquement des dataclasses où les données correspondent aux tables SQL
    - `📁 - repositories`: Un dossier qui contient uniquement le code qui permet les requêtes vers la base de données
- `📁 - **\📄 - __init__.py`: Un fichier qui définit un module (Peut contenir du code)
- `📁 - test`: Un dossier qui contient le code des tests unitaire de l'API
    - `📁 - mock`: Un dossier qui contient uniquement des classes qui se comporte comme une base de données
    - `📁 - <nom-module>`: Un dossier qui portera un nom logique en relation avec la partie que vous tester

## Lancer une base de données local
Nous avons notre propre repo sur Github qui contient un package où il y a une image docker heberger. Il contient un script d'initialisation et des données de test dès l'initialisation de la base de données (Vous avez rien à faire en quelque sorte).

Il vous suffit d'un premier temps de pull l'image docker sur votre machine :
```
docker pull ghcr.io/dut-info-montreuil/sae-5.a-carmate-database:master
```
et d'ensuite run l'image
```
docker run -p 5432:5432 ghcr.io/dut-info-montreuil/sae-5.a-carmate-database:master
```

Le nom de la base de données héberger correspond au nom d'utilisateur par defaut.
Le `POSTGRES_USER` par defaut est postgres et son password est postgres

## Lancer les tests unitaire
Placez-vous dans le dossier `src` et faite cette commande
```
python3 -m unittest discover test
```
