from importlib import import_module

_SUPPORTED_LANGUAGES = ["da", "de", "en", "es", "fr", "hu",
                        "it", "nl", "pt", "sv"]

def passthrough(*args):
    raise NotImplementedError("Formatter not implemented"
                                " in specified language")

def populate_localized_function_dict(lf_module):
    return_dict = {}
    for lang_code in _SUPPORTED_LANGUAGES:
        return_dict[lang_code] = {}
        try:
            mod = import_module(".lang." + lf_module + "_" + lang_code,
                                "lingua_franca")
        except ModuleNotFoundError:
            print("WARNING: language code '" + lang_code + "' is registered"
                  " with Lingua Franca, but its " + lf_module + " module"
                  " could not be found.")
        function_names = getattr(import_module("." + lf_module, "lingua_franca"), "_REGISTERED_FUNCTIONS")
        for function_name in function_names:
            try:
                function = getattr(mod, function_name + "_" + lang_code)
            except AttributeError:
                function = passthrough
            return_dict[lang_code][function_name] = function
        del mod
    return return_dict