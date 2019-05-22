source venv/bin/activate
export PYTHONPATH=./src:./plugins
python src/main.py --data data/AAPS-AAPS18_export_all.json --rules rules/rules.json $@

