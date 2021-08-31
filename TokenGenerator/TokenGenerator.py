from twisted.web.template import flattenString
from twisted.web.template import Element, renderer, XMLFile, TagLoader, tags
from twisted.python.filepath import FilePath
import base64
import attr
import hashlib
from itertools import chain, count
from uuid import uuid4
import html
import twisted.web._flatten as _f

def efc(x):
    if isinstance(x, bytes):
        return x
    return x.encode('utf-8')

_f.escapeForContent = efc


def md5f(fp: FilePath):
    with fp.open('rb') as f:
        return hashlib.md5(f.read()).hexdigest()


@attr.attributes(auto_attribs=True)
class MTMeta(Element):
    loader = XMLFile(FilePath(__file__).sibling("asset_template.xml"))
    name: str
    id: str
    extension: str
    @renderer
    def asset(self, request, tag):
        print(request)
        tag.fillSlots(name=self.name, id=self.id, extension=self.extension)
        return tag

    

    
@attr.attributes(auto_attribs=True)
class MTToken(Element):
    img: FilePath
    name: str
    idx: int
    width: int = 90
    macros: list = attr.ib(factory=list)
    
    loader = XMLFile(FilePath(__file__).sibling("template.xml"))
    @renderer
    def tokenUID(self, request, tag):
        with open('/dev/urandom', 'rb') as f:
            return tag(base64.b64encode(b'1'+f.read(15)).decode('charmap'))

    @renderer
    def image(self, request, tag):
        return tag(md5f(self.img))

    @renderer
    def fillSlots(self, request, tag):
        tag.fillSlots(
            X=str(self.idx * self.width),
            Y='0',
            name=self.name,
            
        )
        return tag

    @renderer
    def macroList(self, request, tag):
        return [
            MTMacro(macro, idx, TagLoader(tag.clone())) for idx, macro in enumerate(self.macros)
        ]

    @renderer
    def notes(self, request, tag):
        return ""

    def serialize(self, op: FilePath):
        assets: FilePath = op.child("assets")
        assets.makedirs(True)
        imgd5 = md5f(self.img)
        img_metadata: FilePath = assets.child(imgd5)
        self.img.copyTo(img_metadata.siblingExtension(self.img.splitext()[1]))
        flattenString(None, MTMeta(self.name, imgd5, self.img.splitext()[1])).addCallback(img_metadata.setContent)
        FilePath(__file__).sibling("properties.xml").copyTo(op.child("properties.xml"))
        self.img.copyTo(op.child("thumbnail"))
        self.img.copyTo(op.child("thumbnail_large"))
        flattenString(None, self).addCallback(op.child('content.xml').setContent)

@attr.attributes(auto_attribs=True)
class MTMacro(Element):
    macro: FilePath
    idx: int
    loader: TagLoader

    @renderer
    def macroProperties(self, request, tag):
        tag.fillSlots(macroUUID=str(uuid4()),
                      autoExecute='false',
                      applyToTokens='false',
                      allowPlayerEdits='false',
                      macroLabel=self.macro.basename()[:-4]
                      )
        return tag

    @renderer
    def macroText(self, request, tag):
        
        return tag(html.escape(self.macro.getContent().decode('utf-8')).replace('&#x27;', "&apos;"))

    
    
    @renderer
    def macroInt(self, request, tag):
        return tag(str(self.idx+1))

def findImg(fp):
    for child in chain(fp.children(),
                       fp.parent().children(),
                       fp.parent().parent().children()):
        if child.basename().startswith('token.'):
            return child
    return None
    
        

def GenerateTokens(inp, outp):
    libs = inp.child("Libs")
    idx = count()
    if libs.exists():
        for lib in libs.children():
            img = findImg(lib)
            token = MTToken(img=img,
                            name = 'Lib:' + lib.basename(),
                            idx = next(idx)
                            )
            for child in lib.children():
                if child.splitext()[1]=='.mts':
                    token.macros.append(child)
            print(token)
            token.serialize(outp.child(lib.basename()))
