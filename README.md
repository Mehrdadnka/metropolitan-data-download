# Iranian Pottery Dataset Collector: Metropolitan-Dataset-Api

A fully automated, multithreaded Python tool for collecting, classifying, and organizing high-quality images and metadata of ancient Iranian pottery from The Metropolitan Museum of Art (MET) public API — designed for use in machine learning, digital heritage preservation, and archaeological research.

---

## 🔍 Purpose

This tool supports a master's research project focused on the **classification of ancient Iranian pottery** by historical period. The collected data serves as a training set for machine learning models in:

* Artifact classification
* Chronological period detection
* Digital preservation of cultural heritage

---

## 🎯 Key Features

✅ **Automated Data Collection**
Fetches pottery artifacts from the MET Collection API using carefully crafted search queries.

✅ **Intelligent Classification**
Automatically classifies artifacts into:

* **Pre-Islamic periods**: e.g., Elam, Achaemenid, Sassanian
* **Islamic periods**: e.g., Safavid, Seljuk, Qajar

Based on keywords extracted from object metadata (title, culture, period, objectDate).

✅ **Folder Structure by Period**
Downloads and stores each artifact's image into a hierarchical folder structure by **era and historical sub-period**.

✅ **Metadata Export**
Saves comprehensive metadata in:

* **JSON** format (`iran_pottery_metadata.json`)
* **CSV** format (`iran_pottery_metadata.csv`) — suitable for ML pipelines.

✅ **Multithreaded Performance**
Fast, concurrent downloads with error handling and retry logic.

✅ **Robust Download Verification**
Ensures only high-quality images (≥10KB) are saved.

✅ **Configurable**
Modify dataset size, retries, timeouts, historical period filters, and more in the `CONFIG` dictionary.

---

## ⚙️ Configuration Overview

Adjust these in the script’s `CONFIG` dictionary:

| Parameter            | Description                                           | Example Value                 |
| -------------------- | ----------------------------------------------------- | ----------------------------- |
| `dataset_path`       | Root folder for images and metadata                   | `"./iran_pottery_dataset"`    |
| `timeout`            | Timeout per API request (seconds)                     | `25`                          |
| `retries`            | Number of download retries per image                  | `4`                           |
| `max_images`         | Maximum number of images to collect                   | `200`                         |
| `historical_periods` | Dictionary of Pre-Islamic and Islamic period keywords | see script                    |
| `user_agents`        | Random User-Agent rotation for requests               | Chrome, Safari, Linux headers |

---

## 🚀 Usage Instructions

### 1. Install Dependencies

```bash
pip install requests tqdm
```

### 2. Run the Collector

```bash
python iran_pottery_downloader.py
```

### 3. Output Structure

```
iran_pottery_dataset/
│
├── images/
│   ├── pre_islamic/
│   │   ├── Elam/
│   │   ├── Achaemenid/
│   │   └── Sassanian/
│   └── islamic/
│       ├── Safavid/
│       ├── Seljuk/
│       └── Qajar/
│
├── iran_pottery_metadata.json   # Full metadata (JSON)
└── iran_pottery_metadata.csv    # Tabular metadata (CSV)
```

---

## 📋 Sample Metadata Fields

| Field Name           | Example Value                               |
| -------------------- | ------------------------------------------- |
| `objectID`           | 324019                                      |
| `title`              | Bowl with geometric patterns                |
| `culture`            | Iranian                                     |
| `period`             | Achaemenid                                  |
| `objectDate`         | 5th century B.C.                            |
| `classification`     | Ceramics                                    |
| `era_classification` | pre\_islamic                                |
| `historical_period`  | Achaemenid                                  |
| `local_path`         | ./images/pre\_islamic/Achaemenid/324019.jpg |

---

## ⚠️ Known Limitations

* **Keyword-based classification**: Possible misclassifications due to incomplete or ambiguous metadata from the MET API.
* **API reliance**: Dependent on MET's public API availability and accuracy.
* **Curation needed**: Automatic results may include artifacts irrelevant to the research focus (manual review is advised for final dataset usage).

---

## 🧩 Planned Improvements

* Integration with other museum APIs (e.g., British Museum, Louvre)
* Advanced NLP-based period classification
* Duplicate detection & removal
* Automatic dataset curation suggestions

---

## 👤 Author

**Mehrdadnka**
Master's Thesis Project – \[Art University Of Isfahan]
Email: *\[mehrdad2762@gmail.com]*
GitHub: *https://github.com/Mehrdadnka*

---

## 📜 License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.

---

## ❤️ Acknowledgments

* The Metropolitan Museum of Art (MET) Open Access Initiative
* Python Community and Open-Source Contributors

---

### 🔗 Related Resources

* [MET Collection API Documentation](https://metmuseum.github.io/)

