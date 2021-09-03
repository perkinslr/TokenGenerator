from twisted.web.template import flattenString
from twisted.web.template import Element, renderer, XMLFile, TagLoader, tags
from twisted.python.filepath import FilePath
import base64
import attr
from itertools import chain, count
from uuid import uuid4
from .utils import md5f, findImg
from .MTToken import MTToken
from .MTMacro import MTMacro


def GenerateTokens(inps: [FilePath, ...], outp: FilePath):
    for inp in inps:
        libs = inp.child("Libs")
        idx = count()
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
            autoLoadJS = []
            for file in js.children():
                print(file.splitext())
                if file.splitext()[1] == '.js':
                    jsFragment = MTToken(img = findImg(js),
                                         name = f"JS:{inp.basename()}:{file.basename()[:-3]}",
                                         idx = next(idx))
                    jsFragment.javascript = file.getContent().decode('utf-8')
                    if '/////' in jsFragment.javascript:
                        header, body = jsFragment.javascript.split("/////", 1)
                    
                
