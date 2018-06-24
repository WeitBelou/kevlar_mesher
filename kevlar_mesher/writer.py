import pathlib

from vtk import vtkXMLDataSetWriter

from . import geo


def save(mesh: geo.Mesh, out_dir: str, name: str):
    out = pathlib.Path(out_dir)
    out.mkdir(exist_ok=True)
    out /= pathlib.Path(f'{name}.vtu')

    grid = mesh.make_vtu_grid()

    writer = vtkXMLDataSetWriter()
    writer.SetFileName(str(out.absolute()))
    writer.SetInputData(grid)
    writer.Write()
