SHIM = """
[h: link = macroLinkText("deferredCalls@"+getMacroLocation())]
[h: execLink(link,1)]
"""

FETCHER = """
[r: js.eval("return getJS(JSON.parse(args[0])[0])", macro.args)]
"""

LOADER = """
[h: defineFunction("js.load", "loadjs@"+getMacroLocation())]
[h: js.eval("
	this.jsTokenMap = {};
	this.getJS = function(name) {return jsTokenMap['JS:'+name].getNotes()};
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
			eval(token.getNotes());
		}
		catch (e) {
			MapTool.chat.broadcast('AutoLoad javascript failed (see console for details): '+e)	
			console.log(e.stack)
		}
	}
")]

"""
