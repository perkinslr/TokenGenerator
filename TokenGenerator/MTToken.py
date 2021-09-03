from twisted.web.template import flattenString
from twisted.web.template import Element, renderer, XMLFile, TagLoader, tags
from twisted.python.filepath import FilePath
import base64
import attr
import html
from itertools import chain, count
from uuid import uuid4
from .utils import md5f
from .MTMacro import MTMacro


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
    javascript: str = ""
    
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
        for m in self.macros:
            m.loader = TagLoader(tag.clone())
        print(self.macros)
        return self.macros
    

    @renderer
    def notes(self, request, tag):
        return tag("\n"+html.escape(self.javascript).replace('&#x27;', "&apos;"))
        

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


