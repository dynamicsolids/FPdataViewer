import os
os.environ["OVITO_GUI_MODE"] = "1"

from operator import attrgetter

from PySide6.QtGui import QImage

from internal.adapters.ovito_adapter import configuration_to_datacollection
from internal.structures import MLABSection

from ovito.pipeline import Pipeline, StaticSource
from ovito.vis import Viewport, TachyonRenderer


def render(section: MLABSection, size: tuple[int, int]) -> tuple[QImage, QImage]:
    configuration = min(section.configurations, key=attrgetter("energy"))

    data = configuration_to_datacollection(configuration)

    pipeline = Pipeline(source=StaticSource(data=data))
    pipeline.add_to_scene()

    renderer = TachyonRenderer()

    vp = Viewport(type=Viewport.Type.Top)
    vp.zoom_all(size=size)
    top = vp.render_image(size=size, renderer=renderer)

    vp = Viewport(type=Viewport.Type.Front)
    vp.zoom_all(size=size)
    front = vp.render_image(size=size, renderer=renderer)

    return top, front
