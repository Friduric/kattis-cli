source venv/bin/activate
export PYTHONPATH=./src:./plugins
python src/scrape.py > data/my-data.json
