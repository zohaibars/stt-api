# stt-api



## Getting Started

Follow the steps below to get started with this project:

## Using This Repository
### Environment
* Python 3.10.12
* Cuda 11.2
* Torch 2.4.1+cu121
### Installation
1. Clone the repository
```
https://github.com/AI-TEAM-R-D-Models/stt-api
```

2. Install the requirements
```
python3 -m venv myenv

source myenv/bin/activate

pip install -r requirements.txt
```

```

3. Prepare Dataset
```
    Dataset/
    │
    ├── Custom_dataset/
    │   ├── folder1/
    │   │   ├── audio1.wav
    │   │   ├── audio1.txt
    │   │   └── ...
    │   ├── folder2/
    │   │   ├── audio1.wav
    │   │   ├── audio1.txt
    │   │   └── ...
    |   │── ├── folder3/
    │   │   ├── audio1.wav
    │   │   ├── audio1.txt
    │   │   └── ...

```
4. convert 16000hz sampling rate
```

```
cd finetune-whisper
python3 convert_sampling_rate.py

```

```
5. Generate audio_paths and text file
```
python GenerateDataPaths.py
```
6. Split Dataset
```
python dataset_split.py 
```
7. FineTune
```
python train.py

```
8. Extract Model
```
python extract_model.py

```
cd APi
change model ID in inference.py
python3 app.py
```