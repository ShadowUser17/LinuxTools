### Scripts for Linux automatization.

#### Configure environment:
```bash
python3 -m venv --upgrade-deps env && \
./env/bin/pip3 install -r requirements.txt
```

#### Validate project files:
```bash
./env/bin/flake8 --ignore="E501" *.py
```
