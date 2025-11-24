# folketingetApi

# Create a embedding_model folder in root of project

mkdir embedding_model

# Download the model and store locally

Link: https://drive.google.com/drive/folders/1IETGrF30kq8ESCUntfXONUVts1Ms9tTx?usp=drive_link
This FastAPI script uses v5 of the model. Download and place the model into the folder embedding_model.

# Install dependencies

pip install -r requirements.txt

# Run

uvicorn search:app --reload --host 0.0.0.0 --port 5001

# Test

using the endpoint /search

# For import_data

check installed cuda version in terminal
nvidia-smi

# download cuda toolkit

download matching toolkit from nvidia https://developer.nvidia.com/cuda-toolkit

# uninstall old torch version

pip uninstall torch torchvision torchaudio

# install matching version

For version 12.8 of cuda toolkit, the latest stable version of torch is 12.1
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

if you have a older or newer version, check what matches for you.

# run the script

if the above went smoothly, you should be able to run the script.
