from twisted.web.template import flattenString
from twisted.web.template import Element, renderer, XMLFile, TagLoader, tags
from twisted.python.filepath import FilePath
import base64
import attr
from itertools import chain, count
from uuid import uuid4
from .utils import md5f, findImg
from .MTToken import MTToken
from .MTMacro import MTMacro, JSAutoLoader


def GenerateTokens(inps: [FilePath, ...], outp: FilePath):
    autoLoadJS = []
    idx = count()
            
    for inp in inps:
        libs = inp.child("Libs")
        if libs.exists():
            for lib in libs.children():
                midx = count()
                img = findImg(lib)
                token = MTToken(img=img,
                                name = 'Lib:' + lib.basename(),
                                idx = next(idx)
                                )
                for child in lib.children():
                    if child.splitext()[1]=='.mts':
                        token.macros.append(MTMacro(child, next(midx)))
                    elif child.isdir():
                        for c in child.children():
                            if c.splitext()[1] == '.mts':
                                token.macros.append(MTMacro(c, next(midx), group = child.basename()))

                print(token)
                token.serialize(outp.child(lib.basename()))
        js = inp.child("JS")
        if js.exists():
            for file in js.children():
                print(file.splitext())
                if file.splitext()[1] == '.js':
                    settings = dict(executeOnLoad="false")
                    jsFragment = MTToken(img = findImg(js),
                                         name = f"JS:{inp.basename()}:{file.basename()[:-3]}",
                                         idx = next(idx))
                    jsFragment.javascript = file.getContent().decode('utf-8')
                    if '/////' in jsFragment.javascript:
                        header, body = jsFragment.javascript.split("/////", 1)
                        for line in header.splitlines():
                            if line.strip() and line.strip()[0].isalpha() and '=' in line:
                                key, value = line.split('=')
                                settings[key.strip()] = value.strip()
                    print(settings)
                    if settings['executeOnLoad'].lower() == 'true':
                        autoLoadJS.append(jsFragment.name)
                    jsFragment.serialize(outp.child(lib.basename()))
    if autoLoadJS:
        autoLoadJS.sort()
        jsLoader = MTToken(img = findImg(inp),
                           name = "Lib:AutoLoadJS",
                           idx = next(idx))
        jsLoader.macros.append(JSAutoLoader(shim=True, idx=0, macro=FilePath("onCampaignLoad.mts")))
        jsLoader.macros.append(JSAutoLoader(shim=False, idx=1, macro=FilePath("deferredCalls.mts"), toProcess=autoLoadJS))
        jsLoader.serialize(outp.child("AutoLoadJS"))

