# ans-project
Little project for our applied network sciences class

# Goals
We want to work on the same idea as this (study)[https://doi.org/10.1073/pnas.2313377121], which analysed whether the youtube algorithm leads to radicalization. We would like to explore the way political content on youtube networks and whether any structures emerge upon clicking on the next video starting from a certain point.

# Usage
We used poetry with a venv in the project directory to manage all the packages. Just execute the following commands to make sure poetry is installed and a venv is initialzed: 
```bash
pip install poetry
python -m venv .venv
poetry install
``` 
Once poetry installed all packages you can run python files by just running: `poetry run python path/to/script.py`. And if using Jupyter you can select the .venv/bin/python file for the kernel.

# Create a Run in YouTube
To run thorough youtube you can use the YouTube.py script by executing `poetry run python scripts/YouTube.py`. With `poetry run scripts/YouTube.py --help` you can see a list of arguments including how to specify a training list. To create a training list you can create a file in the VideoLists directory and fill it with YouTube urls.

# Create a Graph of runs
To create a graph of your different runs you must manually select the runs you want to plot in the runs directory and move/copy them to a directory you created in selected runs. Then you can Execute a script like the one found in scripts/create_graph.py (`poetry run python scripts/create_graph.py`) or use the Jupyter notebook in networkgraph/plot.ipynb.

# Stats
The statistical analysis found in the presentation was done using the notebook statistics/stats.ipynb

