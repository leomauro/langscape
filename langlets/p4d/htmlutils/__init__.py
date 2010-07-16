import webbrowser
from langscape.util.path import path

def exec_html(html, p4dfile):
    from htmlprinter import htmlprinter
    import os
    html_str = html.xmlstr(xml_declaration = False, xmlprinter = htmlprinter)
    print html_str
    #f = p4dfile.replace(".p4d", ".html")
    #open(f, "w").write(html_str)
    #webbrowser.open_new_tab("file:///"+f.replace(os.sep, "/"))



