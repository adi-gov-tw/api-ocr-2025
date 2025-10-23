<h4 align="center">
    <p>
        <b>繁體中文</b> |
        <a href="">English</a>
    </p>
</h4>

# ASR 多語言訓練專案（國語/台語/客語/英語）

(*此處需描述標案、專案正式名稱，以及專案簡述*)

本專案提供一套自動語音辨識（ASR, Automatic Speech Recognition）模型訓練流程，並附有已訓練好的國語、台語、客語、英語模型。你可以根據自己的語音資料進行微調（fine-tune），或直接使用現有模型進行語音辨識。

## 目錄結構

(*此處需描述專案程式碼目錄結構*)

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

### 資料夾說明

(*此處需描述專案程式碼檔案細節*)

- **sample_corpus/**  
  存放語音資料與標註檔案，每個子資料夾（如 `train_ds_01`、`train_ds_02`）代表一個資料集。每個資料集包含：
  - `train.tsv`、`test.tsv`、`validated.tsv`：標註檔案，以Tab分隔，包含語音檔案路徑與對應轉寫文字。
  - `clips/`：存放實際語音檔案，支援多層子目錄。

- **models/**  
  存放已訓練好的國語、台語、客語、英語模型，包含：
  - `model.bin`：模型權重檔案。
  - `config.json`、`preprocessor_config.json`、`tokenizer.json`、`vocabulary.json`：模型設定與詞彙表。

- **train_asr.py**  
  訓練腳本，用於微調或訓練ASR模型。

- **run.sh**  
  執行訓練的腳本，可根據需求修改參數。

- **README.md**  
  專案說明文件，提供使用指南與參考資訊。

## 語料格式說明

- 語音資料與標註檔案需放在 `sample_corpus` 目錄下，每個子資料夾（如 `train_ds_01`、`train_ds_02`）代表一個資料集。
- 每個資料集需包含：
  - `train.tsv`、`test.tsv`、`validated.tsv`：標註檔案，格式如下（以Tab分隔）：
    ```
    path    sentence
    audio_train_01_1.wav    這是一段語音
    audio_train_01_2.wav    另一段語音
    ```
    - `path` 欄位為語音檔案的相對路徑。
    - `sentence` 欄位為對應的語音轉寫文字。
  - `clips/`：實際語音檔案存放處，支援多層子目錄。

## 訓練方法

1. **安裝依賴套件**  
   請先安裝 Python 3.8+ 及以下套件（建議使用虛擬環境）：
   ```
   pip install torch transformers datasets evaluate
   ```

2. **準備語料**  
   依照上述格式放置語音資料與標註檔案。

3. **執行訓練腳本**  
   可直接執行 `run.sh`，或根據需求修改參數：
   ```bash
   bash run.sh
   ```
   主要參數說明：
   - `--model_name_or_path`：預訓練模型名稱（如 openai/whisper-large-v3）
   - `--corpus_data_dir`：語料資料夾（如 sample_corpus）
   - `--dataset_config_name`：資料集組合（如 train_ds_01+train_ds_02）
   - `--language`：語言代碼（如 zh、en、nan、hak）
   - 其他參數可參考 `run.sh` 及 `train_asr.py`。

4. **訓練結果**  
   訓練完成後，模型與相關設定會儲存在 `output/` 目錄。

## 已訓練模型

- 已訓練好的國語、台語、客語、英語模型存放於 `models/` 目錄，包含：
  - `model.bin`：模型權重
  - `config.json`、`preprocessor_config.json`、`tokenizer.json`、`vocabulary.json`：模型設定與詞彙表

## 推論/辨識語音

可利用 HuggingFace Transformers 或自行撰寫推論腳本，載入 `models/` 內的模型進行語音辨識。

## 參考

(*此處需描述專案參考資料*)

- 本專案訓練流程基於 HuggingFace Transformers 語音辨識範例腳本進行改寫與優化。
- 若需自訂資料集或語言，請參考 `train_asr.py` 內部註解與參數說明。

### 引用

(*此處需列出專案主要貢獻者、發起人*)

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

如需更多協助，請於 Issues 留言或聯絡專案維護者。 