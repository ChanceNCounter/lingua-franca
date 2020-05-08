# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from warnings import warn
from lingua_franca.common import get_default_lang, \
    set_default_lang, get_full_lang_code as gflc, \
    get_primary_lang_code as gplc

# __active_lang = "en-us"  # English is the default active language
# TODO: Should this really be stored in the user config file?


def get_active_lang():
    """ Get the active full language code (BCP-47)

    Returns:
        str: A BCP-47 language code, e.g. ("en-us", or "pt-pt")
    """
    _getlang = "Direct imports from lingua_franca.lang"
    " have been deprecated. Use"
    " lingua_franca.common.get_active_lang()"
    warn(_getlang, DeprecationWarning)
    return get_default_lang()


def set_active_lang(lang_code):
    """ Set the active BCP-47 language code to be used in formatting/parsing

    Args:
        lang (str): BCP-47 language code, e.g. "en-us" or "es-mx"
    """
    _setlang = "Direct imports from lingua_franca.lang"
    " have been deprecated. Use"
    " lingua_franca.common.get_active_lang()"
    warn(_setlang, DeprecationWarning)
    set_default_lang(lang_code=lang_code)


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
    warn("Direct imports from lingua_franca.lang have been deprecated. Use"
         " lingua_franca.common.get_primary_lang_code()", DeprecationWarning)
    return gplc(lang=lang)


def get_full_lang_code(lang=None):
    """ Get the full language code

    Args:
        lang (str, optional): A BCP-47 language code, or None for default

    Returns:
        str: A full language code, such as "en-us" or "de-de"
    """
    warn("Direct imports from lingua_franca.lang have been deprecated. Use"
         " lingua_franca.common.get_full_lang_code()", DeprecationWarning)
    return gflc(lang=lang)
    # if not lang:
    #     lang = __active_lang

    # return lang or "en-us"
