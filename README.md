# julep-buildathon
Generate a hero from a linkedin profile and create 
a twelve pane story!


## Setup
Copy .env.example to .env and fill the tokens.
```bash
poetry install
```

## To run
```python
from storygenerator import main

main.generate_story()

# optionally provide a linked in url to generate a hero
# main.generate_story(li_url=<some_linkedin_url>)
```

From command line:
```bash
python storygenerator/main.py
```