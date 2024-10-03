# INSA 5IF - OT8 - TP2

## Usage

### Installation

```bash
# create a virtual environment
python3 -m venv venv

# activate the virtual environment
source venv/bin/activate

# install the requirements
pip install -r requirements.txt
```

### Execution

With a single URL :

```bash
python -m scraper -u https://my.url/my-article
```

With a list of URLs from a file :

```bash
python -m scraper -f urls.txt
```