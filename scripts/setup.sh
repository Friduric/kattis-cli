mkdir -p data
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt

echo "Virtulenv created and dependencies installed."
