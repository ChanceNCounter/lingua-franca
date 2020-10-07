import unittest
import lingua_franca
import lingua_franca.parse


def unload_all_languages():
    lingua_franca.unload_languages(lingua_franca.get_active_langs())


def setUpModule():
    unload_all_languages()


def tearDownModule():
    unload_all_languages()


class TestException(unittest.TestCase):
    def setUpClass():
        unload_all_languages()

    def tearDownClass():
        unload_all_languages()

    def test_must_load_language(self):
        self.assertRaises(ModuleNotFoundError,
                          lingua_franca.parse.extract_number, 'one')


class TestLanguageLoading(unittest.TestCase):
    def test_load_language(self):
        unload_all_languages()
        lingua_franca.load_language('en')

        # Verify that English is loaded and, since it's the only language
        # we've loaded, also the default.
        self.assertEqual(lingua_franca.get_default_lang(), 'en')
        # Verify that English's default full code is 'en-us'
        self.assertEqual(lingua_franca.get_full_lang_code('en'), 'en-us')
        # Verify that this is also our current full code
        self.assertEqual(lingua_franca.get_default_loc(), 'en-us')
        self.assertFalse('es' in lingua_franca.get_active_langs())

        # Verify that unloaded languages can't be invoked explicitly
        self.assertRaises(ModuleNotFoundError,
                          lingua_franca.parse.extract_number,
                          'uno', lang='es')
        unload_all_languages()

    def test_default_language(self):
        unload_all_languages()
        lingua_franca.load_language('en')

        # Load two languages, ensure first is default
        lingua_franca.load_languages(['en', 'es'])
        self.assertEqual(lingua_franca.get_default_lang(), 'en')
        self.assertEqual(lingua_franca.parse.extract_number('one'), 1)

        unload_all_languages()

    def test_default_language_singles(self):
        unload_all_languages()

        # Load languages one at a time, ensure first is default
        self.assertEqual(lingua_franca.get_active_langs(), [])
        lingua_franca.load_language('en')
        self.assertEqual(lingua_franca.get_default_lang(), 'en')
        lingua_franca.load_language('es')
        self.assertEqual(lingua_franca.get_default_lang(), 'en')

        self.assertEqual(lingua_franca.parse.extract_number('dos'), False)
        self.assertEqual(lingua_franca.parse.extract_number('dos',
                                                            lang='es'),
                         2)

        # Verify default language failover
        lingua_franca.unload_language('en')
        self.assertEqual(lingua_franca.get_default_lang(), 'es')
        unload_all_languages()
