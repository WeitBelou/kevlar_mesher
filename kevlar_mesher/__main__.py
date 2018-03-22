from . import args
from . import config


def main():
    cmd_args = args.CommandLineArgs()
    cfg = config.parse(cmd_args.config)
    print(cfg)


if __name__ == '__main__':
    main()
