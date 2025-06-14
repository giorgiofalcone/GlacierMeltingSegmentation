# SORS Framework: Repository Structure Overview
This repository contains the **SORS Framework**, which integrates semantic segmentation and ontological modeling to support environmental monitoring tasks. The name **SORS** derives from the custom-developed ontology implemented within the system.
The framework supports two primary application domains: **glacier melting** and **deforestation**.

---
### Segmentation/
It contains Jupyter notebooks and scripts for training and testing semantic segmentation models on satellite images. Key notebooks include:

- `Segmentation.ipynb`: performs segmentation tasks for both glaciers and forest areas.

- `DataToCSV.ipynb`: extracts structured data from segmentation results and meteorological `.nc` files (NetCDF),   producing CSV outputs for downstream ontology population.

**Applicable to**: Glacier monitoring and deforestation assessment.

---
### Ontology/
Includes the `SORSOntology.owl` file, which integrates SOSA/SSN and WeatherOntology to semantically represent segmentation outputs alongside contextual environmental data. This directory also contains:

- Scripts for ontology population.
- Reasoning modules and SPARQL query examples.

**Applicable to**: Both domains, ontology can be extended with glacier- or forest-specific classes.

---
### Deforestation/
Houses scripts and data specific to deforestation modeling, including training and evaluation of segmentation models on tropical forest datasets. This domain uses additional vegetation indices (e.g., NDVI, MSAVI) for enhanced performance.

**Applicable to**: Deforestation monitoring only.

---
### APP/app_segmentation/
Web application that integrates the segmentation model and ontology backend. The app allows users to:

- Upload satellite images.
- Perform segmentation (glacier or forest).
- Query semantic data via a web interface.

**Supports**: Both glacier melting and deforestation use cases.
