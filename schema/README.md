[README.md](https://github.com/user-attachments/files/25780408/README.md)
# standards/

This folder contains the versioned MARS schema files.

| File | Version | Status |
|------|---------|--------|
| [MARS_v0.9.json](./MARS_v0.9.json) | v0.9 | Public Draft |

## Schema Validation

```bash
# Python
pip install jsonschema
python -c "import json, jsonschema; jsonschema.validate(json.load(open('your_record.json')), json.load(open('MARS_v0.9.json'))); print('Valid MARS record.')"
```

Previous versions are archived here as the standard evolves.
