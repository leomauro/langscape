'''
The Monitor module implements objects used to perform code-coverage and visualisation.
'''
import sys

class StmtSensor:
    def __init__(self, suite_begin, suite_end, **kwd):
        self.done        = False
        self.suite_begin = suite_begin
        self.suite_end   = suite_end
        Monitor().stmt_sensors.append(self)

class ExprSensor:
    def __init__(self, line_begin, idx):
        self.done        = False
        self.line_begin  = line_begin
        self.idx = idx
        Monitor().expr_sensors.append(self)


def measure_stmt(nbr):
    '''
    Basic sensor function. A call of this function will be compiled into
    Python stmt blocks.
    '''
    try:
        s = Monitor().stmt_sensors[nbr]
        s.done = True
    except IndexError:
        raise ValueError("no measure_stmt data available for %d"%nbr)

def measure_expr(expr, nbr):
    try:
        s = Monitor().expr_sensors[nbr]
        s.done = True
    except IndexError:
        raise ValueError("no measure_stmt data available for %d"%nbr)
    return expr


class Monitor:
    single = None
    def __init__(self):
        if Monitor.single:
            self.__dict__ = Monitor.single.__dict__
        else:
            self.stmt_sensors   = []
            self.expr_sensors   = []
            self.modules   = []
            Monitor.single = self

    def assign_sensors(self, module):
        if self.modules:
            last_mod = self.modules[-1]
            last_mod[1][1] = len(self.stmt_sensors)
            last_mod[2][1] = len(self.expr_sensors)
            self.modules.append((module,[len(self.stmt_sensors),0],[len(self.expr_sensors),0]))
        else:
            self.modules.append((module,[0,0],[0,0]))

    def check_on_covered_expr(self, mod):
        # print self.expr_sensors
        begin, end = mod[2]
        uncovered   = 0
        sensorlines = []
        created = len(self.expr_sensors[begin:end])
        k = 0
        for sensor in self.expr_sensors[begin:end]:
            if sensorlines:
                no, s = sensorlines[-1]
            else:
                no, s = 0, ''
            if sensor.line_begin == no:
                if sensor.done:
                    sensorlines[-1] = (no, s[:-1]+"+]")
                else:
                    sensorlines[-1] = (no, s[:-1]+"!]")
                    uncovered+=1
                k = max(k, len(s)-1)
            elif sensor.done:
                sensorlines.append((sensor.line_begin, "[+]"))
                # print "SENSOR-LINE-BEGIN", sensor.line_begin
            else:
                sensorlines.append((sensor.line_begin, "[!]"))
                uncovered+=1
                # print "SENSOR-LINE-BEGIN", sensor.line_begin
        return k, dict(sensorlines), created, uncovered

    def check_on_covered_stmts(self, mod):
        f = file(mod[0])
        lines = f.readlines()
        begin, end = mod[1]
        to_check    = []
        uncovered   = []
        sensorlines = []
        for sensor in self.stmt_sensors[begin:end]:
            # print "BEGIN", sensor.suite_begin, "   ", "END", sensor.suite_end
            sensorlines.append(sensor.suite_begin)
            if not sensor.done:
                to_check.append(sensor)
            else:
                for s in to_check:
                    if sensor.suite_begin<s.suite_end:   # included -> suite entered
                        if sensor.suite_end<s.suite_end: # end-sensor did not respond
                            k = s.suite_end  # the suite-end may not be the accurate place
                                             # it can include comments and empty lines
                            while 1:
                                l = lines[k-1]
                                l = l.strip()
                                # print "DEBUG line: ", k,l
                                if len(l)==0 or l.startswith('#'):
                                    k-=1
                                else:
                                    break
                            sensorlines.append(k)
                            uncovered.append(k)
                            s.done = True
                        else:
                            s.done = True
                    else:
                        uncovered.append(s.suite_begin)
                        s.done = True
            to_check = [s for s in to_check if not s.done]
        for s in to_check:
            uncovered.append(s.suite_begin)
        return lines, sensorlines, uncovered


    def show_report(self, show_sensor=True, out=sys.stdout):
        if len(self.stmt_sensors) == 0:
            raise RuntimeError("No stmt_sensors applied to module(s). Check the acceptance rules for coverage!")

        def write_stmt_status(created, not_responded, uncovered):
            out.write("\n"+(13+len_f)*"-"+".\n")
            out.write(("Statement Coverage:%%-%ds|\n"%(len_f-6))%" ")
            out.write(("%%-%ds|\n"%(len_f+13))%created)
            out.write(("%%-%ds|\n"%(len_f+13))%not_responded)
            out.write(("Covered: %%d%%%%%s|\n"%((len_f+1)*" ")%int(100*float(k - uncovered)/k)))
            out.write((13+len_f)*"-"+"'\n")

        def write_expr_status(k, created, not_responded, uncovered):
            out.write("\n"+(13+len_f)*"-"+".\n")
            out.write(("Expression Coverage:%%-%ds|\n"%(len_f-7))%" ")
            out.write(("%%-%ds|\n"%(len_f+13))%created)
            out.write(("%%-%ds|\n"%(len_f+13))%not_responded)
            out.write(("Covered: %%d%%%%%s|\n"%((len_f+1)*" ")%int(100*float(k - uncovered)/k)))
            out.write((13+len_f)*"-"+"'\n")

        def write_resume():
            n = len(self.stmt_sensors)
            pc = int(100*float(n - all_uncovered)/n)
            out.write("\n==========================================================================================\n")
            out.write("Summary:\n  %d sensors created\n  %d sensors did not respond\nStatement Coverage: %d%%\n\n"%(n,all_uncovered,pc))
            out.write("==========================================================================================\n")

        logo = []
        logo.append(r"     _____")
        logo.append(r"    /  __ \ ")
        logo.append(r"    | /  \/ _____   _____ _ __ __ _  __ _  ___")
        logo.append(r"    | |    / _ \ \ / / _ \ '__/ _` |/ _` |/ _ \ ")
        logo.append(r"    | \__/\ (_) \ V /  __/ | | (_| | (_| |  __/")
        logo.append(r"     \____/\___/ \_/ \___|_|  \__,_|\__, |\___|")
        logo.append(r"                                     __/ |")
        logo.append(r"                                    |___/")
        logo.append("")
        out.write("\n".join(logo))
        self.modules[-1][1][1] = len(self.stmt_sensors)
        self.modules[-1][2][1] = len(self.expr_sensors)
        all_uncovered = 0
        all_uncovered_expr = 0
        for mod in self.modules:
            spaces, exprlines, created_expr, uncovered_expr = self.check_on_covered_expr(mod)
            # print "EXPRLINES", exprlines
            if spaces:
                spaces+=2
            lines, sensorlines, uncovered = self.check_on_covered_stmts(mod)
            all_uncovered+=len(uncovered)
            out.write("\n")
            out.write("-"*(len(mod[0])+14)+".\n")
            out.write(" Coverage : %s  |\n"%mod[0])
            out.write("-"*(len(mod[0])+14)+"'\n")
            import math
            n = int(math.ceil(math.log(len(lines),10)))
            out.write("0"*n+"\n")
            if show_sensor:
                sensor_mark = ">"
            else:
                sensor_mark = ""
            for i,l in enumerate(lines):
                l = l.rstrip()
                if i+1 in sensorlines:
                    if i+1 in uncovered:
                        out.write("%%0%dd %%s  ! %%s  %%s\n"%n%(i+1, sensor_mark, spaces*" ",l))
                    else:
                        exprcover = exprlines.get(i+1, " "*spaces)
                        out.write("%%0%dd %%s    %%s  %%s\n"%n%(i+1, sensor_mark, exprcover, l))
                else:
                    exprcover = exprlines.get(i+1, " "*spaces)
                    out.write("%%0%dd      %%s  %%s\n"%n%(i+1, exprcover, l))
            begin, end = mod[1]
            k = len(sensorlines) #end - begin
            n = len(uncovered)
            def format(k, n):
                created       = "  %d sensors created"%k
                if n == 0:
                    not_responded =  "  all sensors responded"
                elif n == 1:
                    not_responded = "  1 sensor did not respond"
                else:
                    not_responded = "  %s sensors did not respond"%n
                return created, not_responded
            len_f = len(mod[0])
            # print "UNCOVERED", uncovered
            created, not_reponded = format(k, n)
            write_stmt_status(created, not_reponded, n)
            if created_expr:
                created, not_responded = format(created_expr, uncovered_expr)
                write_expr_status(created_expr, created, not_responded, uncovered_expr)


        if len(self.modules)>1:
            write_resume()





