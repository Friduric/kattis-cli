source venv/bin/activate
export PYTHONPATH=./src:./plugins
echo "Downloading your kattis data and putting it in data/my-data.json"
python src/scrape.py > data/my-data.json
