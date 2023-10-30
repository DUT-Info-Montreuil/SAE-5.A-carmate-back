# Projet CARMATE
## Structure du projet
### Fichier `.gitignore`
Permet d'exclure les dossiers/fichiers qui ne concerne pas le code de l'API
### Dans le dossier `src`:
#### Dossier `handlers`
Permet de déclarer toute les routes de chaque module

__Exemple:__
Vous avez un module `test` dans votre dossier `src` et vous devez déclarer deux route `route1` et la route `route2`.
Pour faire cela, vous devez crée un fichier Python qui porte le nom de votre module dans `handlers` :
```python
# code d'exemple du fichier test dans le dossier handlers
"""
All routes about test here
"""
from flask import Blueprint

test = Blueprint('test', __name__)


@test.route("/route1")
def say_hello() -> (int, str):
    """Say hello"""
    return 200, "hello"


@test.route("/route2")
def do_something() -> (int, str):
    # ...
    return 200, "sucess"
```
#### Dossier `models`
Permet de déclarer toute les classes de type DTO qui sera utilisé dans le code

__Exemple:__
```python
from dataclasses import dataclass

@dataclass
class UserDTO:
    id: int
    login: str
    email_address: str

    def to_json(self) -> str:
        return self.__dict__
```
#### Dossier `<nom-du-module>`
Contien tous le code côté process de la donnée
__Exemple:__
Arborescence du projet:
```
- src
  |- handlers
  |- models
  |- nom-du-module
  |  |- user.py
  |  |- message.py
  |- main.py
  |- tools.py
```
Le `nom-du-module` portera le nom de votre module qui aura toute les fonctions de traitement de la données (Recuperation vers des objets DTO)
#### Fichier `main.py`
Uniquement l'ajout des `Blueprint` et des informations qui concerne le lancement de l'API
#### Fichier `tools.py`
Fichier qui contient des fonctions qui sont utilisé partout voir presque partout dans le code