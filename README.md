# Template Repository
This is a template repository meant to be used to add new services to the coral annotation tool. You can copy this repository to implement your own service to the tool. 
>[!IMPORTANT]
> With this repo you can only implement your own service to run on its own. To be able to use it in the annotation tool, you still need to add it to the main API and depending on your service the frontend (to add the needed inputs). 
## Installation & Packages
This repository is built with [uv](https://docs.astral.sh/uv/). I recommend using uv to install and manage dependencies. Just run the following and you are good to go:
```shell
uv sync
```
Adding a new package is as easy as running:
```shell
uv add numpy
```
or
````shell
uv pip install numpy
````
> [!TIP]
> If you need more complex setup options like installing from a repo, consider dockerizing.
## Structure
This template services uses [FastAPI](https://fastapi.tiangolo.com) for routing and managing HTTP endpoints. FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.
You can see the docs, when you run the API:
```shell
uv run fastapi run main.py
```

Each service is its own API in the coral setup, accepting (and sending) requests. In general, a lot of services implement the same functionality, hence this repo is meant to make creating a new service easier by supplying a skeleton with most functionalities implemented.

### Where to find what
All **endpoints** can be found under [app/routes](app/routes). An endpoint to check whether the service is running, is defined in [app/routes/\_\_init__.py](app/routes/__init__.py).

[Pydantic](https://docs.pydantic.dev/latest/) schemas should be added under [app/schemas](app/schemas). These help you to define data classes easily. You can directly pass them to fastapi routes and they are json serializable.

**Caches and persistent memory** should be added to [app/state.py](app/state.py). 

The **app creator** function can be found under [app/\_\_init\_\_.py](app/\_\_init\_\_.py). You need to add new routers here, if you create any.

**Utility functionality** should be added under [util](util). It already contains an image cache and loading functionality.

Any functionality regarding **models** should be added under [models](models). This folder already contains a bunch of .py files. Notably, a base model class, a registry, a cache and a register script.

## Workflow and Endpoints
The workflow for most inference related tasks, where users want to run some model on an image, is as follows:
1. Upload this image to the service.
2. Select a model to use.
3. Run inference with some parameters.

In the following are all endpoints in more detail.
### Uploading an image
Uploading an image is straight forward. Images are kept in a cache such that users do not have to upload before every inference (as a key the cache uses their username).
- `open_image`: Upload an image to be used in the current session.
- `focus_crop`: Only use a crop of the image instead of the entire image for the current session.
- `unfocus_crop`: Use the whole image again for this session.
- `close_image`: Remove an image from the Image cache.
>[!IMPORTANT] 
> Notice how we have a normal `router` and a `session_router`. The `session_router` is meant to be used for anything related to an active annotation session. The normal `router` can be used for everything else.

### Selecting a model
Before you run inference you need to select a model, which you want to use. This is intentionally separated from the actual inference call, as users might choose the model way before actually choosing to send a request. Giving the backend time to preload the model.
- `list_models`: Get a list of all available (and loadable) models. This is important for the main API to give the user a list of possible models.
- `load_model`: Load a model into the model cache, such that the user can later on use it.
#### Model Registry
There is a model registry, which is initialized on startup. You can register models to the register by editing the [registration function](models/register_models.py). 
Each model has a loader component and an info component. The loader is responsible for correctly loading the model into memory. The info component just holds some information about the model.
### Inference
If image and model are selected and loaded, you can run inference. This endpoint does not come with predefined functionality. You need to implement it yourself!
