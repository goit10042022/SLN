import mlrun
import mlrun.feature_store as fstore
from mlrun.features import Feature
from mlrun.data_types.data_types import spark_to_value_type
from mlrun.datastore import ParquetTarget,CSVTarget
import json
import glob
import os
import pandas as pd
import shutil
from qgate.setup import Setup
from qgate.uc.ucbase import UCBase

class Solution:
    """Create solution"""

    def __init__(self, setup: Setup):
        """ Init

        :param setup:   Setup for the solution
        """
        self._setup=setup
        self._projects=[]
        self._project_specs={}

    def create_projects(self, uc: UCBase):
        """ Create projects

        :param uc:      Use case
        """
        uc.loghln()
        uc.new_usecase()
        dir=os.path.join(os.getcwd(), self.setup.model_definition, "01-model", "01-project", "*.json")
        for file in glob.glob(dir):
            with (open(file, "r") as json_file):
                json_content = json.load(json_file)
                name, desc, lbls, kind=self._get_json_header(json_content)

                # create project
                uc.log("\t{0} ... ", name)
                uc.usecase_detail(f"{name}")
                self._projects.append(name)
                prj=mlrun.get_or_create_project(name, context="./", user_project=False)
                prj.description=desc
                for lbl in lbls:
                    prj.metadata.labels[lbl]=lbls[lbl]
                prj.save()
                self._project_specs[name] = json_content['spec']
                uc.logln("DONE")
                uc.usecase_state("DONE")

    def delete_projects(self, uc: UCBase):
        """
        Delete projects

        :param uc:      Use case
        """
        uc.loghln()
        uc.new_usecase()
        for project_name in self._projects:
            uc.log("\t{0} ... ", project_name)
            uc.usecase_detail(project_name)

            # delete project
            mlrun.get_run_db().delete_project(project_name, "cascade")

            # delete project in FS
            project_dir=os.path.join(self.setup.model_output, project_name)
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir, True)

            uc.logln("DONE")
            uc.usecase_state("DONE")

        # delete other things (generated from e.g. CSVTargets)
        dir = os.path.join(os.getcwd(), self.setup.model_output, "*")
        for file in glob.glob(dir):
            if os.path.isdir(file):
                shutil.rmtree(file, True)


    def _has_featureset(self, name, project_spec):
        # Support two different collections
        if isinstance(project_spec, dict):
            return name in project_spec["feature-sets"]
        elif isinstance(project_spec, list):
            return name in project_spec
        else:
            raise Exception("Unsupported type")

    def _get_featuresets(self, project_spec):
        # Support two different collections
        if isinstance(project_spec, dict):
            return project_spec["feature-sets"]
        elif isinstance(project_spec, list):
            return project_spec
        else:
            raise Exception("Unsupported type")

    def _get_featurevectors(self, project_spec):
        # Support two different collections
        if isinstance(project_spec, dict):
            return project_spec["feature-vectors"]
        return []


    def create_featureset(self, uc: UCBase):
        """ Get or create featuresets

        :param uc:      Use case
        """
        uc.loghln()
        uc.new_usecase()
        for project_name in self._projects:

            # TODO: change iteration base on feature vector (it is faster way)
            dir=os.path.join(os.getcwd(), self.setup.model_definition, "01-model", "02-feature-set", "*.json")
            for file in glob.glob(dir):

                # iterate cross all featureset definitions
                with open(file, "r") as json_file:
                    json_content = json.load(json_file)
                    name, desc, lbls, kind=self._get_json_header(json_content)

                    if kind=="feature-set":
                        if self._has_featureset(name, self._project_specs[project_name]): # build only featuresets based on project spec
                            uc.log('\t{0}/{1} create ... ', project_name, name)
                            uc.usecase_detail(f'{project_name}/{name} create')

                            # create feature set only in case not exist
                            try:
                                fstore.get_feature_set(f"{project_name}/{name}")
                            except:
                                self._create_featureset(project_name, name, desc, json_content['spec'])
                            uc.logln("DONE")
                            uc.usecase_state("DONE")

    def create_featurevector(self, uc: UCBase):
        # https://docs.mlrun.org/en/latest/api/mlrun.feature_store.html#mlrun.feature_store.FeatureVector

        uc.loghln()
        uc.new_usecase()
        for project_name in self._projects:
            for featurevector_name in self._get_featurevectors(self._project_specs[project_name]):
                # create file with definition of vector
                source_file = os.path.join(os.getcwd(),
                                           self.setup.model_definition,
                                           "01-model",
                                           "03-feature-vector",
                                           f"*-{featurevector_name}.json")

                # check existing data set
                for file in glob.glob(source_file):
                    uc.log("\t{0}/{1} ... ", project_name, featurevector_name)
                    uc.usecase_detail(f"{project_name}/{featurevector_name}")

                    # iterate cross all featureset definitions
                    with open(file, "r") as json_file:
                        json_content = json.load(json_file)
                        name, desc, lbls, kind = self._get_json_header(json_content)

                        # create feature vector only in case not exist
                        try:
                            fstore.get_feature_vector(f"{project_name}/{name}")
                        except:
                            self._create_featurevector(project_name, featurevector_name, desc, json_content['spec'])

                    uc.logln("DONE")
                    uc.usecase_state("DONE")

    def ingest_data(self, uc: UCBase):
        """
        Data ingest

        :param uc:  Use case
        """
        uc.loghln()
        uc.new_usecase()
        for project_name in self._projects:
            for featureset_name in self._get_featuresets(self._project_specs[project_name]):
                # create possible file for load
                source_file=os.path.join(os.getcwd(),
                                         self.setup.model_definition,
                                         "02-data",
                                         self.setup.data_size,
                                         f"*-{featureset_name}.csv.gz")

                # check existing data set
                for file in glob.glob(source_file):
                    uc.log("\t{0}/{1} ... ", project_name, featureset_name)
                    uc.usecase_detail(f"{project_name}/{featureset_name}")

                    # get existing feature set (feature set have to be created in previous use case)
                    featureset = fstore.get_feature_set(f"{project_name}/{featureset_name}")

                    # ingest data with bundl/chunk
                    for data_frm in pd.read_csv(file,
                                             sep=";",
                                             header="infer",
                                             decimal=",",
                                             compression="gzip",
                                             encoding="utf-8",
                                             chunksize=10000):
                        fstore.ingest(featureset,
                                      data_frm,
                                      #overwrite=False,
                                      return_df=False,
                                      infer_options=mlrun.data_types.data_types.InferOptions.Null)
                    uc.logln("DONE")
                    uc.usecase_state("DONE")

    @property
    def setup(self) -> Setup:
        return self._setup

    def _create_featurevector(self, project_name, featurevector_name, featurevector_desc, json_spec):
        # switch to proper project if the current project is different
        if mlrun.get_current_project().name != project_name:
            mlrun.load_project(name=project_name, context="./", user_project=False)

        features = json_spec['features']

        # create feature vector
        vector = fstore.FeatureVector(featurevector_name, features, description=featurevector_desc)
        vector.save()


    def _create_featureset(self, project_name, featureset_name, featureset_desc, json_spec):
        """
        Create featureset based on json spec

        :param project_name:        project name
        :param featureset_name:     feature name
        :param featureset_desc:     feature description
        :param json_spec:  Json specification for this featureset
        """

        # switch to proper project if the current project is different
        if mlrun.get_current_project().name != project_name:
            mlrun.load_project(name=project_name, context="./", user_project=False)

        fs = fstore.FeatureSet(
            name=featureset_name,
            description=featureset_desc,
            relations=json_spec.get('relations')
        )

        # define entities
        for item in json_spec['entities']:
            fs.add_entity(
                name=item['name'],
                value_type=spark_to_value_type(item['type']),
                description=item['description']
            )

        # define features
        for item in json_spec['features']:
            fs.add_feature(
                name=item['name'],
                feature=Feature(
                    value_type=spark_to_value_type(item['type']),
                    description=item['description']
                )
            )

        # define targets
        count=0
        target_providers=[]
        for target in json_spec['targets']:
            target_name = f"target_{count}"
            if target.lower().strip()=="parquet":
                # support more parquet targets (each target has different path)
                target_providers.append(ParquetTarget(name=target_name, path=os.path.join(self.setup.model_output, project_name, target_name)))
            elif target.lower().strip()=="csv":
                target_providers.append(CSVTarget(name=target_name, path=os.path.join(self.setup.model_output, project_name, target_name,target_name+".csv")))
            else:
                # TODO: Add support other targets for MLRun CE e.g. RedisTarget
                raise NotImplementedError()
            count+=1
        fs.set_targets(target_providers, with_defaults=False)

        fs.save()
        return fs

    def _get_json_header(self, json_content):
        """ Get common header

        :param json_content:    json content
        :return:                name, description, labeles and kind from header
        """
        name = json_content['name']
        desc = json_content['description']
        kind = json_content['kind']

        # optional labels
        lbls = None if json_content.get('labels') is None else json_content.get('labels')
        return name, desc, lbls, kind

    def get_data_offline(self, uc: UCBase):
        """
        Get data from off-line feature vector
        """
        uc.loghln()
        for project_name in self._projects:
            for featurevector_name in self._get_featurevectors(self._project_specs[project_name]):

                uc.log("\t{0}/{1} ... ", project_name, featurevector_name)

                if mlrun.get_current_project().name != project_name:
                    mlrun.load_project(name=project_name, context="./", user_project=False)

                vector = fstore.get_feature_vector(f"{project_name}/{featurevector_name}")

                resp = fstore.get_offline_features(vector)
                frm=resp.to_dataframe()
                uc.log("get {0} items ... ", len(frm.index))
                uc.logln("DONE")

        # resp = fs.get_offline_features("store://feature-vectors/gate-alfa/vector-partycontact:latest")
        # resp.to_dataframe()
        #
        # svc = fs.get_online_feature_service("store://feature-vectors/gate-alfa/vector-partycontact:latest")
        # resp = svc.get([{"customer_id": "42"}, {"customer_id": "50"}])

    def serving_score(self, uc: UCBase):
        """
        Serve score
        """
        uc.loghln()

        # prepare model

        # store pickl file

        # add model

