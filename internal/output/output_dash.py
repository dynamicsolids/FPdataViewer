import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, html, dcc

from internal import rendering
from internal.structures import MLABSection, MLABSectionStats

_red = px.colors.qualitative.Plotly[1]
_green = px.colors.qualitative.Plotly[2]
_blue = px.colors.qualitative.Plotly[0]
_black = "black"


def create_annotation(x: float, text: str, color: str, shift: float | None = None) -> dict:
    shape = {
        "line": {"color": color, "dash": "dash", "width": 1},
        "x0": x,
        "x1": x,
        "y0": 0,
        "y1": 1,
        "xref": "x",
        "yref": "paper",
    }

    annotation = {
        "x": x,
        "y": 1,
        "xref": "x",
        "yref": "paper",
        "text": text,
        "showarrow": True,
        "arrowhead": 7,
    }

    if shift is not None:
        annotation.update({
            "ay": -shift,
            "ayref": "y",
        })

    return {
        "shapes": [shape],
        "annotations": [annotation]
    }


def merge_annotations(*annotations: dict) -> dict:
    return {
        "shapes": [annotation["shapes"][0] for annotation in annotations],
        "annotations": [annotation["annotations"][0] for annotation in annotations],
    }


def plot_energy(section: MLABSection):
    df = pd.DataFrame({
        "energy": [conf.energy for conf in section.configurations],
    })
    median = df["energy"].median()

    hist = go.Histogram(x=df["energy"], marker_color=_blue)
    annotations = create_annotation(median, f"median: {median:.1f} eV", _blue)
    layout = go.Layout(xaxis={"title": "energy [eV]"},
                       yaxis={"title": "count"},
                       **annotations)

    return go.Figure(data=hist, layout=layout)


def plot_pressure(section: MLABSection):
    df = pd.DataFrame({
        "pressure": [conf.stress.get_mechanical_pressure() for conf in section.configurations],
    })
    median = df["pressure"].median()

    hist = go.Histogram(x=df["pressure"], marker_color=_blue)
    annotations = create_annotation(median, f"median: {median:.1f} kbar", _blue)
    layout = go.Layout(xaxis={"title": "mechanical pressure [kbar]"},
                       yaxis={"title": "count"},
                       **annotations)

    return go.Figure(data=hist, layout=layout)

def plot_force(section: MLABSection):
    df = pd.DataFrame([(*np.abs(force), np.linalg.norm(force)) for conf in section.configurations for force in conf.forces], columns=["x", "y", "z", "||.||"])
    median = df["||.||"].median()

    hist_x = go.Histogram(x=df["x"], opacity=0.7, name="x", marker_color=_red)
    hist_y = go.Histogram(x=df["y"], opacity=0.7, name="y", marker_color=_blue)
    hist_z = go.Histogram(x=df["z"], opacity=0.7, name="z", marker_color=_green)
    hist_l = go.Histogram(x=df["||.||"], opacity=0.7, name="||.||", marker_color=_black)

    hist = [hist_x, hist_y, hist_z, hist_l]
    annotations = create_annotation(median, f"median: {median:.1f} eV/ang", _black)
    layout = go.Layout(barmode="overlay",
                       xaxis={"title": "force [eV/ang]"},
                       yaxis={"title": "count"},
                       **annotations)

    return go.Figure(data=hist, layout=layout)


def plot_lattice(section: MLABSection):
    df = pd.DataFrame([(np.linalg.norm(conf.lattice_vectors[0]), np.linalg.norm(conf.lattice_vectors[1]), np.linalg.norm(conf.lattice_vectors[2])) for conf in section.configurations], columns=["a", "b", "c"])
    median_a = df["a"].median()
    median_b = df["b"].median()
    median_c = df["c"].median()

    hist_a = go.Histogram(x=df["a"], opacity=0.7, name="a", marker_color=_red)
    hist_b = go.Histogram(x=df["b"], opacity=0.7, name="b", marker_color=_blue)
    hist_c = go.Histogram(x=df["c"], opacity=0.7, name="c", marker_color=_green)

    hist = [hist_a, hist_b, hist_c]
    annotations = merge_annotations(
        create_annotation(median_a, f"median: {median_a:.1f} eV/ang", _red, shift=25.),
        create_annotation(median_b, f"median: {median_b:.1f} eV/ang", _blue, shift=40.),
        create_annotation(median_c, f"median: {median_c:.1f} eV/ang", _green, shift=55.),
    )
    layout = go.Layout(barmode="overlay",
                       xaxis={"title": "lattice vector length [ang]"},
                       yaxis={"title": "count"},
                       **annotations)

    return go.Figure(data=hist, layout=layout)


def plot_info(section: MLABSection):
    atom_repr = ", ".join([f"{name} ({number})" for name, number in section.number_of_atoms_per_type])
    energies = [conf.energy for conf in section.configurations]
    mean_energy = np.mean(energies)
    std_energy = np.std(energies)

    return [
        html.P([
            f"Name      : {section.name}", html.Br(),
            f"Atoms     : {section.number_of_atoms}", html.Br(),
            f"Atom types: {atom_repr}", html.Br(),
            f"Structures: {len(section.configurations)} / {len(section.source.configurations)}",
        ]),
        html.P([
            f"Energy: {mean_energy:.1f} eV \u00B1 {2 * std_energy:.2f} eV", html.Br(),
            f"Energy: {mean_energy:.1f} eV \u00B1 {2 * std_energy:.2f} eV", html.Br(),
            f"Energy: {mean_energy:.1f} eV \u00B1 {2 * std_energy:.2f} eV", html.Br(),
            f"Energy: {mean_energy:.1f} eV \u00B1 {2 * std_energy:.2f} eV",
        ]),
    ]


def cardify(*component, title=None):
    if title is None:
        return dbc.Card(dbc.CardBody(*component))
    else:
        return dbc.Card(dbc.CardBody([html.H5(title, className="card-title"), *component]))


def run(section: MLABSection, stats: MLABSectionStats):
    # fig = px.scatter(x=range(10), y=range(10))
    # fig.write_html("test.html", include_plotlyjs="cdn")

    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    rendering.render(section)

    app.layout = dbc.Container([
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H1(f"{section.name}", style={"textAlign": "center"}),
                cardify(plot_info(section)),
            ], style={"whiteSpace": "pre-wrap"}),
            # dbc.Col(cardify(html.Img(src="https://placehold.co/600x400")), width=4),
            # dbc.Col(cardify(html.Img(src="https://placehold.co/600x400")), width=4),
            dbc.Col(dbc.Card([
                dbc.CardImg(src=dash.get_asset_url("front.jpg"), top=True),
                dbc.CardImgOverlay([
                    dbc.CardBody(html.H5("Front (minimum energy)", className="card-title"))
                ]),
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardImg(src=dash.get_asset_url("top.jpg"), top=True),
                dbc.CardImgOverlay([
                    dbc.CardBody(html.H5("Top (minimum energy)", className="card-title"))
                ]),
            ]), width=4),
        ], align="center"),
        html.Br(),
        dbc.Row([
            dbc.Col(cardify(dcc.Graph(figure=plot_energy(section)), title="Energy")),
            dbc.Col(cardify(dcc.Graph(figure=plot_lattice(section)), title="Lattice parameters")),
        ], align="center"),
        html.Br(),
        dbc.Row([
            dbc.Col(cardify(dcc.Graph(figure=plot_force(section)), title="Force")),
            dbc.Col(cardify(dcc.Graph(figure=plot_pressure(section)),  title="Pressure")),
        ], align="center"),
        html.Br(),
        dbc.Row([
            dbc.Col(cardify(dcc.Graph(figure=plot_energy(section)), dcc.Graph(figure=plot_energy(section)), title="Radial Distribution Functions")),
        ], align="center"),
        html.Br(),
    ], fluid=True, style={"fontFamily": "Consolas"})

    app.run_server(debug=False)
