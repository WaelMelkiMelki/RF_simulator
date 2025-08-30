#!/bin/bash
# scripts/install_and_run.sh

# Vérifie si Python est installé
if ! command -v python3 &> /dev/null
then
    echo "Python 3 n'est pas installé"
    # Installation automatique pour différentes plateformes
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update && sudo apt install python3 python3-pip -y
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python
    elif [[ "$OSTYPE" == "msys" ]]; then
        # Télécharge et installe Python pour Windows
        PYTHON_URL="https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
        curl -O $PYTHON_URL
        start /wait python-3.10.11-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    fi
fi

# Installe les dépendances
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Lance l'application
if [[ "$OSTYPE" == "msys" ]]; then
    # Windows
    python src/main.py
else
    # macOS/Linux
    python3 src/main.py
fi
