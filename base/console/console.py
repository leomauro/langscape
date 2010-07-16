import langscape
from langscape.trail.nfaparser import NFAParser as Parser
from langscape.util.path import path
from langscape.base.display import DisplayMixin
from langscape.ls_exceptions import*
from langscape.util import get_traceback
import pprint
import sys
import os
import traceback
import warnings
import __main__
__main__.__dict__["__"] = __main__


__all__ = ["User", "LSConsole"]

class NoCompilationWarning(Warning): pass

warnings.simplefilter("once", NoCompilationWarning)

COMPILER_FLAGS = PyCF_DONT_IMPLY_DEDENT = 0x200   # ???

class User:
    '''
    Used to mediate or simulate user actions
    '''
    def get_input(self, prompt):
        return raw_input(prompt)

class ConsoleBase(object):
    def at_exit(self):
        raise NotImplementedError

    def try_parse(self):
        raise NotImplementedError

    def compile_cst(self, cst):
        raise NotImplementedError

    def write(self, data):
        sys.stdout.write(data)

    def input(self, prompt):
        """
        Wraps raw_input. Override this method in subclasses to customize input behaviour.
        @param prompt: prompt to be printed at input.
        """
        return raw_input(prompt)

    def reset(self):
        self.parseTree   = None
        self.line_buffer = []
        self.nl_count    = 2
        self.parse_error = (None, None)

    def compile_source(self, *args):
        if args[0] != '':
            return self.langlet.target.compiler.compile_source(*args)
        else:
            return ''

    def interact(self):
        self.at_start()
        try:
            gen_process = self.process_line()
            line = None
            while True:
                try:
                    prompt = gen_process.send(line)
                    line   = self.user.get_input(prompt)
                except StopIteration:
                    break
        finally:
            self.at_exit()

    def process_line(self):
        '''
        Processes one line of code in an interactive loop.

        This implementation uses two flags to determine the state of user input processing ::

            - force_more: true if command is incomplete. Otherwise false.
            - guess_more: true if command is incomplete or if it's complete but one more empty
              line or newline character is acceptable. Otherwise false.

        The ``guess_more`` flag is introduced instead of hypothetical line break trailers and
        maybe_compile cruft of the codeop.py stdlib implementation.
        '''
        force_more = False
        guess_more = False
        self.reset()
        while 1:
            try:
                if force_more or guess_more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = yield prompt  # receive user input here
                    line = line.replace('\r', '\n') # hmm...
                    self.line_buffer.append(line)
                    try:
                        if line:
                            source    = self.prepare_source()  # line-buffer -> source
                            tokstream = self.try_tokenize(source)
                            self.parseTree = self.try_parse(tokstream)
                        else:
                            guess_more = False
                        if not self.parseTree:
                            if line:
                                force_more = True
                            else:
                                self.nl_count -=1
                                if self.nl_count == 0:
                                    exc, msg = self.parse_error
                                    self.reset()
                                    force_more = False
                                    if exc:
                                        raise exc, msg.formatter()
                                elif not force_more:
                                    self.reset()
                            continue
                        elif force_more:
                             guess_more = True
                             force_more = False
                             continue
                        if not force_more and not guess_more:
                            code = self.compile_cst(self.parseTree)
                            self.reset()
                    except (EOFError, KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        self.reset()
                        force_more = guess_more = False
                        self.showtraceback()
                except EOFError:
                    self.write("\n")
                    break
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.reset()
                force_more = guess_more = False
            except SystemExit:
                break

    def runcode(self, code):
        """
        Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.

        (copied from Lib/code.py)
        """
        try:
            exec code in self.dct # self.locals
        except SystemExit:
            raise
        except:
            self.showtraceback()

    def showtraceback(self):
        self.write(get_traceback())

    def at_start(self):
        raise NotImplementedError


class LSConsole(ConsoleBase, DisplayMixin):
    '''
    Console object used to handle user input.

    This console object is to some extend a redesign of the InteractiveConsole object of the stdlib.

        - tryParse, compile_cst and runcode are clearly separated from each other and can be adapted
          in subclasses.
        - the interact method is removed from cruft of codeop.py
        - some EE specifific methods are added used show CSTs, token streams and unparsed Python code
    '''
    def __init__(self, langlet,
                       name,
                       locals = None,
                       globals = None,
                       use_new_prompt   = True,
                       **kwd):
        self.user = User()
        self.locals  = __main__.__dict__ if locals is None else locals
        self.langlet = langlet
        self.console_name = name
        self.use_new_prompt = use_new_prompt
        self.line_buffer = []
        self.terminates  = True
        # debug options
        self._compiled = {}
        self.parse_error = None
        self.dct = {}


    def at_start(self):
        '''
        Method used at console start. Select right prompt and print header.
        '''
        if not self.use_new_prompt:
            return
        sys.ps1 = self.prompt = self.langlet.config.prompt
        sys.ps2 = "."*(len(self.prompt)-1)+" "
        if hasattr(self.langlet, "docs"):
            docs = self.langlet.docs
        else:
            docs = ""
        py_vers = " On Python %s"%sys.version
        if docs:
            langlet_doc = " Langlet documentation: %s"%docs
        else:
            langlet_doc = " Langlet documentation: not yet available."
        self._header_len =  max(len(py_vers),len(langlet_doc))+2
        print "_"*self._header_len
        print
        print " %s"% self.console_name
        print
        print py_vers
        if docs:
            print langlet_doc
        if hasattr(self,"additional_header_info"):
            print
            print  self.additional_header_info
            print
        print "_"*self._header_len
        print

    def at_exit(self):
        "reset default prompt"
        sys.ps1 = ">>> "
        sys.ps2 = "... "
        print "_"*self._header_len
        print

    def prepare_source(self):
        self.parse_error = (None, None)
        source = '\n'.join(self.line_buffer)+"\n"
        if source in ("quit\n",":quit\n"):  # special commands for console. "quit" is standard in 2.5
            raise SystemExit
        return source

    def transform(self, parse_tree, **kwd):
        show_source = self.langlet.options["show_source"]
        self.langlet.options["show_source"] = False
        cst = self.langlet.transform(parse_tree, **kwd)
        self.langlet.target.projection(cst)
        self.langlet.options["show_source"] = show_source
        return cst

    def compile_cst(self, parse_tree):
        """
        Transforms langlet expr/statement into one or more Python
        statements. Compile and execute those statements.
        @param cst: langlet cst
        """
        cst = self.transform(parse_tree, interactive=True)
        self.maybe_grammar_check(cst)
        sources = []
        for tree in self.langlet.target.fn.split(cst):
            src = self.langlet.target.unparse(tree)
            if src not in ("", "\n", "\r"):
                sources.append(src)
        try:
            if self.langlet.options.get("parse_only"):
                return # parsed
            for src in sources:
                if not self._compiled.get(src):
                    _code = self.compile_source(src,"<input>","single", COMPILER_FLAGS)
                    self._compiled[src] = _code
        finally:
            self.maybe_show_source("\n".join(sources))
        for src in sources:
            self.runcode(self._compiled[src])

    def try_tokenize(self, source):
        try:
            tokstream = self.langlet.tokenize(source)
        except LexerError, err:
            if err.token[1] in ('\n', '\r', ''):
                self.parse_error = (LexerError, err)
                raise   # ?
            else:
                raise   # ??
        return tokstream

    def try_parse(self, tokstream):
        # Parse potentially incomplete langlet statement.
        # Following actions are possible:
        # 1) Complete langlet statement could be parsed. Parse tree is returned.
        # 2) Langlet statement incomplete. Needs more user input. Nothing is returned.
        # 3) Syntax error detected within langlet statement. SyntaxError exception is raised.
        try:
            parseTree = self.langlet.parse(tokstream)
            return parseTree
        except ParserError, err:
            self.parse_error = (ParserError, err)
            if err.token[1].strip() == '':         # ugly but not too constraining
                return
            else:
                raise
        except TokenError, err:
            return
