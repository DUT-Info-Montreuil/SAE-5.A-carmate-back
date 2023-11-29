# Comment faire ?
## Sommaire
- [Getting started](#getting-started)
- [Comprendre la séparation du code dans le projet]()
- [Comprendre la traduction et les differentes couche d'erreurs](#comprendre-la-traduction-et-les-differentes-couche-derreurs)
- [Faire un controller](#faire-un-controller)
    - [Qu'est-ce que c'est ?](#quest-ce-que-cest)
    - [Creation d'une route](#creation-dune-route)
    - [Ajouter la route dans le fichier `main.py`](#ajouter-la-route-dans-le-fichier-mainpy)
- [Faire un worker](#faire-un-worker)
    - [Qu'est-ce que c'est ?](#quest-ce-que-cest-1)
    - [Crée mon objet "worker"](#crée-mon-objet-worker)
    - [Crée vos models](#crée-vos-models)
- [Faire un repository](#faire-un-repository)
    - [Qu'est-ce que c'est ?](#quest-ce-que-cest-2)
    - [Crée un repository](#crée-un-repository)
    - [Qu'est-ce que c'est le `schemas.py` ?](#quest-ce-que-cest-le-schemapy)
- [Faire un test unitaire](#faire-un-test-unitaire)
    - [Mockito](#mockito)
        - [Qu'est-ce que c'est ?](#quest-ce-que-cest-3)
        - [Crée un mock](#crée-un-mock)
    - [unittest](#unittest)

## Getting started
Ce fichier permet vous developer de savoir implementer des classes, interfaces, ect au sain du projet

Avant tous de chose, pour avoir une idée clair de la structure vous pouvez vous rendre [ici](/docs/DEVELOPMENT.md)

## Comprendre la séparation du code dans le projet
- `src` : Le code source du projet
- `controller` : Contient uniquement des déclarations de route et verifie si la données recus est correct avant d'envoyer les données dans le `worker`
- `worker` : Contient uniquement des classes avec une fonction `worker` qui permet de codé la partie logique du code
- `database` : Toute les requêtes vers une base donnée que vous voulez faire doivent se retrouver ici
- `test` : Le code qui correspond au test unitaire des workers
- `mock` : Doit contenir uniquement les mockitos de la base de donnée

## Comprendre la traduction et les differentes couche d'erreurs
Nous avons trois couche d'erreur dans notre API:
- Erreur de la base de donnée (`database/exceptions.py`)
- Erreur du worker (`api/exceptions.py`)
- Erreur du controler

Chaque erreur qui provienne d'une librairie externe, d'une librairie native ou quelque soit l'erreur vous devez obligatoirement la traduire avec une exception qu'on a crée (ou que vous allez crée) dans l'API !

Exemple:
- dans `database/repositories/` => Erreur PostgreSQL -> traduit en erreur géré par nous
```python
# * repository file *
try:
    # query executed here
except lookup(errorcodes.UNIQUE_VIOLATION) as e:    # Error in psycopg2
    raise UniqueViolation(e)                        # Error in database/exception.py
except lookup(errorcodes.INTERNAL_ERROR) as e:      # Error in psycopg2
    raise InternalServer(e)                         # Error in database/exception.py
except Exception as e:                              # Catch all other exceptions
    raise InternalServer(e)                         # Error in database/exception.py
```
Le fichier qui contient les exceptions est dans `database/exceptions.py`

- dans `api/worker/` => Erreur base de donnée -> traduit en erreur géré par nous
```python
# * worker file *
user: UserTable
try:
    user = self.user_repository.insert(credential)
except UniqueViolation as e:        # Error in database
    raise AccountAlreadyExist()     # Error in api/exception.py
except InternalServer as e:         # Error in database
    raise InternalServerError()     # Error in api/exception.py
except Exception as e:              # Catch all other exceptions
    raise InternalServerError()     # Error in api/exception.py
```
Le fichier qui contient les exceptions est dans `api/exceptions.py`

- dans `api/controller` => Erreur worker -> traduit en erreur HTTP géré par vous
```python
# * controller file *
try:
    # call worker here
except AccountAlreadyExist:     # Error in api/exception.py
    abort(409)                  # Error in HTTP code
except LengthNameTooLong:       # Error in api/exception.py
    abort(400)                  # Error in HTTP code
except InternalServerError:     # Error in api/exception.py
    abort(500)                  # Error in HTTP code
except Exception:               # Catch all other exceptions
    abort(500)                  # Error in HTTP code
```

## Faire un controller
### Qu'est-ce que c'est ?
Le controller est un dossier qui contient toute les routes de l'API.

Les routes ne doivent contenir aucune logique mais doit quand même verifier si la donnée entrée est correct ou non avant d'appeler le `worker`

Il doit traduit les erreurs provenant du `worker` par des `abort(<HTTPCode>)` (Comprendre les couches d'erreur [ici](#comprendre-la-traduction-et-les-differentes-couche-derreurs))
### Creation d'une route
Placez-vous dans le dossier contrôleur et nommé vous un dossier qui correspond au nom de votre module, exemple:
```
📁 - src
^
| 📁 - api
|  ^
|  | 📁 - controller
|  |  ^
|  |  | 📄 - driver.py
```
Je vien de nommé un fichier qui porte le nom de mon module qui est driver où le fichier va contenir les routes associé uniquement a ce module

Dans ce dossier, vous allez donc declarer les routes comme ci-dessous :
```python
class DriverRoutes(Blueprint):
    driver_repository: DriverRepositoryInterface

    def __init__(self,
                 driver_repository: DriverRepositoryInterface):
        super(DriverRoutes, self).__init__("driver", __name__,
                                           url_prefix="/driver")
        
        self.driver_repository = driver_repository

        self.route("/exemple",
                   methods=["GET"])(self.exemple_api)

    def exemple_api(self) -> Response:
        return "I'm an exemple", 200
```
Dans cet exemple, je declare un [Blueprint](https://flask.palletsprojects.com/en/2.3.x/blueprints/) (Pour vulgarisé, vous etes obliger de crée un Blueprint lorsque vous séparer les routes du main), la classe [Blueprint](https://flask.palletsprojects.com/en/2.3.x/blueprints/) s'initie avec ses valeurs
```python
class flask.Blueprint(
    name, 
    import_name, 
    static_folder=None, 
    static_url_path=None, 
    template_folder=None, 
    url_prefix=None, 
    subdomain=None, 
    url_defaults=None, 
    root_path=None, 
    cli_group=<object object>
)
```
source: https://flask.palletsprojects.com/en/2.3.x/api/#blueprint-objects

Uniquement `name`, `import_name` et `url_prefix` sera le plus utilisé dans notre API.

L'argument `driver_repository` sera le repository qu'on passera dans le `main.py` lors de l'ajout de la route dans la fonction `register_blueprint`.

### Ajouter la route dans le fichier `main.py`
Le fichier `main.py` a l'initialisation du projet ressemble à cela :
```python
from flask import Flask


class Api(object):
    """
    All property about the API
    """
    api = Flask(__name__)
    port = 5000
    host = '0.0.0.0'

    driver_repository: DriverRepositoryInterface

    def __init__(self) -> None:
        match os.getenv("API_MODE"):
            case "PROD":
                self.postgres()
            case "TEST":
                self.mock()
            case None:
                raise Exception("API_MODE must be set !")
            case _:
                raise Exception(f"Value error in API_MODE ({os.getenv('API_MODE')} invalid)")

        # add routes
        # self.api.register_blueprint()
        self.api.register_blueprint(DriverRoutes(self.driver_repository))

    def mock(self) -> None:
        self.driver_repository = InMemoryDriverRepository()

    def postgres(self) -> None:
        self.driver_repository = DriverRepository()

    def run(self) -> None:
        self.api.run(port=self.port, host=self.host)


Api().run()
```
Un commentaire est déjà prevu a cet effet pour ajouter votre route dans le fichier `main.py`. Il vous suffit juste de prendre `self.api.register_blueprint()` et ajouter votre classe que vous avez crée (dans mon exemple elle se nomme `DriverRoutes`) en argument de la fonction.

Selon vos besoin, vous devez ajoutez des variables dans `mock` et `postgres` selon les routes que vous ajouté dans la fonction `register_blueprint`.

## Faire un worker
### Qu'est-ce que c'est ?
Le worker est uniquement là pour contenir la partie logique de l'API (conditions, traitements, ...)
### Crée mon objet "worker"
Placez-vous dans le dossier worker et nommé vous un dossier qui correspond au nom de votre module, exemple:
```
📁 - src
^
| 📁 - api
|  ^
|  | 📁 - worker
|  |  ^
|  |  | 📁 - driver
```
Une fois le dossier crée, vous devez obligatoirement crée 3 autres dossiers qui portera le nom `interfaces`, `models` et `use_case`.
```
📁 - src
^
| 📁 - api
|  ^
|  | 📁 - worker
|  |  ^
|  |  | 📁 - driver
|  |  |  ^
|  |  |  | 📁 - interfaces
|  |  |  | 📁 - models
|  |  |  | 📁 - use_case
```
Une explication détaillé des dossiers est disponible [ici](/docs/DEVELOPMENT.md)

Lorque les 3 dossiers on été crée, vous pouvez commencez a mettre votre partie logique du code dans `use_case`, exemple : 
```
📁 - src
^
| 📁 - api
|  ^
|  | 📁 - worker
|  |  ^
|  |  | 📁 - driver
|  |  |  ^
|  |  |  | 📁 - interfaces
|  |  |  | 📁 - models
|  |  |  | 📁 - use_case
|  |  |  |  ^
|  |  |  |  | 📄 - driver.py
```
Le nom du fichier `driver.py` sera probablement diffèrent, vous êtes libre a ce niveau là tant que cela reste cohérent

Dans ce fichier que j'ai nommé `driver.py` vous allez ecrire une classe comme si dessous :
```python
class Driver(object):
    driver_repository: DriverRepositoryInterface

    def __init__(self, driver_repository: DriverRepositoryInterface):
        self.user_repository = user_repository

    def worker(self):
        pass
```
_Cette classe n'est qu'un exemple, copier coller de manière intelligente !_

Vous vous dites "bordel pourquoi il y a Repository machin Interface !?", c'est comprehensible :)

Nous devons avoir ca en paramètre de la classe car cela sera utilise dans le mock. Ces interfaces permet de changer la maniere de stocker des données selon les environments. Par exemple côté Mock on aura `InMemoryDriverRepository` qui hérite de l'interface `DriverRepositoryInterface` en argument et dans le contrôler on aura plutôt `DriverRepository` en argument.

### Crée vos models
Les models dans le worker represente les données qui vont transitionner entre votre route et le worker, on les nommes des DTO

Placez-vous dans le dossier worker/models et nommé vous un ficher qui correspond au nom de votre donnée qui va transiter, exemple:
```
📁 - src
^
| 📁 - api
|  ^
|  | 📁 - worker
|  |  ^
|  |  | 📁 - driver
|  |  |  ^
|  |  |  | 📁 - interfaces
|  |  |  | 📁 - models
|  |  |  |  ^
|  |  |  |  | 📄 - driver_dto.py
|  |  |  | 📁 - use_case
```

Exemple d'un DTO :
```python
# * driver_dto.py *
from dataclasses import dataclass


@dataclass(frozen=True)
class DriverDTO:
    id: int
    first_name: str
    last_name: str

    @staticmethod
    def to_self(_tuple: tuple) -> Self:
        return UserTable(
            _tuple[0],
            _tuple[1],
            _tuple[2]
        )
```
Les DTO doivent être en capacité de ce traduire en plusieurs format utile dans notre API, comme par exemple une fonction `self_to_json()` qui permet de traduire ses données vers un format `json`


## Faire un repository
### Qu'est-ce que c'est ?
Le repository est destiné uniquement au requête vers la base de données, il doit toujours hériter obligatoirement d'une interface
### Crée un repository
Placez-vous dans le dossier database/repositories et nommé vous un ficher qui correspond au nom de la table que vous ciblé pour faire des opérations, exemple:
```
📁 - src
^
| 📁 - database
|  ^
|  | 📁 - repositories
|  |  ^
|  |  | 📄 - driver_repository.py
```

Exemple d'un repository :
```python
# * driver_repository.py *
class DriverRepositoryInterface(ABC):
    def insert(id: int) -> DriverTable: ...


class DriverRepository(DriverRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "driver"

    def insert(self, id: int) -> DriverTable:
        # request and insert here thanks to psycopg2
        pass
```

L'interface et le repository doit être dans le même fichier pour évité le circular import de Python t___t
### Qu'est-ce que c'est le `schemas.py` ? 
Dans `database`, le fichier `schemas.py` represente les tables SQL dans la base de donnée, exemple d'un script qui crée une table user :
```sql
CREATE TABLE "user" (
    id                  SERIAL          PRIMARY KEY,
    first_name          VARCHAR(255)    NOT NULL,
    last_name           VARCHAR(255)    NOT NULL
);
```
Representation de la table en objet dans `schemas.py` :
```python
@dataclass(frozen=True)
class UserTable:
    id: int
    first_name: str
    last_name: str

    @staticmethod
    def to_self(_tuple: tuple) -> Self:
        return UserTable(
            _tuple[0],
            _tuple[1],
            _tuple[2]
        )
```

Il doit être utilisé en valeurs de retour des fonctions dans les repositories.

## Faire un test unitaire
### Mockito
#### Qu'est-ce que c'est ?
Un mockito recopie **bêtement** le comportement d'une base de données, il doit toujours implementé une interface qui correspond a l'interface utiliser dans vos repositories.

#### Crée un mock
Placez-vous dans le dossier tests/mock et nommez vous un ficher qui aura toujours comme prefix `InMemory` suivie du nom de votre repository, exemple :
```
📁 - test
^
| 📁 - mock
|  ^
|  | 📁 - user
|  |  ^
|  |  | 📄 - in_memory_user_repository.py
```

Exemple d'un mock :
```python
class InMemoryUserRepository(UserRepositoryInterface):
    def __init__(self):
        self.users: List[UserTable] = []
        self.users_counter = 0

    def insert(self, info: UserDTO) -> UserTable:
        first_name, last_name = info.to_json().values()
        in_memory_user = UserTable.to_self((InMemoryUserRepository.users_counter, first_name, last_name))
        self.users.append(in_memory_user)
        self.users_counter = self.users_counter + 1
        return in_memory_user
```
Il doit toujours avoir une liste de schema et d'autre variables utile pour simuler d'autre comportement de la DB comme l'auto-increment, ect...

### unittest 
Documentation officiel de `unittest` : https://docs.python.org/3/library/unittest.html

Le nom du fichier Python doit obligatoirement commencer par `test_...`, sinon le CI/CD dans Github qui lance les tests unitaire ne pourra detecter le fichier ou la commande `python3 -m unittest discover tests` ne pourra pas voir les fichiers de test.

Exemple d'un test unitaire :
```python
import unittest


class DummyTestCase(unittest.TestCase):
    def test_dummy(self):
        with self.assertRaises(Exception):
            Dummy.worker()
```
La classe qui contient les fonctions de test doit obligatoirement hériter de `unittest.TestCase`.

Les fonction doivent aussi commencer par `test_...` pour qu'il soit detecter par la librairie `unittest`.
Comme en Java, il y a les fonction `assertXxxx`
