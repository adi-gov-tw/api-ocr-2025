<h4 align="center">
    <p>
        <a href="">繁體中文</a> |
        <b>English</b>
    </p>
</h4>

# Multilingual ASR Training Project (Mandarin/Taiwanese/Hakka/English)

(*Please describe the project, official project name, and a brief summary here*)

This project provides an Automatic Speech Recognition (ASR) model training workflow, including pre-trained models for Mandarin, Taiwanese, Hakka, and English. You can fine-tune the models with your own speech data or use the existing models for speech recognition directly.

## Project Structure

(*Please describe the project code directory structure here*)

```
.
├── sample_corpus/
│   ├── train_ds_01/
│   │   ├── train.tsv
│   │   ├── test.tsv
│   │   ├── validated.tsv
│   │   └── clips/
│   │       ├── audio_train_01_1.wav
│   │       ├── audio_train_01_2.wav
│   │       └── audio_test_01_1.wav
│   └── train_ds_02/
│       ├── train.tsv
│       ├── test.tsv
│       ├── validated.tsv
│       └── clips/
│           └── a1/
│               ├── audio_train_02_1.wav
│               ├── audio_train_02_2.wav
│               └── audio_test_02_1.wav
├── models/
│   ├── model.bin
│   ├── config.json
│   ├── preprocessor_config.json
│   ├── tokenizer.json
│   └── vocabulary.json
├── train_asr.py
├── run.sh
├── CITATION.cff
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
└── README.md
```

### Folder Descriptions

(*Please describe the details of the project code files here*)

- **sample_corpus/**  
  Stores speech data and annotation files. Each subfolder (e.g., `train_ds_01`, `train_ds_02`) represents a dataset. Each dataset includes:
  - `train.tsv`, `test.tsv`, `validated.tsv`: Annotation files in tab-separated format, containing the path to the audio file and the corresponding transcription.
  - `clips/`: Stores the actual audio files, supporting multi-level subdirectories.

- **models/**  
  Stores pre-trained models for Mandarin, Taiwanese, Hakka, and English, including:
  - `model.bin`: Model weights file.
  - `config.json`, `preprocessor_config.json`, `tokenizer.json`, `vocabulary.json`: Model configuration and vocabulary files.

- **train_asr.py**  
  Training script for fine-tuning or training ASR models.

- **run.sh**  
  Script to execute training; parameters can be modified as needed.

- **README.md**  
  Project documentation, providing usage guide and reference information.

## Corpus Format Description

- Speech data and annotation files should be placed under the `sample_corpus` directory. Each subfolder (e.g., `train_ds_01`, `train_ds_02`) represents a dataset.
- Each dataset must include:
  - `train.tsv`, `test.tsv`, `validated.tsv`: Annotation files in the following format (tab-separated):
    ```
    path    sentence
    audio_train_01_1.wav    This is a speech segment
    audio_train_01_2.wav    Another speech segment
    ```
    - The `path` column is the relative path to the audio file.
    - The `sentence` column is the corresponding transcription.
  - `clips/`: Directory for actual audio files, supporting multi-level subdirectories.

## Training Method

1. **Install Dependencies**  
   Please install Python 3.8+ and the following packages (virtual environment recommended):
   ```
   pip install torch transformers datasets evaluate
   ```

2. **Prepare Corpus**  
   Place your speech data and annotation files according to the format described above.

3. **Run Training Script**  
   You can directly execute `run.sh` or modify parameters as needed:
   ```bash
   bash run.sh
   ```
   Main parameter descriptions:
   - `--model_name_or_path`: Pre-trained model name (e.g., openai/whisper-large-v3)
   - `--corpus_data_dir`: Corpus directory (e.g., sample_corpus)
   - `--dataset_config_name`: Dataset combination (e.g., train_ds_01+train_ds_02)
   - `--language`: Language code (e.g., zh, en, nan, hak)
   - For other parameters, refer to `run.sh` and `train_asr.py`.

4. **Training Results**  
   After training, the model and related configurations will be saved in the `output/` directory.

## Pre-trained Models

- Pre-trained models for Mandarin, Taiwanese, Hakka, and English are stored in the `models/` directory, including:
  - `model.bin`: Model weights
  - `config.json`, `preprocessor_config.json`, `tokenizer.json`, `vocabulary.json`: Model configuration and vocabulary files

## Inference/Speech Recognition

You can use HuggingFace Transformers or write your own inference script to load the models in the `models/` directory for speech recognition.

## References

(*Please describe the project references here*)

- The training workflow of this project is adapted and optimized from HuggingFace Transformers speech recognition example scripts.
- For custom datasets or languages, please refer to the comments and parameter descriptions in `train_asr.py`.

### Citation

(*Please list the main contributors and initiators of the project here*)

If you use this project, please cite it as follows:

```yaml
cff-version: 1.2.0
title: "Automatic Speech Recognition (ASR) Project"
authors:
  - family-names: "Hsieh"
    given-names: "Archer"
    affiliation: "Taiwan Mobile Co., Ltd"
date-released: "2025-07-14"
version: "1.0.0"
abstract: |
  This project provides a comprehensive framework for Automatic Speech Recognition (ASR), supporting multilingual speech processing and fine-tuning capabilities. It includes pre-trained models for Mandarin, Taiwanese, Hakka, and English, and tools for speech-to-text conversion and spoken language identification.

keywords:
  - ASR
  - Automatic Speech Recognition
  - Multilingual Speech Processing
  - Speech-to-Text
  - Open Source

repository-code: "https://github.com/your-repo/asr-project"
license: "MIT"
```

---

For further assistance, please leave a message in Issues or contact the project maintainer. 