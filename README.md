# CF-Zenodo

[![License: MPL-2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Cite this repository](https://img.shields.io/badge/Cite%20this-Repository-blue)](./CITATION.cff)
[![Conda environment](https://img.shields.io/conda/vn/conda-forge/cf-zenodo.svg)](https://anaconda.org/conda-forge/cf-zenodo)
[![GitHub issues](https://img.shields.io/github/issues/cofinoa/CF-Zenodo.svg)](https://github.com/cofinoa/CF-Zenodo/issues)

---

## **Overview**
**CF-Zenodo** is a software tool for the management, curation, and publication of **CF Convention-related records** on Zenodo. It provides an end-to-end solution for caching metadata, reviewing content, and managing publishing workflows. By supporting **controlled publishing** via the InvenioRDM API, CF-Zenodo ensures the integrity, discoverability, and longevity of CF community records on Zenodo.

---

## **Repository Structure**
```
/
├── config/
│   ├── zenodo_config.json       # Zenodo API configuration (API URL, community, access token)
│   ├── default_settings.json    # Default settings for fetching and CLI
│   └── metadata_template.json   # Template for filtering and validating metadata
│
├── scripts/
│   ├── fetch_records.py         # Script to fetch and cache records from Zenodo
│   └── zenodo.py                # CLI to fetch, update, publish, and show Zenodo records
│
├── utils/
│   ├── config_utils.py          # Functions for configuration and environment initialization
│   ├── zenodo_api.py            # Zenodo API abstraction for reusable API interactions
│   └── docopt.py                # CLI argument parser for zenodo.py
│
├── example.env                  # Example environment file
├── environment.yml              # Conda environment file
├── LICENSE                      # License file (Mozilla Public License 2.0)
├── NOTICE                       # Notices and attributions required by the license
├── README.md                    # This README file
└── CITATION.cff                 # Citation file to enable proper citation of the repository
```

---

## **Installation**

### **1. Clone the repository**
```bash
git clone https://github.com/cofinoa/CF-Zenodo.git
cd CF-Zenodo
```

---

### **2. Set up the environment**
```bash
conda env create -f environment.yml
conda activate cf-zenodo
```

---

### **3. Set up environment variables (optional)**
Create a `.env` file at the root of the repository with the following content:
```dotenv
ZENODO_BASE_URL=https://zenodo.org/api
ZENODO_ACCESS_TOKEN=your_access_token_here
ZENODO_COMMUNITY_ID=cfconventions
```

Alternatively, export these environment variables in your terminal:
```bash
export ZENODO_BASE_URL=https://zenodo.org/api
export ZENODO_ACCESS_TOKEN=your_access_token_here
export ZENODO_COMMUNITY_ID=cfconventions
```

These environment variables configure access to the Zenodo API, including the community and access token.

---

## **Configuration**

The CF-Zenodo repository supports multiple configuration methods:
1. **`.env` file**: Defines environment variables (e.g., `ZENODO_ACCESS_TOKEN`).
2. **Configuration files**:
    - **`config/zenodo_config.json`**: Contains base URL, community ID, and Zenodo API-related options.
    - **`config/default_settings.json`**: Contains settings for script behaviors like `dry_run` and `output_dir`.
    - **`config/metadata_template.json`**: Defines which metadata fields to extract and filter from the Zenodo API response.

---

## **Usage**

### **1. scripts/fetch_records.py**
**Purpose**: Fetch and cache Zenodo records, storing them locally.

**Usage**:
```bash
python scripts/fetch_records.py
```

**Options**:
- **`ZENODO_BASE_URL`**: Base URL for the Zenodo API (default: `https://zenodo.org/api`).
- **`ZENODO_ACCESS_TOKEN`**: Access token for authenticated requests.
- **`ZENODO_COMMUNITY_ID`**: Community ID to fetch records from.

**Example Directory Structure**:
```
 /records/{record_id}/
   ├── metadata.json  # Filtered metadata according to metadata_template.json
   └── files/         # Directory where record files are downloaded
```

---

### **2. scripts/zenodo.py**

**Purpose**: A CLI to manage Zenodo records, supporting **fetch**, **update**, **publish**, and **show** operations.

**Usage**:
```bash
python scripts/zenodo.py <command> [options]
```

**Commands**:
 - **`fetch`**: Download and cache Zenodo records for a specific community.
 - **`update`**: Update a Zenodo record by modifying its metadata.
 - **`publish`**: Publish a Zenodo record that is currently a draft.
 - **`show`**: Display and cache a specific Zenodo record.

 **Options**:
 - **`--record-id`**: The ID of the record to fetch, update, or publish.
 - **`--community-id`**: The Zenodo community to fetch records from.
 - **`--output-dir`**: Directory to store records (default: `./records`).
 - **`--dry-run`**: Run the command without making any changes.

---

## **Development Environment**

To set up the development environment, use the `environment.yml` file.

To create the environment, run:
```bash
conda env create -f environment.yml
```

To activate the environment, run:
```bash
conda activate cf-zenodo
```

To export the current environment to `environment.yml`, run:
```bash
conda env export --no-builds > environment.yml
```

---

## **Citation**

If you use **CF-Zenodo** in your project or research, please cite it as follows:

```
Cofiño, Antonio S. (2024). CF-Zenodo: A Toolkit for Managing CF Conventions Records on Zenodo (Version 0.1) [Software]. Available at: https://github.com/cofinoa/cf-zenodo
```

Alternatively, you may use the following BibTeX entry:

```bibtex
@software{cf-zenodo,
  author       = {Antonio S. Cofiño},
  title        = {CF-Zenodo: A Toolkit for Managing CF Conventions Records on Zenodo},
  year         = 2024,
  version      = {0.1},
  publisher    = {GitHub},
  url          = {https://github.com/cofinoa/cf-zenodo}
}
```

A [**CITATION.cff**](./CITATION.cff) file is included to make it easy to cite this repository. You can use tools like [GitHub's citation file feature](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files) to access the citation.

---

## **License**
This project is licensed under the Mozilla Public License, Version 2.0. See the [LICENSE](./LICENSE) file for more information.

---

## **Notice**

The **CF-Zenodo** project is subject to important notices and attributions, which are documented in the [NOTICE](./NOTICE) file.  
These notices may include information regarding third-party libraries, disclaimers of warranty, and any special legal attributions related to this project.  
By using this software, you agree to the terms and conditions set out in the **LICENSE** and **NOTICE** files.

---

## **Contributing**
Contributions are welcome! Please fork this repository and submit a pull request to suggest improvements or fixes.

---

## **Issues**
If you encounter issues, please create an issue on the [GitHub Issues](https://github.com/cofinoa/CF-Zenodo/issues) page.

---
