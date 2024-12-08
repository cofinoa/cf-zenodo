# CF-Zenodo

A repository for the collection, uploading, and curation of historic documents to Zenodo, related to the CF Convention. Preserving the past, shaping the future.

---

## 📚 **Overview**
CF-Zenodo is a Python-based command-line interface (CLI) and script-based tool for managing Zenodo records. It allows users to fetch, cache, curate, and publish Zenodo records. The system uses the **Zenodo InvenioRDM API** and is highly configurable via `.env` files, JSON configurations, and environment variables.

---

## 📁 **Repository Structure**
```
cf-zenodo/
├── config/
│   ├── zenodo_config.json       # Main Zenodo configuration (API URL, community, etc.)
│   ├── default_settings.json    # Default settings for fetching and CLI
│   └── metadata_template.json   # Metadata template for filtering metadata fields
│
├── scripts/
│   ├── fetch_records.py         # Script to fetch and cache records from Zenodo
│   └── zenodo.py                # CLI to fetch, update, publish, and show Zenodo records
│
├── utils/
│   ├── config_utils.py          # Functions for environment and configuration initialization
│   ├── zenodo_api.py            # Zenodo API abstraction for reusable API interactions
│   └── docopt.py                # CLI argument parser for zenodo.py
│
├── .env                         # Optional file to define environment variables
├── environment.yml              # Conda environment file for setting up the development environment
├── README.md                    # This README file
└── requirements.txt             # Pip dependencies required for the repository
```

---

## 🚀 **Installation**

1. **Clone the repository**:
```bash
git clone https://github.com/cofinoa/CF-Zenodo.git
cd CF-Zenodo
```

2. **Set up the environment**:
```bash
conda env create -f environment.yml
conda activate cf-zenodo
```

3. **Set up environment variables** (optional):

Create a `.env` file at the root of the repository with the following content:
```
ZENODO_BASE_URL=https://zenodo.org/api
ZENODO_ACCESS_TOKEN=your_access_token_here
ZENODO_COMMUNITY_ID=cfconventions
```

Alternatively, you can export these variables in your terminal:
```bash
export ZENODO_BASE_URL=https://zenodo.org/api
export ZENODO_ACCESS_TOKEN=your_access_token_here
export ZENODO_COMMUNITY_ID=cfconventions
```

---
## ⚙️ **Configuration**
The CF-Zenodo repository supports multiple configuration methods:
1. **`.env` file**: Defines environment variables (e.g., `ZENODO_ACCESS_TOKEN`).
2. **Config files**:
    - **`config/zenodo_config.json`**: Contains base URL, community ID, and Zenodo API-related options.
    - **`config/default_settings.json`**: Settings for script behaviors like `dry_run` and `output_dir`.
    - **`config/metadata_template.json`**: Defines which metadata fields to extract from the Zenodo API response.

---

## 📘 **Usage**

### **1️⃣ scripts/fetch_records.py**
**Purpose**: Fetch and cache Zenodo records, storing them locally.

**Usage**:
```bash
python scripts/fetch_records.py
```

**Options**:
- **`ZENODO_BASE_URL`**: Base URL for Zenodo API (default: `https://zenodo.org/api`).
- **`ZENODO_ACCESS_TOKEN`**: Access token for authenticated requests.
- **`ZENODO_COMMUNITY_ID`**: Community ID to fetch records from.

**Example Directory Structure**:
```
 /records/{record_id}/
   ├── metadata.json  # Filtered metadata according to metadata_template.json
   └── files/         # Directory where record files are downloaded
```

---

### **2️⃣ scripts/zenodo.py**

**Purpose**: A CLI to manage Zenodo records, supporting **fetch**, **update**, **publish**, and **show** operations.

**Usage**:
```bash
python scripts/zenodo.py <command> [options]
```

**Commands**:
 - **`fetch`**: Download and cache Zenodo records for a specific community.
 - **`update`**: Update a Zenodo record by modifying its metadata and sending a PUT request.
 - **`publish`**: Publish a Zenodo record that is currently a draft.
 - **`show`**: Display and cache a specific Zenodo record.

 **Options**:
 - **`--record-id`**: The ID of the record to fetch, update, or publish.
 - **`--community-id`**: The Zenodo community to fetch records from.
 - **`--output-dir`**: Directory to store records (default: `./records`).
 - **`--dry-run`**: Run the command without making any changes.

---

## 🔧 **Development Environment**
To set up the development environment, use the `environment.yml` file.
```yaml
name: cf-zenodo
channels:
  - conda-forge
dependencies:
  - python=3.10  # Ensures compatibility with the latest libraries
  - requests      # Required for API interactions
  - docopt        # Used for CLI argument parsing
  - pyyaml        # Used for reading YAML configuration files
```

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

## 📜 **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 **Contributing**
Contributions are welcome! Please fork this repository and submit a pull request to suggest improvements or fixes.

---

## 🐛 **Issues**
If you encounter issues, please create an issue on the [GitHub Issues](https://github.com/cofinoa/CF-Zenodo/issues) page.
