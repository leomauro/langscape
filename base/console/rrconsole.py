####################################################################################
#
#  Enhanced console functionality: recording + replay
#
####################################################################################

from console import LSConsole, User

import re
import sys
import os
from langscape.util.path import path
import __main__
__main__.__dict__["__"] = __main__


class LastOutput(object):
    '''
    Stores last output. Used mostly for test purposes.
    '''
    def __init__(self):
        self.items = []

    def _get_s(self):
        return self.select()

    s = property(_get_s)

    def set(self, s):
        if len(self.items)==3:
            del self.items[0]
        self.items.append(s)

    def select(self):
        items = [item for item in self.items[:-1] if item.strip()]
        if items:
            return items[-1]
        else:
            return ""

    def __str__(self):
        return self.select()

    def __repr__(self):
        return self.select()


class dual_io:
    '''
    Wraps a standard interface and extend it by a report which is usually a text-log.
    '''
    def __init__(self, console, rep, std):
        self.console = console
        self.report  = rep
        self.std     = std

    def write(self,s):
        self.std.write(s)
        self.report.write(s)
        self.console.last_output.set(s)
        self.console.line_count+=s.count("\n")
        __main__.__ = str(self.console.last_output)

    def readline(self,*size):
        return self.std.readline(*size)

    def flush(self):
        return self.std.flush()

class RecordedUser(User):
    '''
    Logs all user input and writes it into a report.
    '''
    def __init__(self, report):
        self.report = report

    def get_input(self, prompt):
        text = raw_input(prompt)
        self.report.write(text+"\n")
        return text

class LSRecordedConsole(LSConsole):
    '''
    LSConsole extension used to record user input.
    '''

    def __init__(self, langlet, name, *args, **kwd):
        super(LSRecordedConsole, self).__init__(langlet, name, *args, **kwd)
        self.last_output   = LastOutput()
        self.line_count    = 0
        self.report = self.acquire_session_report(langlet,name,kwd.get("recording"))
        self.additional_header_info = " Creates session report " + path(self.report.name).basename()
        self.user = RecordedUser(self.report)

    def _set_dual_IO(self):
        '''
        Replaces sys.stdxxx files by dual_io counterparts.
        '''
        global sys
        sys.stdout = dual_io(self, self.report,sys.stdout)
        sys.stdin  = dual_io(self, self.report,sys.stdin)
        sys.stderr = dual_io(self, self.report,sys.stderr)

    def _clear_dual_IO(self):
        '''
        Unwraps dual_io.
        '''
        global sys
        try:
            sys.stdout = sys.stdout.std
            sys.stdin  = sys.stdin.std
            sys.stderr = sys.stderr.std
        except AttributeError:   # no report object
            pass

    def at_start(self):
        self._set_dual_IO()
        super(LSRecordedConsole, self).at_start()

    def at_exit(self):
        super(LSRecordedConsole, self).at_exit()
        self._clear_dual_IO()
        self.report.close()

    def acquire_session_report(self, langlet, console_name, recording_option):
        pth = langlet.path+os.sep+"reports"
        if recording_option == "enum":
            k = str(len(pth.files("*.ees"))+1)
            f = pth+os.sep+console_name+"_"+k+".ees"
            return file(f,"w")
        elif recording_option.startswith("+"):
            f = pth+os.sep+console_name+"_"+recording_option[1:]+".ees"
            return file(f,"w")
        elif recording_option.endswith("+"):
            f = pth+os.sep+recording_option[:-1]+"_"+console_name+".ees"
            return file(f,"w")
        elif recording_option == "stdname":
            f = pth+os.sep+console_name+".ees"
            return file(f,"w")
        elif recording_option.startswith(os.sep):
            f = pth+recording_option
            return file(f,"w")
        else:
            raise ValueError("Invalid recording option: '%s'"%recording_option)


class recorded_out_replay:
    '''
    Wraps a standard interface and extend it by a report which is usually a text-log.
    '''
    def __init__(self, std, console):
        self.console = console
        self.std     = std

    def write(self,s):
        self.std.write(s)
        self.console.last_output.set(s)
        self.console.line_count+=s.count("\n")
        __main__.__ = str(self.console.last_output)


    def readline(self,*size):
        return self.std.readline(*size)

    def flush(self):
        return self.std.flush()

class ReplayedUser(User):
    '''
    A ReplayedUser is used to switch between a user input mode and a mode
    where data is read from a session protocol.
    '''
    def __init__(self, session_protocol):
        self.session_protocol = session_protocol
        self.get_input = self.get_input_from_protocol

    def get_input_from_protocol(self, prompt):
        try:
            prefix, user_input = self.session_protocol.next()
            if prefix.startswith("?!"):
                self.get_input = self.get_raw_user_input
                return user_input
            elif prefix.startswith("?"):
                self.get_input = self.get_raw_user_input
                if user_input:
                    return self.get_raw_user_input(prefix[1:])
                else:
                    return self.get_raw_user_input(prefix[1:]+" ")
            else:
                return user_input
        except StopIteration:
            raise SystemExit

    def get_raw_user_input(self, prompt):
        text = raw_input(prompt)
        if text.strip() == "!":
            self.get_input = self.get_input_from_protocol
            return self.get_input_from_protocol(prompt)
        return text


class LSReplayConsole(LSConsole):

    def session(self, file):
        '''
        Line generator. Lines are read from file and file gets closed.
        This way the file can be used within a RecordedReplayedSession which derives
        from a ReplayedSession.
        '''
        lines = file.readlines()
        file.close()
        yield None
        for line in lines:
            yield line

    def __init__(self, langlet, name, *args, **kwd):
        super(LSReplayConsole, self).__init__(langlet, name, *args, **kwd)
        self.last_output = LastOutput()
        self.line_count  = 0
        self.ees_file = self.find_recorded_session(langlet,name,kwd.get("session"))
        self.recorded_session = self.session(self.ees_file)
        self.recorded_session.next() # closes report file
        self.additional_header_info = " Replay session " + path(self.ees_file.name).basename()
        self.user = ReplayedUser(self.session_protocol())

    def _prepare_prefix(self):
        prompt1 = sys.ps1.rstrip()
        prompt2 = sys.ps2.rstrip()
        return re.compile('(?:\\?\\!?)?(?:'+re.escape(prompt1)+"\\ ?|"+re.escape(prompt2)+'\\ ?)')

    def split_prefix(self, line):
        m = self.prefix_pattern.match(line)
        if m:
            prefix = m.group()
            print line,
            text = line[len(prefix):].rstrip()
            return prefix, text
        else:
            if line.startswith("#"):
                print line,
            return None, line

    def at_start(self):
        self._set_recorded_output()
        super(LSReplayConsole, self).at_start()
        self.prefix_pattern = self._prepare_prefix()


    def at_exit(self):
        super(LSReplayConsole, self).at_exit()
        self._clear_recorded_output()

    def _set_recorded_output(self):
        global sys
        __main__.__dict__["__"] = self.last_output
        sys.stdout   = recorded_out_replay(sys.stdout, self)
        sys.stdin    = recorded_out_replay(sys.stdin, self)
        sys.stderr   = recorded_out_replay(sys.stderr, self)

    def _clear_recorded_output(self):
        global sys
        try:
            sys.stdout = sys.stdout.std
            sys.stdin  = sys.stdin.std
            sys.stderr = sys.stderr.std
        except AttributeError:   # no report object
            pass

    def session_protocol(self):
        while True:
            line = self.recorded_session.next()
            prefix, user_input = self.split_prefix(line)
            if prefix:
                yield prefix, user_input
            else:
                continue

    def find_recorded_session(self, langlet, console_name, session):
        pth = langlet.path+os.sep+"reports"
        if os.sep in session:
            return file(session)
        else:
            if session.isdigit():
                f = pth+os.sep+console_name+"_"+session+".ees"
                if f.isfile():
                    return file(f)
            elif session == '_':
                f = pth+os.sep+console_name+".ees"
                if f.isfile():
                    return file(f)
            elif session.startswith("+"):
                f = pth+os.sep+console_name+"_"+session[1:]+".ees"
                if f.isfile():
                    return file(f)
            elif session.endswith("+"):
                f = pth+os.sep+session[:-1]+"_"+console_name+".ees"
                if f.isfile():
                    return file(f)
            else:
                f = pth+os.sep+session
                if f.isfile():
                    return file(f)
        raise ValueError("Invalid session: '%s'"% session)


def raises(exc, func, *args, **kwd):
    '''
    Turns a side effect into a boolean value.
    @param exc: exception class. function is expected to raise an exception of this class.
    @param func: function to raise an exception.
    @param args: optional arguments of func.
    @param kwd: optional keyword areguments of func.
    @returns: True if exception 'exc' is raised, False otherwise.
    '''
    try:
        func(*args, **kwd)
    except exc:
        return True
    else:
        return False

__main__.__dict__["raises"] = raises

class Assertion:
    def __init__(self):
        self.Line = 0
        self.Status = "OK"
        self.Text = ""
        try:
            self.last_exc = sys.last_value
        except AttributeError:
            self.last_exc = None


class LSReplayConsoleTest(LSReplayConsole):

    def __init__(self, langlet, name, *args, **kwd):
        super(LSReplayConsoleTest, self).__init__(langlet, name, *args, **kwd)
        self.assert_stmts = ["assert"]
        self.assertions   = []
        _assert = langlet.options.get("assert", "assert")
        self.assert_stmt = _assert

    def print_result(self):
        print
        print "--------------------."
        print "Recorded assertions |"
        print "--------------------------------------------------------------------------------------------------"
        print "Status |ees ln |repl ln| Assertion"
        print "-------+-------+-------+--------------------------------------------------------------------------"
        form_status = "%-7s|"
        form_line   = " %-6s|"
        form_assert = " %s"
        res = []
        for a in self.assertions:
            res.append(form_status % a.Status)
            res.append(form_line % a.SrcLine)
            res.append(form_line % a.DestLine)
            res.append(form_assert % a.Text)
            res.append("\n")
        text = "".join(res)
        print text[:-1]
        print "-------+-------+-------+--------------------------------------------------------------------------"

    def session_protocol(self):
        _assertion = None
        i = 0
        while True:
            line = self.recorded_session.next()
            i+=1
            prefix, user_input = self.split_prefix(line)
            if prefix:
                if prefix.startswith("?!") or not prefix.startswith("?"):
                    if user_input.lstrip().startswith(self.assert_stmt):
                        _assertion = Assertion()
                        _assertion.SrcLine = i
                        _assertion.DestLine = self.line_count
                        _assertion.Text = user_input
                        self.assertions.append(_assertion)

                yield prefix, user_input

                if _assertion:
                    try:
                        if sys.last_value == _assertion.last_exc:
                            _assertion.Status = "OK"
                        else:
                            _assertion.Status = "ERROR"
                    except AttributeError:
                        if _assertion.last_exc:
                            _assertion.Status = "ERROR"
                        else:
                            _assertion.Status = "OK"
                _assertion = None
            else:
                continue

    def at_exit(self):
        if self.assertions:
            self.print_result()
        super(LSReplayConsoleTest, self).at_exit()


class RecordedReplayedUser(ReplayedUser):

    def __init__(self, console):
        self.console = console
        ReplayedUser.__init__(self, console.session_protocol())

    def get_raw_user_input(self, prompt):
        text = raw_input(prompt)
        if text.strip() == "!":
            self.get_input = self.get_input_from_protocol
            self.console.check_prefix_split = True
            return self.get_input_from_protocol(prompt)
        self.console.user.report.write(text+"\n")
        return text

class recorded_out_rec_replay(recorded_out_replay):
    '''
    Wraps a standard interface and extend it
    by a report which is usually a text-log.
    '''

    def write(self,s):
        self.std.write(s)
        if not self.console.check_prefix_split:
            self.console.user.report.write(s)
        else:
            self.console.check_prefix_split = False
            m = self.console.prefix_pattern.match(s)
            if m:
                prefix = m.group()
                text = s[len(prefix):].strip()
                self.console.user.report.write(text+"\n")
        self.console.last_output.set(s)
        self.console.line_count+=s.count("\n")
        __main__.__dict__["__"] = str(self.console.last_output)


class LSRecordedReplayConsole(LSReplayConsoleTest):
    def __init__(self, langlet, name, *args, **kwd):
        super(LSRecordedReplayConsole, self).__init__(langlet, name, *args, **kwd)
        self.additional_header_info = " Reuses session report " + path(self.ees_file.name).basename()
        self.user = RecordedReplayedUser(self)
        self.user.report = file(self.ees_file.name,"w")
        self.check_prefix_split = False

    def _set_recorded_output(self):
        global sys
        __main__.__dict__["__"] = self.last_output
        sys.stdout   = recorded_out_rec_replay(sys.stdout, self)
        sys.stdin    = recorded_out_rec_replay(sys.stdin, self)
        sys.stderr   = recorded_out_rec_replay(sys.stderr, self)

    def at_exit(self):
        super(LSRecordedReplayConsole, self).at_exit()
        self._clear_recorded_output()
        self.user.report.close()


