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
