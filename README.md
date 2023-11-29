# Projet CARMATE
## Sommaire
- [Image Docker](#image-docker)
    - [Variable d'environment](#variable-denvironment)
    - [Comment execute l'image](#comment-execute-limage)
- [Endroit pratique pour le development](#endroit-pratique-pour-le-development)

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
docker pull ghcr.io/dut-info-montreuil/sae-5.a-carmate-back:master
```
Ensuite, lancez l'image Docker :
```
docker run \
    --env API_PORT=5000
    --env API_MODE=TEST \
    --name carmate-back \
    -p 5432:5432 \
    -d ghcr.io/dut-info-montreuil/sae-5.a-carmate-back:master
```

## Endroit pratique pour le development
Un `CODESTYLE` est disponible [ici](/docs/CODESTYLE.md)

Un `HOWTO` est disponible [ici](/docs/HOWTO.md)

Un `DEVELOPMENT` est disponible [ici](/docs/DEVELOPMENT.md)
