import os.path
from importlib import import_module
from inspect import signature
from warnings import warn

_SUPPORTED_LANGUAGES = ["cs", "da", "de", "en", "es", "fr", "hu",
                        "it", "nl", "pt", "sv"]

__default_lang = "en-us"  # English is the default active language
__loaded_langs = [i for i in _SUPPORTED_LANGUAGES]

_localized_functions = {}


def set_active_langs(langs, override_default=True):
    """ Set the list of languages to load.
        Unloads previously-loaded languages which are not specified here.
        If the input list does not contain the current default language,
        langs[0] will become the new default language. This behavior
        can be overridden.

    Arguments:
        langs: {list(str) or str} -- a list of language codes to load

    Keyword Arguments:
        override_default {bool} -- Change default language to first entry if
                                    the current default is no longer present
                                    (default: True)
    """
    if isinstance(langs, str):
        langs = [langs]
    if not isinstance(langs, list):
        raise(TypeError("lingua_franca.common.set_active_langs expects"
                        " 'str' or 'list'"))
    langs = [get_primary_lang_code(lang) for lang in langs]
    global __loaded_langs
    __loaded_langs = list(dict.fromkeys(langs))
    if override_default or get_primary_lang_code(__default_lang) \
            not in __loaded_langs:
        set_default_lang(get_full_lang_code(__loaded_langs[0]))
    _refresh_function_dict()


def _refresh_function_dict():
    for mod in _localized_functions.keys():
        populate_localized_function_dict(mod, langs=__loaded_langs)


def get_active_langs():
    """ Get the list of currently-loaded language codes

    Returns:
        list(str)
    """
    return __loaded_langs


def load_language(lang):
    if lang not in __loaded_langs:
        __loaded_langs.append(lang)


def get_default_lang():
    """ Get the active full language code (BCP-47)

    Returns:
        str: A BCP-47 language code, e.g. ("en-us", or "pt-pt")
    """
    return __default_lang


def set_default_lang(lang_code):
    """ Set the active BCP-47 language code to be used in formatting/parsing

    Args:
        lang (str): BCP-47 language code, e.g. "en-us" or "es-mx"
    """
    global __default_lang
    if __default_lang != lang_code:
        # TODO: Validate lang codes?
        __default_lang = lang_code
    if __default_lang not in __loaded_langs:
        __loaded_langs.insert(0, __default_lang)
        _refresh_function_dict()


def get_primary_lang_code(lang=None):
    """ Get the primary language code

    Args:
        lang (str, optional): A BCP-47 language code, or None for default

    Returns:
        str: A primary language family, such as "en", "de" or "pt"
    """
    # split on the hyphen and only return the primary-language code
    # NOTE: This is typically a two character code.  The standard allows
    #       1, 2, 3 and 4 character codes.  In the future we can consider
    #       mapping from the 3 to 2 character codes, for example.  But for
    #       now we can just be careful in use.
    return get_full_lang_code(lang).split("-")[0]


def get_full_lang_code(lang=None):
    """ Get the full language code

    Args:
        lang (str, optional): A BCP-47 language code, or None for default

    Returns:
        str: A full language code, such as "en-us" or "de-de"
    """
    if not lang:
        lang = __default_lang

    return lang or "en-us"


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


def localized_function_caller(mod, func_name, lang, args):
    """Calls a localized function from a dictionary populated by
        `populate_localized_function_dict()`

    Arguments:
        mod (str): the module calling this function
        func_name (str): the name of the function to find and call
                (e.g. "pronounce_number")
        lang (str): a language code
        arguments (dict): the arguments to pass to the localized function

    Returns:
        Result of localized function

    Note: Not intended for direct use. Called by top-level modules.

    """
    if not lang:
        lang = get_default_lang()
    lang_code = get_primary_lang_code(lang)
    if lang_code not in _SUPPORTED_LANGUAGES:
        raise_unsupported_language(lang_code)

    elif mod not in _localized_functions.keys():
        raise ModuleNotFoundError("Module lingua_franca." + mod +
                                  " not recognized")

    elif lang_code not in _localized_functions[mod].keys():
        raise ModuleNotFoundError(mod + " module of language '" +
                                  lang_code + "' is not currently loaded.")

    # _localized_functions is a dict of dicts:
    #   functions, by module and then by language code
    #   _localized_functions{[module]: {[language]: [functions]}}
    func_signature = _localized_functions[mod][lang_code][func_name]
    if not func_signature:
        raise KeyError("Something is very wrong with Lingua Franca."
                       " Have you altered the library? If not, please"
                       " contact the developers through GitHub.")
    elif isinstance(func_signature, type(NotImplementedError())):
        raise func_signature
    else:
        _module = import_module(".lang." + mod + "_" + lang_code,
                                "lingua_franca")
        func = getattr(_module, func_name + "_" + lang_code)
        r_val = func(**{arg: val for arg, val in args if arg in
                        func_signature.parameters})
        del func
        del _module
        return r_val


def populate_localized_function_dict(lf_module, langs=get_active_langs()):
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
    for lang_code in langs:
        return_dict[lang_code] = {}
        _FUNCTION_NOT_FOUND = ""
        try:
            lang_common_data = import_module(".lang.common_data_" + lang_code,
                                             "lingua_franca")
            _FUNCTION_NOT_FOUND = getattr(lang_common_data,
                                          "_FUNCTION_NOT_IMPLEMENTED_WARNING")
            del lang_common_data
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
                function = getattr(mod, function_name
                                   + "_" + lang_code)
                function_signature = signature(function)
                del function
            except AttributeError:
                function_signature = _FUNCTION_NOT_FOUND
                # TODO log these occurrences: "function 'function_name' not
                # implemented in language 'lang_code'"
                #
                # Perhaps provide this info to autodocs, to help volunteers
                # identify the functions in need of localization
            return_dict[lang_code][function_name] = function_signature

        del mod
    _localized_functions[lf_module] = return_dict
    return _localized_functions[lf_module]


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
