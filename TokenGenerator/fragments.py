SHIM = """
[h: link = macroLinkText("deferredCalls@"+getMacroLocation())]
[h: execLink(link,1)]
"""

FETCHER = """
[r: js.eval("return getJS(JSON.parse(args[0])[0])", macro.args)]
"""

LOADER = r"""
[h: defineFunction("js.load", "loadjs@"+getMacroLocation())]
[h: js.eval("
	this.jsTokenMap = {};
	this.getJS = function(name) {
            let notes = jsTokenMap['JS:'+name].getNotes();
            if (notes.indexOf('/////') > -1) {
                header = notes.split('/////')[0];
                for (let line of header.split('\\n')) {
                    if (line.indexOf('=') > -1) {
                        let key, val
                        [key, val] = line.split('=');
                        if (key.trim() == 'dependencies') {
                            for (let dep of val.trim().split(' ')) {
                                if (dep.indexOf(':') < 0) {
                                    dep = name.split(':')[0] + ':' + dep
                                }
                                console.log('Chain loading ' + dep)
                                notes = getJS(dep) + '\\n\\n' + notes;
                            }
                        }
                    }
                }
            }
            return notes;
        };
	let autoLoadTokens = ['$autoLoadTokens'];
	let tokens = MapTool.tokens.getMapTokens();
	let to_process = {};
	let cnt = 0;
	for (let token of tokens) {
		if (autoLoadTokens.indexOf(token.getName()) > -1) {
			if (MTScript.evalMacro(`[r: getOwners(',', '`+token.getId()+`')]`)) {
				console.log(`Not executing JS in ` + token.getName() + ` because it is owned`);
				continue;
			}
			to_process[token.getName()] = token;
			cnt++;
		}
		if (token.getName().startsWith('JS:')) {
			jsTokenMap[token.getName()] = token;		
		}
	}
	console.log('Executing '+cnt+' javascript macros')
	for (let tokenName of autoLoadTokens) {
		let token = to_process[tokenName];
		try {
			console.log('Loading ' + token.getName());
			eval(token.getNotes());
		}
		catch (e) {
			MapTool.chat.broadcast('AutoLoad javascript failed (see console for details): '+e)	
			console.log(e.stack)
		}
	}
")]

"""
