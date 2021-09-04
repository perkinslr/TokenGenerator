from twisted.web.template import flattenString
from twisted.web.template import Element, renderer, XMLFile, TagLoader, tags
from twisted.python.filepath import FilePath
from collections import defaultdict
import base64
import attr
import html
from itertools import chain, count
from uuid import uuid4
from .utils import md5f
from . import fragments


@attr.attributes(auto_attribs=True)
class MTMacro(Element):
    macro: FilePath
    idx: int
    loader: TagLoader = None
    group: str = ""
    lib: FilePath = None
    UDFList = {}

    @property
    def header(self):
        content = self.macro.getContent().decode('utf-8')
        if '\n#####' in content:
            return content.split('\n#####',1)[0]
        return ""

    @property
    def body(self):
        content = self.macro.getContent().decode('utf-8')
        if '\n#####' in content:
            return content.split('\n#####',1)[1].lstrip()
        return content

    @renderer
    def macroProperties(self, request, tag):
        header = self.header.split('\n')
        params = dict(allowPlayerEdits='false',
                      fontColor="black",
                      group=self.group,
                      autoExecute="true",
                      includeLabel="false",
                      applyToTokens="true",
                      fontColorKey="black",
                      fontSize="1.00",
                      minWidth="",
                      maxWidth="",
                      toolTip="",
                      makeUDF=""

                      )
                      
        for line in header:
            if line.strip().startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=')
                params[key.strip()] = value.strip()

        tag.fillSlots(macroUUID=str(uuid4()),
                      macroLabel=self.macro.basename()[:-4],
                      **params
                      )
        if params['makeUDF']:
            self.UDFList[self.macro.basename()[:-4]+'@'+'Lib:'+self.lib.basename()] = params['makeUDF']
        return tag

    @renderer
    def macroText(self, request, tag):
        return tag(html.escape(self.body).replace('&#x27;', "&apos;"))
    
    @renderer
    def macroInt(self, request, tag):
        return tag(str(self.idx+1))

@attr.attributes(auto_attribs=True)
class AutoLoader(MTMacro):
    target: str = "SHIM"
    toProcess: list = ()
    @property
    def header(self):
        return ""
    @property
    def body(self):
        if self.target == 'UDFLOADER':
            udfs = []
            for target, UDF in self.UDFList.items():
                funcname, ignoreOutput, newScope = UDF.split(':')
                udfs.append(fragments.UDFLOADER.replace(
                    '$FUNCNAME', funcname.strip()
                ).replace(
                    '$TARGET', target.strip()
                ).replace(
                    '$DISCARD', ignoreOutput.strip()
                ).replace(
                    '$NEWSCOPE', newScope.strip()
                ))
            return str.join("\n", udfs)
        return getattr(fragments, self.target).replace('$autoLoadTokens', str.join("', '",self.toProcess))

    
