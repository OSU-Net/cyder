# Installation

- Clone the repo and cd into it.
- (*optional*) Create and activate a virtualenv:

    ```bash
virtualenv .env
source .env/bin/activate
    ```
    
- Install dependencies:

    ```bash
pip install -r requirements/prod.txt
    ```
    
# Usage

- (*if you use a virtualenv and haven't activated it in this shell session*) Activate the virtualenv:

    ```bash
source .env/bin/activate
    ```
    
- Compare some files:

    ```bash
python compare.py test1.conf test2.conf
    ```
