import os
from io import BytesIO
from operator import attrgetter

from PIL import Image

from mlab_viewer.config import get_config

os.environ["OVITO_GUI_MODE"] = "1"

from PySide6.QtCore import QBuffer
from PySide6.QtGui import QImage

from mlab_tools.adapters.ovito_adapter import configuration_to_datacollection
from mlab_tools.structures import MLABConfiguration, MLABSection

from ovito.pipeline import Pipeline, StaticSource
from ovito.vis import Viewport, TachyonRenderer, CoordinateTripodOverlay


def render_images(section: MLABSection) -> dict[str, dict[str, QImage]]:
    min_energy_conf = min(section.configurations, key=attrgetter("energy"))
    max_energy_conf = max(section.configurations, key=attrgetter("energy"))

    image_size = (get_config()["rendering"]["width"], get_config()["rendering"]["height"])

    print("\rrendering minimum energy configuration ... ", end="")
    min_images = _render_images_configuration(min_energy_conf, size=image_size)
    print("\rrendering maximum energy configuration ... ", end="")
    max_images = _render_images_configuration(max_energy_conf, size=image_size)

    return {
        "min": min_images,
        "max": max_images,
    }


def _render_images_configuration(configuration: MLABConfiguration, size: tuple[int, int]) -> dict[str, Image]:
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
    images["perspective"] = _qt_to_pil(vp.render_image(size=size, renderer=renderer))

    vp.type = Viewport.Type.Front
    vp.zoom_all(size=size)
    images["front"] = _qt_to_pil(vp.render_image(size=size, renderer=renderer))

    vp.type = Viewport.Type.Top
    vp.zoom_all(size=size)
    images["top"] = _qt_to_pil(vp.render_image(size=size, renderer=renderer))

    pipeline.remove_from_scene()

    return images


def _qt_to_pil(image: QImage) -> Image:
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    image.save(buffer, "png")
    return Image.open(BytesIO(buffer.data()))
