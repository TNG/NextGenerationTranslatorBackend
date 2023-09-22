import pytest


class TestTranslationHelperMethods:
    """ Integration tests for the helper endpoints such as listing languages."""

    def test_translation_languages(self, app_mock):
        response_wrapper = app_mock.get("languages")
        assert response_wrapper.status_code == 200
        assert list(sorted(response_wrapper.json['languages'])) == ['de', 'en', 'es', 'fr']

    def test_translation_health(self, app_mock):
        response_wrapper = app_mock.get("health")
        assert response_wrapper.status_code == 200
        assert response_wrapper.json == {'healthy': True, 'serviceAvailable': True}

    @pytest.mark.parametrize("base_language, expected_languages",
                 [["en", ['de', 'en', 'es', 'fr']],
                  ["hu", ["hu"]]
                  ])
    def test_translation_languages_post(self, base_language, expected_languages, app_mock):
        response_wrapper = app_mock.post("languages", json={"baseLanguage": base_language})
        assert response_wrapper.status_code == 200
        assert list(sorted(response_wrapper.json['languages'])) == expected_languages

    def test_get_models(self, app_mock):
        response_wrapper = app_mock.get("models")
        assert response_wrapper.status_code == 200
        assert list(sorted(response_wrapper.json['models'])) == ["mockA", "mockB"]