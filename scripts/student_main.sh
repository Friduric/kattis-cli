source venv/bin/activate
export PYTHONPATH=./src:./plugins
python src/main.py --teacher --detailed --data data/my-data.json --rules rules/rules.json $@
