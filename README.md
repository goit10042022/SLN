[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version fury.io](https://badge.fury.io/py/qgate-sln-mlrun.svg)](https://pypi.python.org/pypi/qgate-sln-mlrun/)
![coverage](https://github.com/george0st/qgate-sln-mlrun/blob/master/coverage.svg?raw=true)
![GitHub commit activity](https://img.shields.io/github/commit-activity/w/george0st/qgate-sln-mlrun)
![GitHub release](https://img.shields.io/github/v/release/george0st/qgate-sln-mlrun)

# QGate-Sln-MLRun
The Quality Gate for solution MLRun (and Iguazio). The main aims of the project are:
- independent quality test (function, integration, acceptance, ... tests)
- deeper quality checks before full rollout/use in company environments
- identification of possible compatibility issues (if any)
- external and independent test coverage
- etc.

The tests use these key components, MLRun solution see **[GIT mlrun](https://github.com/mlrun/mlrun)**, 
sample meta-data model see **[GIT qgate-model](https://github.com/george0st/qgate-model)** and this project.

## Test scenarios
The quality gate covers these test scenarios (✅ done, ✔ in-progress, ❌ planned):
 - **Project**
   - ✅ TS101: Create project(s)
   - ✅ TS102: Delete project(s)
 - **Feature set**
   - ✅ TS201: Create feature set(s)
 - **Ingest data**
   - ✅ TS301: Ingest data to feature set(s) from DataFrame source
   - ✅ TS302: Ingest data to feature set(s) from CSV source 
   - ✅ TS303: Ingest data to feature set(s) from Parquet source
   - ✔  TS304: Ingest data to feature set(s) from SQL source
   - ❌ TS305: Ingest data to feature set(s) from Kafka source
   - ❌ TS306: Ingest data to feature set(s) from HTTP source
 - **Feature vector**
   - ✅ TS401: Create feature vector(s)
 - **Get data from vector**
   - ✅ TS501: Get data from off-line feature vector(s)
   - ✅ TS502: Get data from on-line feature vector(s)
 - **Pipelines**
   - ❌ TS601: Simple cleanup pipeline for DataFrame source
   - ❌ TS602: Simple cleanup pipeline for CSV source
   - ❌ TS603: Simple cleanup pipeline for Parquet source
   - ❌ TS604: Complex cleanup pipeline for DataFrame source
   - ❌ TS605: Complex cleanup pipeline for CSV source
   - ❌ TS606: Complex cleanup pipeline for Parquet source
 - **Build model**
   - ✅ TS701: Build CART model
   - ❌ TS702: Build XGBoost model
   - ❌ TS703: Build DNN model
 - **Serve model**
   - ✅ TS801: Serving score from CART
   - ❌ TS802: Serving score from XGBoost
   - ❌ TS803: Serving score from DNN
   
NOTE: Each test scenario contains addition specific test cases (e.g. with different
targets for feature sets, etc.).

## Test inputs/outputs
The quality gate tests these inputs/outputs (✅ done, ✔ in-progress, ❌ planned):
 - Outputs (targets)
   - ✅ RedisTarget, ✔ SQLTarget/MySQL, ✔ SQLTarget/Postgres, ✅ KafkaTarget
   - ✅ ParquetTarget, ✅ CSVTarget
   - ✅ File system, ❌ S3, ❌ BlobStorage
 - Inputs (sources)
   - ✅ Pandas/DataFrame, ❌ SQLSource/MySQL, ❌ SQLSource/Postgres, ❌ KafkaSource
   - ✔ ParquetSource, ✅ CSVSource
   - ✅ File system, ❌ S3, ❌ BlobStorage


The supported [sources/targets from MLRun](https://docs.mlrun.org/en/latest/feature-store/sources-targets.html).

## Sample of outputs

![Sample of outputs](https://github.com/george0st/qgate-sln-mlrun/blob/master/assets/imgs/qgt-mlrun-samples.png?raw=true)

The reports in original form, see:
 - all DONE - [HTML](https://htmlpreview.github.io/?https://github.com/george0st/qgate-sln-mlrun/blob/master/docs/samples/outputs/qgt-mlrun-sample.html), 
   [TXT](https://github.com/george0st/qgate-sln-mlrun/blob/master/docs/samples/outputs/qgt-mlrun-sample.txt?raw=true)
 - with ERR - [HTML](https://htmlpreview.github.io/?https://github.com/george0st/qgate-sln-mlrun/blob/master/docs/samples/outputs/qgt-mlrun-sample-err.html),
   [TXT](https://github.com/george0st/qgate-sln-mlrun/blob/master/docs/samples/outputs/qgt-mlrun-sample-err.txt?raw=true)

## Usage

You can easy use this solution in four steps:
1. Download content of these two GIT repositories to your local environment
    - [qgate-sln-mlrun](https://github.com/george0st/qgate-sln-mlrun)
    - [qgate-model](https://github.com/george0st/qgate-model)
2. Update file `qgate-sln-mlrun.env` from qgate-model
   - Update variables for MLRun/Iguazio, see `MLRUN_DBPATH`, `V3IO_USERNAME`, `V3IO_ACCESS_KEY`, `V3IO_API`
     - setting of `V3IO_*` is needed only in case of Iguazio installation (not for pure free MLRun)
   - Update variables for QGate, see `QGATE_*` (basic description directly in *.env)
     - detail setup [configuration](./docs/configuration.md)
3. Run from `qgate-sln-mlrun`
   - **python main.py**
4. See outputs (location is based on `QGATE_OUTPUT` in configuration)
   - './output/qgt-mlrun-<date_time>.html'
   - './output/qgt-mlrun-<date_time>.txt'

Precondition: You have available MLRun or Iguazio solution (MLRun is part of that),
see official [installation steps](https://docs.mlrun.org/en/latest/install.html), or directly installation for [Desktop Docker](https://docs.mlrun.org/en/latest/install/local-docker.html). 

## Tested with
The project was tested with these MLRun versions (see [change log](https://docs.mlrun.org/en/latest/change-log/index.html)):
 - **MLRun** (in Desktop Docker)
   - MLRun 1.7.0 (plan 05/2024)
   - MLRun 1.6.3 (plan 04/2024), 1.6.2, 1.6.1, 1.6.0
   - MLRun 1.5.2, 1.5.1, 1.5.0
   - MLRun 1.4.1, 1.3.0
 - **Iguazio** (k8s, on-prem, VM on VMware)
   - Iguazio 3.5.3 (with MLRun 1.4.1)
   - Iguazio 3.5.1 (with MLRun 1.3.0)

NOTE: Current state, only the last MLRun/Iguazio versions are valid for testing 
(these tests are without back-compatibilities).

## Others
 - **To-Do**, the list of expected/future improvements, [see](./docs/todo_list.md)
 - **Applied limits**, the list of applied limits, [see](./docs/applied-limits.md) 
 - **How can you test the solution?**, you have to focus on Linux env. or 
 Windows with WSL2 ([see](./docs/testing.md) step by step tutorial)
 - **The key business changes in MLRun/Iguazio**, [see](./docs/mlrun-history.md)
