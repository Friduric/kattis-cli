source venv/bin/activate
export PYTHONPATH=./src:./plugins
python src/main.py --student --detailed --data data/my-data.json --rules rules/rules.json $@
