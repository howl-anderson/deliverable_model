import copy
import typing
from pathlib import Path
from typing import Dict

from deliverable_model.processor_base import ProcessorBase
from deliverable_model.request import Request
from deliverable_model.response import Response

if typing.TYPE_CHECKING:
    from nlp_utils.preprocess.lookup_table import LookupTable as Lookuper


class LookupProcessor(ProcessorBase):
    def __init__(self, lookup_table=None, **kwargs):
        super().__init__(**kwargs)

        self.lookup_table = lookup_table  # type: "Lookuper"

    @classmethod
    def load(cls, parameter: dict, asset_dir) -> "ProcessorBase":
        from nlp_utils.preprocess.lookup_table import LookupTable as Lookuper

        config = parameter.pop("config", {})

        instance_asset = asset_dir / "data"
        lookup_table = Lookuper.load_from_file(instance_asset, **config)

        self = cls(lookup_table, **parameter)

        return self

    def preprocess(self, request: Request) -> Request:
        query_id_list = []
        for query_item in request[self.pre_input_key]:
            query_item_id = [self.lookup_table.lookup(i) for i in query_item]
            query_id_list.append(query_item_id)

        request[self.pre_output_key] = query_id_list

        return request

    def postprocess(self, response: Response) -> Response:
        data_str_list = []
        for data_int in response[self.post_input_key]:
            data_str = [self.lookup_table.inverse_lookup(i) for i in data_int]
            data_str_list.append(data_str)

        response[self.post_output_key] = data_str_list

        return response

    def get_config(self) -> dict:
        base_config = super().get_config()
        config = self.lookup_table.get_config()

        return {**base_config, **{"config": config}}

    def serialize(self, asset_dir: Path):
        instance_asset = asset_dir / "data"
        self.lookup_table.dump_to_file(instance_asset)

    def get_dependency(self) -> list:
        return ["nlp_utils"]
