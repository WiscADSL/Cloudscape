This repository contains the dataset and code for [Cloudscape: A Study of Storage Services in Modern Cloud Architectures](https://www.usenix.org/conference/fast25/presentation/satija), presented at FAST25.

<details>
<summary>BibTeX</summary>

```
@inproceedings {cloudscape-fast25,
author = {Sambhav Satija and Chenhao Ye and Ranjitha Kosgi and Aditya Jain and Romit Kankaria and Yiwei Chen and Andrea C. Arpaci-Dusseau and Remzi H. Arpaci-Dusseau and Kiran Srinivasan},
title = {Cloudscape: A Study of Storage Services in Modern Cloud Architectures},
booktitle = {23rd USENIX Conference on File and Storage Technologies (FAST 25)},
year = {2025},
address = {Santa Clara, CA},
url = {https://www.usenix.org/conference/fast25/presentation/satija},
publisher = {USENIX Association},
month = feb
}
```
</details>

<br />
This repository has 3 key parts:

1. **Dataset:** The dataset describes 396 cloud architectures. Each cloud architecture is a GraphML file in `data/graphs/`. The services used across these architectures are described in `data/services.csv`. The [schema section](#1-dataset-schema) describes how to interpret the GraphML and csv files.

1. **Analysis Jupyter Notebook:** We provide a [Jupyter notebook](Analysis.ipynb) that replicates the analysis in the paper. The notebook does not always produce the published version of the graphs. Instead, it favours demonstrating how the query is performed, and aims to miminize the presentation code. Our goal is to demonstrate how to traverse the dataset to future researchers. Refer to the [Analysis section](#2-analysis) on how to setup the environment.

1. **Web-based Architecture Explorer:** For easier access to the dataset, we provide a web platform, hosted at [cloudscape.cs.wisc.edu](https://cloudscape.cs.wisc.edu). This repository also contains the source code for this platform. The [Explorer section](#3-architecture-explorer) describes its setup if you wish to modify it.

# 1. Dataset Schema
## Architecture
Each GraphML file describes one architecture. The architecture is encoded as a `MultiDiGraph`, which means that the graph contains directed edges and potentially contains multiple edges between 2 nodes. There are many readers for GraphML files; we use the Python `networkx` package.
### Graph
Each graph has these attributes:

| Attribute Name | Optional | Description                                                                                                              | Example Value                                                                              |
|----------------|----------|--------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `name`           |          | The title of the YouTube video that describes this architecture.                                                         | Snap: Journey of a Snap on Snapchat Using AWS                                              |
| `link`           |          | The link to the source YouTube video.                                                                                    | https://www.youtube.com/watch?v=Cgv0kfp_6xQ                                                |
| `categories`     |          | Comma separated list of functional goals. Possible goals:(data_ingestion, interactive, compute_intensive, control, other)| data_ingestion,compute_intesive                                                            |
| `graph_usable`   |          | Can the encoded graph be used for any quantitative graph analysis? The paper only analyzes architectures marked True.                        | True                                                                                       |
| `notes`          | yes      | Distilled context from the video that captures the requirements of the architectures and how services are used.                                                    | 13TB of peak data to S3 daily. Use of DynamoDB to store metadata has increased throughput. |

### Node
Each node has these attributes:

| Attribute name | Optional | Description                                                                     | Example Value                         |
|----------------|----------|---------------------------------------------------------------------------------|---------------------------------------|
| `service`      |          | The name of the AWS service, or class of other service. Used in `services.csv`. | Lambda or UserMobile                  |
| `name`         | yes      | (ThirdParty nodes only). Name of the service.                                   | nginx or legacy API                   |
| `notes`        | yes      | Additional context about how this service was used.                             | 6000 calls/s, 200k records/validation |

There are five types of nodes,
**AWS** nodes,
**User** nodes,
**Partner** nodes,
**ThirdParty** nodes,
**OnPremDC** nodes.

**AWS** nodes represent AWS services and **User** nodes indicate an end user, and sometimes the device (for example, web app or Alexa). **ThirdParty** nodes are
nodes that don't fit in either, but are often mentioned in the video without much context (for example, 'internal company API'). **Partner** nodes are reserved for AWS partner companies that provide their software via the AWS marketplace (for example, SAP or Couchbase). **OnPremDC** nodes denote a company's on-premisis datacenter. Effectively, **ThirdParty** describes one off services that are only needed to explain one architecture, and thus each **ThirdParty** node is described by its `name`.

### Edge
| Attribute name | Optional | Description                                                                                                                                                  | Example Value |
|----------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `flow_id`        |          | Whole number that indicates which workflow this edge is a part of. All edges with the same `flow_id` are part of the same workflow.                               | 1             |
| `seq`            |          | Orders edges inside a workflow. When events are not strictly synchronous, branches are denoted by apostrophe('). events can have order within branches. Visit the explorer for examples. | 3'.2          |
| `type`           |          | data/meta. data edges convey movement of data, meta edges indicate request trigger or acknowledgement.response                                               | data          |
| `notes`          | yes      | Additional context on how these 2 (connected) nodes communicate.                                                                                             | periodic      |

### Workflow
Videos often describe a set of interactions that collectively result in a logical unit of work. We capture such interactions as workflows. A workflow is encoded using `edge.flow_id`. All edges with the same `flow_id`, and their corresponding nodes, describe the set of interactions for that workflow.

## Services
The `data/services.csv` file describes all the different types of nodes used across the dataset.

| Field                  | Description                                                                                                                                                                                                                                                         |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                 | The name of the AWS service, or node type. As described in [the node section](#node).                                                                                                                                                                               |
| `capability`           | AWS services will have one of (`storage`, `compute`, `networking`, `integration`, `control`, `other`). Ref to paper for description. For User, Partner, ThirdParty and OnPremDC nodes, it will contain the relevant (`User`, `Partner` , `ThirdParty`, `OnPremDC`). |
| `is_aws`               | True for AWS services, False otherwise.                                                                                                                                                                                                                             |
| `schema`               | Only for AWS storage services. One of (`fs`, `sql`, `nosql`, `specialized`, `object`).                                                                                                                                                                                  |
|`aws_product_categories`| Only for AWS services. Comma separated list of [categories](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/amazon-web-services-cloud-platform.html).                                                                                                   |
| `image_url`            | for explorer purposes only. refers to svg file in `static/icons`.                                                                                                                                                                                                   |


# 2. Analysis
To run the [notebook](Analysis.ipynb) locally, clone the repository and install the dependencies using `pip install -r requirements-analysis.txt`. You should then be able to open the notebook with `jupyter-notebook`. This was developed using `Python 3.11`.


# 3. Architecture Explorer
To run the explorer locally, clone the repository and install the dependencies using `pip install -r requirements-explorer.txt`. You can then deploy the platform with `streamlit run explorer_st.py`. This was developed using `Python 3.11`.
