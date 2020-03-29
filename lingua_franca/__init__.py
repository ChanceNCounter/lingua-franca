import os.path
from importlib import import_module
from inspect import signature

from lingua_franca.lang import get_primary_lang_code

_SUPPORTED_LANGUAGES = ["da", "de", "en", "es", "fr", "hu",
                        "it", "nl", "pt", "sv"]
class UnsupportedLanguageError(NotImplementedError):
    pass

class FunctionNotLocalizedError(NotImplementedError):
    pass

def raise_unsupported_language(language):
    """
    Raise an error when a language is unsupported

    Arguments:
        language: str
            The language that was supplied.
    """
    supported = ' '.join(_SUPPORTED_LANGUAGES)
    raise UnsupportedLanguageError("\nLanguage '{language}' is not yet "
                "supported by Lingua Franca. Supported language codes "
                "include the following:\n{supported}"
                .format(language=language, supported=supported))

def _localized_function_caller(funcs, func_name, lang, arguments):
    """Calls a localized function from a dictionary populated by
        `populate_localized_function_dict()`

    Arguments:
        funcs (dict): the function dictionary (e.g. 
                `lingua_franca.format._LOCALIZED_FUNCTIONS)
        func_name (str): the name of the function to find and call
                (e.g. "pronounce_number")
        lang (str): a language code
        arguments (dict): the arguments to pass to the localized function

    Returns:
        Result of localized function

    Note: Not intended for direct use. Called by top-level modules.

    """
    lang_code = get_primary_lang_code(lang)
    if lang_code not in _SUPPORTED_LANGUAGES:
        raise_unsupported_language(lang_code)
    func = funcs[lang_code][func_name]
    if not func:
        raise KeyError("Something is very wrong with Lingua Franca."
                        " Have you altered the library? If not, please"
                        " contact the developers through GitHub.")
    elif isinstance(func, type(NotImplementedError())):
        raise func
    else:   
        return func(**{arg: val for arg, val in arguments if arg in
                    signature(func).parameters})

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
        _FUNCTION_NOT_FOUND = ""
        try:
            lang_common_data = import_module(".lang.common_data_" + lang_code,
                                        "lingua_franca")
            _FUNCTION_NOT_FOUND = getattr(lang_common_data,
                                     "_FUNCTION_NOT_IMPLEMENTED_WARNING")
        except Exception:
            _FUNCTION_NOT_FOUND = "This function has not been implemented" \
                                  " in the specified language."
        _FUNCTION_NOT_FOUND = FunctionNotLocalizedError(_FUNCTION_NOT_FOUND)

        try:
            mod = import_module(".lang." + lf_module + "_" + lang_code,
                                "lingua_franca")
        except ModuleNotFoundError:
            warn(Warning(bad_lang_code.format(lang_code)))
            continue

        function_names = getattr(import_module("." + lf_module, "lingua_franca"),
                                "_REGISTERED_FUNCTIONS")
        for function_name in function_names:
            try:
                function = getattr(mod, function_name + "_" + lang_code)
            except AttributeError:
                function = _FUNCTION_NOT_FOUND
                # TODO log these occurrences: "function 'function_name' not
                # implemented in language 'lang_code'"
                #
                # Perhaps provide this info to autodocs, to help volunteers
                # identify the functions in need of localization
            return_dict[lang_code][function_name] = function

        del mod
    return return_dict

def resolve_resource_file(res_name, data_dir=None):
    """Convert a resource into an absolute filename.

    Resource names are in the form: 'filename.ext'
    or 'path/filename.ext'

    The system wil look for ~/.mycroft/res_name first, and
    if not found will look at /opt/mycroft/res_name,
    then finally it will look for res_name in the 'mycroft/res'
    folder of the source code package.

    Example:
    With mycroft running as the user 'bob', if you called
        resolve_resource_file('snd/beep.wav')
    it would return either '/home/bob/.mycroft/snd/beep.wav' or
    '/opt/mycroft/snd/beep.wav' or '.../mycroft/res/snd/beep.wav',
    where the '...' is replaced by the path where the package has
    been installed.

    Args:
        res_name (str): a resource path/name
    Returns:
        str: path to resource or None if no resource found
    """
    # First look for fully qualified file (e.g. a user setting)
    if os.path.isfile(res_name):
        return res_name

    # Now look for ~/.mycroft/res_name (in user folder)
    filename = os.path.expanduser("~/.mycroft/" + res_name)
    if os.path.isfile(filename):
        return filename

    # Next look for /opt/mycroft/res/res_name
    data_dir = data_dir or os.path.expanduser("/opt/mycroft/res/")
    filename = os.path.expanduser(os.path.join(data_dir, res_name))
    if os.path.isfile(filename):
        return filename

    # Finally look for it in the source package
    filename = os.path.join(os.path.dirname(__file__), 'res', res_name)
    filename = os.path.abspath(os.path.normpath(filename))
    if os.path.isfile(filename):
        return filename

    return None  # Resource cannot be resolved
