import numpy as np
from ovito.data import DataCollection, ParticleType, SimulationCell

from mlab.mlab import MLABConfiguration


def configuration_to_datacollection(conf: MLABConfiguration) -> DataCollection:
    def create_default_particle_type(name: str, id: int) -> ParticleType:
        type = ParticleType(name=name, id=id)
        type.load_defaults()
        return type

    data = DataCollection()
    particles = data.create_particles()

    particles.create_property("Position", data=conf.positions)

    types = [create_default_particle_type(type, i) for i, (type, _) in enumerate(conf.header.number_of_atoms_per_type)]

    type_id_lookup = {type: i for i, (type, _) in enumerate(conf.header.number_of_atoms_per_type)}
    type_lookup = conf.header.generate_type_lookup()

    type_property = particles.create_property("Particle Type", data=[type_id_lookup[type] for type in type_lookup])
    for type in types:
        type_property.types.append(type)
    for i in range(conf.header.number_of_atoms):
        type_property[i] = type_id_lookup[type_lookup[i]]

    cell = SimulationCell(pbc=(True, True, True))
    cell[...] = np.row_stack([conf.lattice_vectors, [0, 0, 0]]).transpose()
    cell.vis.line_width = 0.1
    data.objects.append(cell)

    return data
