# Installation

- Clone the repo and cd into it.
- (<em>optional</em>) Create and activate a virtualenv:

    ```bash
virtualenv .env
source .env/bin/activate
    ```
    
- Install dependencies:

    ```bash
pip install -r requirements/prod.txt
    ```
    
# Usage

- (<em>if you use a virtualenv and haven't activated it in this shell session</em>) Activate the virtualenv:

    ```bash
source .env/bin/activate
    ```
    
- Compare some files:

    ```bash
python compare.py test1.conf test2.conf
    ```
