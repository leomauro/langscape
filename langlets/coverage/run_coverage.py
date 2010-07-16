import langlet_config as config
import langscape.base.loader as loader

if __name__ == '__main__':
    (options, args) = config.opt.parse_args()
    langlet_obj = loader.load_langlet(config.langlet_name, **options.__dict__)
    if args:
        module = args[-1]
        langlet_obj.options["start_module"] = module
        langlet_obj.run_module(module)
    else:
        console = langlet_obj.console()
        console.interact()

