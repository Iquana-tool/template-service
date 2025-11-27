from models.model_registry import ModelRegistry, ModelInfo, ModelLoader
from paths import *


def register_models(model_registry: ModelRegistry):
    """ This function registers all models in the MODEL_REGISTRY. You can extend it to add custom models. """
    model_registry.register_model(
        ModelInfo(
            identifier_str="example",
            name="An example model",
            description="A model meant to show you how to register your own models.",
            tags=["Add", "your", "tags", "here", "eg. Slow inference"],
            supports_refinement=False,
        ),
        ModelLoader(
            loader_function=lambda: None
        )
    )