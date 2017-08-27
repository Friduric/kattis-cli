source venv/bin/activate
export PYTHONPATH=./src:./plugins
python src/main.py --detailed --data data/AAPS-AAPS17_export_all.json --rules rules/rules.json $@

