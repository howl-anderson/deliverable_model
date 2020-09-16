import os
import shutil
from collections import namedtuple
from pathlib import Path
import typing
from typing import List, Any, Callable

from deliverable_model import utils
from deliverable_model.converter_base import ConverterBase
from deliverable_model.request import Request
from deliverable_model.response import Response

if typing.TYPE_CHECKING:
    from deliverable_model.response import Response

ModelInfo = namedtuple("ModelInfo", ["type", "store_dir"])


class SimpleConverterForRequest(ConverterBase):
    def call(self, request: Request):
        return request.query


simple_converter_for_request = SimpleConverterForRequest()


class SimpleConverterForResponse(ConverterBase):
    def call(self, response: Response):
        return response.data


simple_converter_for_response = SimpleConverterForResponse()


class ModelBuilder(object):
    version = "1.0"

    def __init__(self):
        self.model: ModelInfo = None
        self.dependency = ["tensorflow<2.0"]
        self.custom_object_dependency = []

        self.converter_for_request: Callable[[Request], Any] = (
            simple_converter_for_request
        )
        self.converter_for_response: Callable[[Any], Response] = (
            simple_converter_for_response
        )

    def add_keras_h5_model(self, model_dir):
        if self.model:
            raise ValueError()

        self.model = ModelInfo("keras_h5_model", model_dir)

    def add_tensorflow_saved_model(self, model_dir: str):
        if self.model:
            raise ValueError()

        # model_dir is dir to model, we need a timestamp versioned model info
        timestamp_versioned_model_dir = os.path.dirname(model_dir)

        self.model = ModelInfo("tensorflow_saved_model", timestamp_versioned_model_dir)

    def add_keras_saved_model(self, model_dir):
        if self.model:
            raise ValueError()

        self.model = ModelInfo("keras_saved_model", model_dir)

    def add_dummy_model(self, model_dir):
        if self.model:
            raise ValueError()

        self.model = ModelInfo("dummy_model", model_dir)

    def add_converter_for_request(self, func: Callable):
        self.converter_for_request = func

    def add_converter_for_response(self, func: Callable):
        self.converter_for_response = func

    @staticmethod
    def _dump_converter(func: Callable) -> dict:
        return {
            "class_name": utils.get_class_fqn_name(func),
            # TODO this function not exist
            "config": func.get_config(),
        }

    def save(self):
        self.build = True

    def serialize(self, asset_dir: Path):
        output_dir = asset_dir / self.model.type

        shutil.copytree(self.model.store_dir, output_dir)

        return {
            "version": self.version,
            "type": self.model.type,
            "custom_object_dependency": self.custom_object_dependency,
            "converter_for_request": self._dump_converter(self.converter_for_request),
            "converter_for_response": self._dump_converter(self.converter_for_response),
        }

    def get_dependency(self):
        return self.dependency

    def set_dependency(self, dependency: List[str]):
        self.dependency = dependency

    def append_dependency(self, dependency: List[str]):
        self.dependency = self.dependency + dependency

    def set_custom_object_dependency(self, dependency: List[str]):
        self.custom_object_dependency = dependency
