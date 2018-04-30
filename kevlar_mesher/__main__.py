from . import args
from . import config
from . import mesher


def main():
    cmd_args = args.CommandLineArgs()
    cfg = config.parse(cmd_args.config)
    print(cfg)

    mesh = mesher.create_mesh(cfg)
    mesh.save()

    mesh.plot()


if __name__ == '__main__':
    main()
