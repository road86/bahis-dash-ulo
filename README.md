# BAHIS Dashboard

## Local Installation

First [install pipenv](https://pipenv.pypa.io/). If you installed pipenv using `sudo apt install pipenv` and [getting this error](https://github.com/pypa/pipenv/issues/5133) install using `pip` instead.

1. `pipenv install`
2. copy data from `bahis-data/output/` to `exported_data`

If you get an error when running install like this:

```bash
Resolving dependencies...
✘ Locking Failed!
```

remove the `Pipfile.lock` file and run again.

## Local development

Run `pipenv run python app.py`. (If you get a `Permission denied` error you may need to run as `sudo`)

This will run a development server with hot reloading and other useful features.

## Deployment

To run the system in a local "deployment" you can use the Dockerfile with `docker build -t dash . && docker run -p 80:80 dash:latest`.

Cloud deployment is done (currently manually) using bahis-infra. Only the latest release will be deployed - releases are created automatically when a PR is successfully merged into `main`.
