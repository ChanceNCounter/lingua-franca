# Project Structure and Notes

## Source code layout

- package `lingua_franca`
  - `internal.py`: common functions and data used by the top-level modules
  - top-level modules (`lingua_franca.format`, `lingua_franca.parse`, etc.)
      - top-level function definitions (`lingua_franca.format.pronounce_number()`, etc.)
      - list of the member functions which have been localized ([func_name (str)])
          ex: `lingua_franca.format.pronounce_number()` 
              is registered in this list as `"pronounce_number"`, as it has been localized.
              This list enables discovery of localized functions.
  - /lang/
      - localized implementations of top-level functions
          - files named uniformly, based on module and language code. ex:
              `lingua_franca.format` will look for localized functions in
              `lingua_franca.lang.format_<lang_code>`, such as
              `lingua_franca.lang.format_en` and `lingua_franca.lang.format_es`.
      - localized `common_data_<lang_code>`
          - functions and data related to parsing and formatting for a particular language
              - names of months, days
              - default date and time format
              - names of certain numbers
              - etc.
  - /res/: fully localized data (en_US and en_GB, etc.)
      - detailed formatting instructions for dates and times
      - localized vocabulary
  - /test/: pyunit tests, files named for their members
          (`test_format.py`, `test_format_en.py`, `test_format_es.py`, etc.)

----

## On adding new languages

Ensure that all supported languages are registered in `lingua_franca.internal.py`, in the list
`_SUPPORTED_LANGUAGES`.

## On writing new functions which will need localization

Ensure that all functions which will have localized versions are registered in their module's
`_REGISTERED_FUNCTIONS` tuple, conventionally defined near the top.

For example, formatters which have been or will be localized are registered in
  `lingua_franca.format._REGISTERED_FUNCTIONS`, by name only.

As of July, 2020, this tuple looks as follows:

  ```python3
  # lingua_franca/format.py

  _REGISTERED_FUNCTIONS = ("nice_number",
                         "nice_time",
                         "pronounce_number",
                         "nice_response")
  ```

## On localizing functions

If you are localizing an existing top-level function, there is no need to alter the top-level
module to which your function belongs. As mentioned above, Lingua Franca will discover all
localized versions of its top-level functions.

Localized functions live in `lingua_franca/lang/`, in files named for their corresponding module.

>For example, the top level formatting module is `lingua_franca.format`, and lives at
`lingua_franca/format.py`.

>English formatters live in `lingua_franca/lang/format_en.py`.  
>Spanish formatters live in `lingua_franca/lang/format_es.py`.  
>Spanish *parsers*, corresponding to
`lingua_franca.parse` and `lingua_franca/parse.py`,  
>live in `lingua_franca/lang/parse_es.py`.

Note that these use a *primary* language code, such as `en` or `es`, rather than a *full* language
code, such as `en-US` or `es-ES`. Details relating to regional dialects reside in `res`.

Lingua Franca will find your function by itself, as long as

- Your files are named properly
- Your function and its signature are named and organized properly (described below) and
- Your primary language code is registered as a supported language with Lingua Franca itself, in
`lingua_franca.internal._SUPPORTED_LANGUAGES`

What you must do:

- Implement the function with its uniform name, using the appropriate language code.
  - `lingua_franca.lang.format_en.pronounce_number_en`
  - `lingua_franca.lang.format_es.pronounce_number_es`
  - `lingua_franca.lang.format_pt.pronounce_number_pt`
- Name function arguments exactly as they are named in the top-level modules
  - You do not need to implement all arguments, but you must name them identically
  - All arguments must be keyword arguments (except the primary argument)
  - If you need to add new arguments,
        feel free, but MAKE SURE you add the argument to the top-level function, as a keyword arg.
        This is the only time you should need to modify the top-level functions while localizing.
        Ensure that any new arguments are at the end of the function signatures, both in the
        top-level function, and in your localized function.
