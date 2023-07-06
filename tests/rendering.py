import os
os.environ["OVITO_GUI_MODE"] = "1"  # Request a session with OpenGL support

from ovito.data import DataCollection
from ovito.pipeline import Pipeline, StaticSource
from ovito.vis import Viewport, OpenGLRenderer

if __name__ == "__main__":
    data = DataCollection()
    particles = data.create_particles()

    particles.create_property("Position", data=[(0., 0., 0.), (0., 0., 2.)])

    pipeline = Pipeline(source=StaticSource(data=data))
    pipeline.add_to_scene()

    size = (800, 600)

    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 1, -1))
    vp.zoom_all(size=size)
    vp.render_image(size=size,
                    filename="a.png",
                    renderer=OpenGLRenderer())
