"""
  TS405: Ingest data & pipeline to feature set(s) from SQL source
"""

from qgate_sln_mlrun.ts.tsbase import TSBase
from qgate_sln_mlrun.setup import Setup
import mlrun
import mlrun.feature_store as fstore
from mlrun.data_types.data_types import spark_to_value_type
import pandas as pd
import glob
import os
from tspipeline import TSPipeline
from mlrun.datastore.sources import SQLSource
from qgate_sln_mlrun.helper.mysqlhelper import MySQLHelper


class TS405(TSBase):

    def __init__(self, solution):
        super().__init__(solution, self.__class__.__name__)
        self._mysql = MySQLHelper(self.setup)

    @property
    def desc(self) -> str:
        return "Ingest data & pipeline to feature set(s) from SQL source"

    @property
    def long_desc(self):
        return "Ingest data & pipeline to feature set(s) from SQL source"

    def prepare(self):
        """Prepare data for ingestion"""
        pass

    def prj_exec(self, project_name):
        """Data ingest"""
        for featureset_name in self.get_featuresets(self.project_specs.get(project_name)):
            # create possible file for load
            source_file = os.path.join(os.getcwd(),
                                       self.setup.model_definition,
                                       "02-data",
                                       self.setup.dataset_name,
                                       f"*-{featureset_name}.csv.gz")

            # check existing data set
            for file in glob.glob(source_file):
                self._ingest_data(f"{project_name}/{featureset_name}", project_name, featureset_name, file)

    @TSBase.handler_testcase
    def _ingest_data(self, testcase_name, project_name, featureset_name, file):
        # get existing feature set (feature set have to be created in previous test scenario)
        featureset = fstore.get_feature_set(f"{project_name}/{featureset_name}")

        # add pipelines
        pipeline = TSPipeline(featureset,self.test_setting_pipeline['tests'][featureset_name])
        pipeline.add()

        # save featureset
        featureset.save()

        keys = ""
        for entity in featureset.spec.entities:
            keys+=f"{entity.name},"

        fstore.ingest(featureset,
                      SQLSource(name="tst",
                                table_name=self._mysql.create_helper(project_name, featureset_name),
                                db_url=self.setup.mysql,
                                key_field=keys[:-1].replace('-','_')),
                      # overwrite=False,
                      return_df=False,
                      # infer_options=mlrun.data_types.data_types.InferOptions.Null)
                      infer_options=mlrun.data_types.data_types.InferOptions.default())
        # TODO: use InferOptions.Null with python 3.10 or focus on WSL
        # NOTE: option default, change types
        # NOTE: option Null, generate error with datetime in python 3.9
