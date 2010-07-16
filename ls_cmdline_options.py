'''
eeoptions.py defines general command line options for langscape.
'''
import os
import optparse
import sys

def scan_for_program(langlet, argv):
    '''
    Reads module.<ext> in command-line parameter list given <ext> is in the langlet suffixes.
    '''
    from langscape.base.importer import LangletHooks
    suffixes = [suffix[0] for suffix in LangletHooks(langlet).get_suffixes()]
    for i, arg in enumerate(argv[1:]):
        if arg[0] == "-":
            continue
        if any(arg.endswith(suffix) for suffix in suffixes):
            return i+1
    return -1

def parse_cmdline(langlet, opt):
    idx = scan_for_program(langlet, sys.argv)
    if idx == -1:  # no script args
        (options, args) = opt.parse_args()
    else:
        langlet_args, _ = sys.argv[:idx+1], sys.argv[idx:]
        (options, args) = opt.parse_args(args = langlet_args)
    setattr(langlet, "options", options.__dict__)
    return args



def record_rec_seen(option, opt_str, value, parser):
    if parser.rargs:
        v = parser.rargs[0] # consume the value
        if v.startswith("-"):
            setattr(parser.values, option.dest, "rec")
            return
        if v !="enum" and not os.sep in v and not v.startswith("+") and not v.endswith("+"):
            raise optparse.OptionValueError("value of --rec must be one of 'enum', '+<suffix>', '<prefix>+' or a filename of the form %s<filename>"%os.sep)
        setattr(parser.values, option.dest, v)
        del parser.rargs[:]
    else:
        setattr(parser.values, option.dest, "stdname")  # use stdname as default
                                                        # when option is set

##############################################################################################
#
#  Global option definitions
#
##############################################################################################

def getoptions():
    opt = optparse.OptionParser()
    opt.add_option("-b","--show-cst-before" ,dest="show_cst_before" ,help="show CST before transformation", action="store_true" )
    opt.add_option("-a","--show-cst-after" ,dest="show_cst_after" ,help="show CST after transformation",action="store_true")
    opt.add_option("-m","--show-marked-node" ,dest="show_marked_node" ,help="mark one or more different kinds of nodes in a CST",action="store", type = "string")
    opt.add_option("-t","--show-token",dest="show_token", help="show filtered token stream passed to the parser", action="store_true" )
    opt.add_option("--show-scan",dest="show_scan", help="show unfiltered token stream passed to the lexical post processor", action="store_true" )
    opt.add_option("-s","--show-source",dest="show_source", help="show unparsed source code", action="store_true" )
    opt.add_option("-v","--validate-cst",dest="cst_validation", help="CST validation against Python grammar", action="store_true" )
    opt.add_option("--re-compile",dest="re_compile", help="unconditional re-compilation of a source file.", action="store_true" )
    opt.add_option("--parse-only",dest="parse_only", help="terminate transformation after parsing", action="store_true" )
    #opt.add_option("--full-cst",dest="full_cst", help="display complete CST ( without possible omissions )", action="store_true" )
    opt.add_option("--rec", dest = "recording", help="records an interactive console session ", action="callback", callback=record_rec_seen)
    opt.add_option("--rep",dest="session", help="replays an interactive console session", action="store", type = "string" )
    opt.add_option("--dbg-lexer",dest="debug_lexer", help="display NFALexer debug information", action="store_true" )
    opt.add_option("--dbg-parser",dest="debug_parser", help="display NFAParser debug information", action="store_true" )
    opt.add_option("--dbg-import",dest="debug_importer", help="display eeimporter debug information", action="store_true" )
    opt.add_option("--build-nfa",dest="build_nfa", help="(re)builds lex_nfa and parse_nfa files", action="store_true" )
    opt.add_option("-r","--refactor-mode",dest="refactor_mode", help="in refactor mode source can be reconstructed exactly from a CST", action="store_true" )
    opt.add_option("--rs","--sr",dest="show_source_in_refactor_mode", help="compines options -r and -s", action="store_true" )
    return opt


