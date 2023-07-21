import os
os.environ["OVITO_GUI_MODE"] = "1"

from PySide6.QtGui import QImage

from internal.adapters.ovito_adapter import configuration_to_datacollection
from internal.structures import MLABConfiguration

from ovito.pipeline import Pipeline, StaticSource
from ovito.vis import Viewport, TachyonRenderer, CoordinateTripodOverlay


def render(configuration: MLABConfiguration, size: tuple[int, int]) -> dict[str, QImage]:
    data = configuration_to_datacollection(configuration)

    pipeline = Pipeline(source=StaticSource(data=data))
    pipeline.add_to_scene()

    renderer = TachyonRenderer()

    vp = Viewport()
    tripod = CoordinateTripodOverlay(size=0.07)
    vp.overlays.append(tripod)

    images = {}

    vp.type = Viewport.Type.Perspective
    vp.camera_dir = (4, 10, -5)
    vp.zoom_all(size=size)
    images["perspective"] = vp.render_image(size=size, renderer=renderer)

    vp.type = Viewport.Type.Front
    vp.zoom_all(size=size)
    images["front"] = vp.render_image(size=size, renderer=renderer)

    vp.type = Viewport.Type.Top
    vp.zoom_all(size=size)
    images["top"] = vp.render_image(size=size, renderer=renderer)

    pipeline.remove_from_scene()

    return images
