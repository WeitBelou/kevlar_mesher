#!/usr/bin/pvpython
import os

from paraview.simple import *

name_template = 'out/density_{}_radius_{}_amplitude_{}-{:04d}.vtu'
result_template = 'out/img/density_{}_radius_{}_amplitude_{}/{}.png'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

vtu_dir = os.path.join(BASE_DIR, 'out')

screenshots_dir = os.path.join(BASE_DIR, 'out', 'img')
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)

reader = XMLUnstructuredGridReader()

for density in [1, 2, 5]:
    for radius in [1, 5, 10]:
        for amplitude in [0.1, 1, 10]:
            for (idx, step) in enumerate([0, 50, 100, 150, 200, 249]):
                base_name = 'density_{}_radius_{}_amplitude_{}'.format(density, radius, amplitude)
                vtu_file = os.path.join(BASE_DIR, 'out', '{}-{:04d}.vtu'.format(base_name, step))
                reader.FileName = [vtu_file]
                reader.UpdatePipeline()

                # position camera
                view = GetActiveView()
                if not view:
                    # When using the ParaView UI, the View will be present, not otherwise.
                    view = CreateRenderView()

                view.CameraViewUp = [0.1, 0.5, 0.05]
                view.CameraFocalPoint = [50, 50, 0]
                view.CameraViewAngle = 45
                view.CameraPosition = [20, -55, 65]

                # draw the object
                Show()

                # set image size
                view.ViewSize = [640, 480]  # [width, height]

                dp = GetDisplayProperties()

                # set point size
                dp.PointSize = 2

                # set representation
                dp.Representation = "Surface"

                Render()

                # save screenshot
                image_dir = os.path.join(screenshots_dir, base_name)
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)

                WriteImage(os.path.join(image_dir, '{}.png'.format(idx+1)))
