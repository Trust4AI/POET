## Trust4AI Component Template

This project serves as a template for the creation of new components to carry out the evaluation of AI-enabled Search Engines.

### Naming convention for new repositories

It is proposed to use a naming convention for repositories using the template, in order to improve the organisation and facilitate the identification of the different repositories.

The naming convention follows the format `trust4ai-<qa>-<component>-<approach>`, where:

- **\<qa\>** represents the quality attribute associted with the repository. Possible values could be:
    - bias
    - safety
    - privacy
- **\<component\>** indicates the main action performed by the repository on the quality attribute. Possible values could be:
    - generator
    - evaluator
- **\<technique\>** indicates the technique used to carry out the repository's objective on the quality attribute. Possible values could be:
    - ds, for dataset
    - mt, for metamorphic testing
    - llm, for large language models

For example, if you want to create a repository to serve as an input generator for the safety quality attribute, using a dataset, the name of such a repository would be _trust4ai-safety-generator-ds_.

### Template structure

This repository contains the structure to be used as the basis for development:

- `docs/openapi/spec.yaml`: This file is used to describe the entire API, including available endpoints, operations on each endpoint, operation parameters, and the structure of the response objects. It's written in YAML format following the [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) (OAS).
- `docs/postman/collection.json`: This file is a collection of API requests saved in JSON format for use with Postman.
-  `src/`: This directory contains the source code for the project.
-  `.dockerignore`: This file tells Docker which files and directories to ignore when building an image.
-  `.gitignore`: This file is used by Git to exclude files and directories from version control.
-  `Dockerfile`: This file is a script containing a series of instructions and commands used to build a Docker image.
-  `docker-compose.yml`: This YAML file allows you to configure application services, networks, and volumes in a single file, facilitating the orchestration of containers.

## License and funding

[Trust4AI](https://trust4ai.github.io/trust4ai/) is licensed under the terms of the GPL-3.0 license.

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or European Commission. Neither the European Union nor the granting authority can be held responsible for them. Funded within the framework of the [NGI Search project](https://www.ngisearch.eu/) under grant agreement No 101069364.

<p align="center">
<img src="https://github.com/Trust4AI/trust4ai/blob/main/funding_logos/NGI_Search-rgb_Plan-de-travail-1-2048x410.png" width="400">
<img src="https://github.com/Trust4AI/trust4ai/blob/main/funding_logos/EU_funding_logo.png" width="200">
</p>
