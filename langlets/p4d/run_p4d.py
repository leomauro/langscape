import langlet_config as config
import langscape.base.loader as loader
from langscape.util.path import path
import os

def convert2p4d(langlet, input_file):
    if langlet.options["flex"]:
        import langscape.base.importer as importer
        flexutils = importer.import_from_langlet(langlet, "langscape.langlets.p4d.flexutils")
        flexutils.convert2p4d(langlet, input_file)
    else:
        out, ext = input_file.splitext()
        out = out+".p4d"
        if ext in (".htm", ".html"):
            p4d_str = langlet.P4D.from_html(open(input_file).read()).p4dstr()
        else:
            p4d_str = langlet.P4D.from_xml(open(input_file).read()).p4dstr()
        open(out,"w").write("elm "+p4d_str)

def runflex(langlet, input_file):
    import langscape.base.importer as importer
    flexutils = importer.import_from_langlet(langlet, "langscape.langlets.p4d.flexutils")
    flexutils.runflex(langlet, input_file)

def autorun():
    (options, args) = config.opt.parse_args()
    langlet_obj = loader.load_langlet(config.langlet_name, **options.__dict__)

    if langlet_obj.options["xml2p4d"]:
        f = path(args[-1])
        if not f.isfile():
            if f[0] == '*':
                ext = f.splitext()[1]
                for fl in path(os.getcwd()).listdir():
                    if fl.ext == ext:
                        convert2p4d(langlet_obj, fl)
                return
            else:
                f = path(os.getcwd()).joinpath(f)
        convert2p4d(langlet_obj, f)
    elif langlet_obj.options["flex"]:
        f = path(os.getcwd()).joinpath(path(args[-1]))
        runflex(langlet, f)
        return
    elif args:
        module = args[-1]
        langlet_obj.run_module(module)
    else:
        console = langlet_obj.console()
        console.interact()

if __name__ == '__main__':
    autorun()


