# ML AB Viewer

Reads [VASP MLFF](https://www.vasp.at/wiki/index.php/Machine_learning_force_field_calculations:_Basics) [input and output files](https://www.vasp.at/wiki/index.php/ML_AB) (named ML_AB and ML_ABN) 
and graphs various statistics to provide a small overview of the file's content using matplotlib. 
Either produces an interactive overview (`--mode plt`) or saves to a file (`--mode pdf`). 

<details>
<summary>Table of Contents</summary>

- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Config](#config-file)

</details>

| ![rendered front page](images/image_a.png)                 | ![rendered image page](images/image_b.png)                |
|-----------------------------------------------------|----------------------------------------------------|
| ![rendered atom type page for bismuth](images/image_c.png) | ![rendered atom type page for oxygen](images/image_d.png) |

## Installation

```shell
pip install mlab_viewer # DOES NOT WORK YET
```

> Installation through pip will pull in a number of large libraries used in analysis, some of which may not be supported on Windows. 
> If this is not preferable, consider manually installing and using `--skip` to avoid said libraries (see dependencies and [options](#options)).

<details>
<summary>Dependencies</summary>

| Component                         | Dependencies (immediate)                                                                                                                                                                |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **required**                      | **[numpy](https://pypi.org/project/numpy/) [pandas](https://pypi.org/project/pandas/) [matplotlib](https://pypi.org/project/matplotlib/) [seaborn](https://pypi.org/project/seaborn/)** |
| **radial distribution functions** | **[numba](https://pypi.org/project/numba/)**                                                                                                                                            |
| **descriptors**                   | **[scikit-learn](https://pypi.org/project/scikit-learn/) [dscribe](https://pypi.org/project/dscribe/) (possible compatability issues)**                                                                                                                             |
| **rendering**                     | **[ovito](https://pypi.org/project/ovito/) [pyside6](https://pypi.org/project/PySide6/) [pillow](https://pypi.org/project/Pillow/)**                                                    |

</details>

## Usage

```shell
# Basic PDF generation
mlab_viewer examples/ML_AB overview.pdf

# Interactive plots
mlab_viewer examples/ML_AB --mode plt

# Use ML_AB(N) in working directory and output to ML_AB(N).pdf, additionally use custom config
mlab_viewer --config mlab_viewer.json

# Skip radial distribution functions and image rendering, rasterize remaining graphs
mlab_viewer --rasterize --skip rdf img
```

### Options

##### `--mode <[pdf]/plt/none>`, `-m`
Save to a PDF file (`pdf`, default), show interactive plots (`plt`), or only print to console (`none`).

##### `--config <file>`, `-c`
See [Config file](#config-file).

##### `--skip <rdf/desc/img>`, `-s`
Skip calculations for radial distribution functions (`rdf`), descriptors (`desc`), or image rendering (`img`). Multiple can be selected. Useful when only certain statistics are needed.

##### `--strict`, `-t`
Validates the input file. 
Some formats (like VASP's ML_AB) contain redundant or possibly self-contradictory information that can cause parsers to fail unpredictably. 
This option will check the input file against specifications to minimize these errors and help the user repair the broken file.

##### `--rasterize`, `-r`
Disables vector image format for plots and uses raster images. This can greatly reduce file size when many descriptors are being drawn. Simply feeds `rasterize=True` to matplotlib.

## Config file

Specifying a custom config will override settings from the default, which is located in [config.py](fpdata/render/config.py).

```json
{
  "global": {
    "bins": 100
  },
  "rdf": {
    "bins": 1000,
    "structures": 1.0,
    "r_min": 0.0,
    "r_max": "auto",
    "skip_pairs": []
  },
  "descriptors": {
    "structures": 1.0,
    "soap": {
      "r_cut": "auto",
      "n_max": 8,
      "l_max": 8
    }
  },
  "rendering": {
    "width": 1024,
    "height": 1024
  }
}
```

Most settings are self-explanatory, but more specifically:

- `"descriptors"`
  - See DScribe [documentation](https://singroup.github.io/dscribe/latest/doc/dscribe.descriptors.html). The inner content is fed to the respective (local) descriptor object. It should specify one of
    - `"soap"`
    - `"acsf"`
    - `"lmbtr"`
- `"rdf"`
  - `"skip_pairs"` is an array of values `"<atom 1>-<atom 2>"` (e.g. `"Bi-O"`). Usually RDF calculations are fast enough for this to be unnecessary.
- Anywhere
  - `"structures"` specify the number of structures to be included in some calculation, chosen at random. It should specify
    - `0.0 < x < 1.0` for a portion
    - `x > 1` for a specific number
  - `"auto"` will be replaced with the maximum possible radius such that radii never overlap in a periodic structure (the `non periodic distance` in the overview panel).
