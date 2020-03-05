# Check_elastic_pattern

Checks an Elasticsearch ingest pipeline against test cases.
Use case would be to check pipelines from git against expected behaviour in automated tests for CI/CD.

This uses the elasticsearch ingest pipeline simulate feature (see <https://www.elastic.co/guide/en/elasticsearch/reference/current/simulate-pipeline-api.html)>)

## Usage

### Preparation

Spawn an elasticsearch server in your build system. If you use regular epression in the ingest pipelines you will have to enable `script.painless.regex.enabled=true`to make it work.

Then deploy the pipeline to that elasticsearch server. The input JSON file conatins the actual pipeline definition and a name for that pipeline.

```shell
python3 elasticcheck --prepare http://elasticserver:9200 pipeline.json
```

### Tests

Run tests as defined in JSON files against the pipelines.

```shell
python3 elasticcheck --prepare http://elasticserver:9200 tescase.json
```

## File Formats

See examples/ folder.

### Pipeline Definition

```json
{
    "name": "my-pipeline",
    "pipeline":
    {
        PIPELINE DEFINITION
    }
}
```

The pipeline definition is exactly what your would `PUT` into elasticsearch using curl. See <https://www.elastic.co/guide/en/elasticsearch/reference/current/pipeline.html>.

### Test Definitions

```json
{
    "pipeline": "my-pipeline",
    "assertions" : {
        "logmessage": "Starting RestApplication on example-backend-6cfd785f48-xmxgz with PID 7 (/app.jar started by root in /)",
        "thread": "main",
        "@timestamp": "2020-02-05T10:02:57,357",
        "loglevel": "INFO",
        "javaclass": "com.example.app.RestApplication"
    },
    "input": {
        TEST DOCUMENT
    }
}
```

`pipeline` is the name of the pipeline to test against (see Pipeline Definition).
`assertions` ist a list of keys and values, which are expected to be contained in the response from elasticsearch. A test is only considered "Success", if the key and content match exactly. All keys must be present.
`input` is a single (!) elasticsearch document to be processed by the pipeline. This follows the usage documented at <https://www.elastic.co/guide/en/elasticsearch/reference/current/simulate-pipeline-api.html> just that here you do not specify a list of documents, but just a single one.

## Example

Start elasticsearch docker locally

```shell
docker run -d --name elastic -p 9200:9200 -e "discovery.type=single-node" -e "script.painless.regex.enabled=true" elasticsearch:7.5.2
```

Inject pipeline definition into elasticsearch

```shell
python3 elasticcheck.py --prepare http://localhost:9200 examples/pipeline.json
```

Run test

```shell
shell> python3 elasticcheck.py http://localhost:9200 examples/testcase1.json
python3 elasticcheck.py http://localhost:9200 examples/testcase1.json                                                        0|11:22:39
Simulating pipeline my-pipeline returned 200
SUCCESS: Assertion for key logmessage matched.
SUCCESS: Assertion for key thread matched.
SUCCESS: Assertion for key @timestamp matched.
SUCCESS: Assertion for key loglevel matched.
SUCCESS: Assertion for key javaclass matched.
```
