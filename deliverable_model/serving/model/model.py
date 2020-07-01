import importlib
import logging
from pathlib import Path
from typing import Any, Callable, List

from deliverable_model.request import Request
from deliverable_model.response import Response
from deliverable_model.serving.model.model_loaders.model_loader_base import (
    ModelLoaderBase,
)
from deliverable_model.serving.model.model_loaders.model_registry import (
    get_model_loader_instance_by_type,
)
from deliverable_model.utils import class_from_module_path


logger = logging.getLogger(__name__)


class Model(object):
    def __init__(
        self,
        model_loader_instance: ModelLoaderBase,
        converter_for_request: Callable[[Request], Any],
        converter_for_response: Callable[[Any], Response],
    ):
        self.model_loader_instance = model_loader_instance

        self.converter_for_request = converter_for_request
        self.converter_for_response = converter_for_response

    @classmethod
    def load(cls, asset_dir: Path, metadata) -> "Model":
        # load custom dependency to trigger auto registry for keras
        cls._load_custom_object_dependency(metadata["custom_object_dependency"])

        model_type = metadata["type"]
        model_loader_instance = get_model_loader_instance_by_type(
            model_type, asset_dir, metadata
        )

        converter_for_request = cls._load_converter(metadata["converter_for_request"])
        converter_for_response = cls._load_converter(metadata["converter_for_response"])

        self = cls(model_loader_instance, converter_for_request, converter_for_response)

        return self

    def inference(self, request: Request) -> Response:
        logger.debug("Converter for request receives request: %s", request)

        args, kwargs = self.converter_for_request(request)
        logger.debug("Converter for request returns: args: %s, kwargs: %s", args, kwargs)

        native_response = self.model_loader_instance.inference(*args, **kwargs)
        logger.debug("Native model responses: %s", native_response)

        response = self.converter_for_response(native_response)
        logger.debug("Converter for response returns: %s", response)

        return response

    @classmethod
    def _load_custom_object_dependency(cls, custom_object_dependency: List[str]):
        """
        import module from a list of object list
        """
        for dependency in custom_object_dependency:
            importlib.import_module(dependency)

    @classmethod
    def _load_converter(cls, config):
        class_ = class_from_module_path(config["class_name"])
        parameter = config.get("config", {})

        class_load_method = getattr(class_, "from_config")

        instance = class_load_method(parameter)

        return instance
