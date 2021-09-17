from xml.dom.minidom import parse as XMLOpen
from twisted.python.filepath import FilePath

def extractValue(xml, target):
    for c in xml.getElementsByTagName(target):
        c = c.firstChild
        if c:
            d = c.data
            return d.strip()
    return ""

def RipToken(inp: FilePath, outp: FilePath):
    libs = outp.child("Libs")
    js = outp.child("JS")
    if not libs.isdir():
        libs.createDirectory()
    if not js.isdir():
        js.createDirectory()
    with XMLOpen(inp.path) as xml:
        for token in xml.getElementsByTagName('net.rptools.maptool.model.Token'):
            name = extractValue(token, 'name')
            if name.startswith('Lib:'):
                name = name.split(':')[1]
                target = libs.child(name)
                if not target.isdir():
                    target.createDirectory()
                for macro in token.getElementsByTagName('net.rptools.maptool.model.MacroButtonProperties'):
                    group = extractValue(macro, 'group')
                    if group:
                        macroTarget = target.child(group)
                        if not macroTarget.exists():
                            macroTarget.createDirectory()
                    else:
                        macroTarget = target
                    mts = macroTarget.child(extractValue(macro, 'label')).siblingExtension('.mts')
                    command = extractValue(macro, "command")
                    header = dict(allowPlayerEdits='false',
                      fontColor="black",
                      group=group,
                      autoExecute="true",
                      includeLabel="false",
                      applyToTokens="true",
                      fontColorKey="black",
                      fontSize="1.00",
                      minWidth="",
                      maxWidth="",
                      toolTip="",
                      makeUDF="")
                    for e in header:
                        header[e] = extractValue(macro, e)
                    hc = []
                    for e,v in header.items():
                        hc.append(f"{e} = {v}")
                    mts.setContent((str.join("\n", hc) + "\n#####\n"+command).encode('utf-8'))

            

def RipTokens(inps: [FilePath, ...], outp: FilePath):
    for inp in inps:
        RipToken(inp, outp)
