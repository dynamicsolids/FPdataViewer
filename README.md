WIP
---
````
usage: mlab.py [-h] [-c file] [-s] [-g] [-r] [-d] [file]

reads ML_AB files and displays various statistics

positional arguments:
  file                  file to read - if directory is supplied, looks for
                        ML_AB file - defaults to working directory

options:
  -h, --help            show this help message and exit
  -c file, --config file
                        config file - will be created if it does not exist -
                        defaults to "mlab_config.json"
  -s, --separate        produces separate figures for each plot

modules:
  -g, --general         only display general information & histograms
  -r, --rdf             only display radial distribution functions
  -d, --descriptors     only display SOAP descriptors
````