# Prescriptor

<!-- PREREQUISITES AND INSTALLATIONS -->
## Getting Started
To test the web application, you need to create a virtual environment and install the dependencies.

### Prerequisites 
To test the web application, follow the instructions below and install the prerequisites.

Open Anaconda Prompt and Update conda environment
```
conda update conda
```

### Create Virtual Environment
Set up a virtual environment
```
conda create -n venv python=3.8
```
### Installation

Install dependencies in the virtual environment
```
pip install -r requirements.txt
``` 

Migrate Database and Run Server

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
``` 
