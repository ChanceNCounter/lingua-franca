from importlib import import_module
from warnings import warn

_SUPPORTED_LANGUAGES = ["da", "de", "en", "es", "fr", "hu",
                        "it", "nl", "pt", "sv", "ru"]



def populate_localized_function_dict(lf_module):
    """Returns a dictionary of dictionaries, containing localized functions.

    Used by the top-level modules to locate, cache, and call localized functions.

    
    Arguments:
        lf_module (str) -- the name of the top-level module
    
    Returns:
        Dict -- {language_code : {function_name (str) : function}}
    
    Example:
        populate_localized_function_dict("format")["en"]["pronounce_number"](1)
        "one"
    """
    bad_lang_code = "Language code '{}' is registered with" \
                    " Lingua Franca, but its " + lf_module + " module" \
                    " could not be found."
    return_dict = {}
    for lang_code in _SUPPORTED_LANGUAGES:
        return_dict[lang_code] = {}
        try:
            mod = import_module(".lang." + lf_module + "_" + lang_code,
                                "lingua_franca")
        except ModuleNotFoundError:
            warn(Warning(bad_lang_code.format(lang_code)))
            continue
        function_names = getattr(import_module("." + lf_module, "lingua_franca"), "_REGISTERED_FUNCTIONS")
        for function_name in function_names:
            try:
                function = getattr(mod, function_name + "_" + lang_code)
            except AttributeError:
                function = None
                warn(Warning("Function '" + function_name + "' not implemented in "
                             "{}".format(lang_code)))
            return_dict[lang_code][function_name] = function
        del mod
    return return_dict