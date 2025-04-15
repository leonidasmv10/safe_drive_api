#!/bin/bash

echo "Update virtual environment..."
python -m pip install --upgrade pip

echo "Installing virtualenv..."
python -m pip install virtualenv

echo "Creating virtual environment..."
python -m venv env

echo "Activating virtual environment..."
source env/bin/activate

echo "Installing API requirements..."
pip install -r requirements.txt

echo "Installation completed."
read -p "Press Enter to exit..."
