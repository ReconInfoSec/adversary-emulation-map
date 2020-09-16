# Adversary Emulation Maps
Generate an ATT&CK Navigator map from an adversary emulation plan.

This can be useful for visualizing the plan, or for building logical layers to analyze your existing defensive posture against a specific adversary.

## Installation
Using a virtual environment...

```bash
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python build_heatmap.py <name of plan> [optional flags]
```

Flags:
- `--output`: Name of the output file
- `--refresh-repo`: Clone the latest from the MITRE Adversary Emuation Repo

Example:
```bash
python build_heatmap.py fin6
```


## Using VSCode to check syntax
Edit `settings.json`

```json
"yaml.schemas": {
    "./.plans/format_schema.json": "*/Emulation_Plan/*.yaml"
}
```