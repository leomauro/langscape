def build_cstbuilder(cstbuilder):
    alt              = cstbuilder.builder(981003, 'alt', "alt: item+")
    atom             = cstbuilder.builder(981005, 'atom', "atom: '(' rhs ')' | NAME | STRING")
    file_input       = cstbuilder.builder(981000, 'file_input', "file_input: rule* ENDMARKER")
    item             = cstbuilder.builder(981004, 'item', "item: '[' rhs ']' | atom ['*' | '+']")
    rhs              = cstbuilder.builder(981002, 'rhs', "rhs: alt ('|' alt)*")
    rule             = cstbuilder.builder(981001, 'rule', "rule: NAME ':' rhs ';'")
    return locals()

