from request_limitation import RequestLimitExceededException


class TestTranslationErrors:
    """
     Test correct error responses (included codes) are returned in case of errors.
    """

    def test_invalid_language_error(self, app_mock):
        response_wrapper = app_mock.post("translation",
                                         json={
                                             "sourceLanguage": "xy",
                                             "targetLanguage": "de",
                                             "texts": ["dummy_text"]})
        assert response_wrapper.status_code == 400
        assert response_wrapper.json == {"error": "Language 'xy' is not supported."}

    def test_invalid_language_error_II(self, app_mock):
        """ Languages exist, but not that pair."""
        response_wrapper = app_mock.post("translation",
                                         json={
                                             "sourceLanguage": "de",
                                             "targetLanguage": "hu",
                                             "texts": ["dummy_text"]})
        assert response_wrapper.status_code == 400
        assert response_wrapper.json == {"error": "Translation 'de' to 'hu' not supported."}

    def test_request_limit_exceeded_error(self, integration_test_environment, app_mock):
        integration_test_environment.request_limiter.return_value.limited_requests.return_value.__enter__.side_effect = RequestLimitExceededException
        response_wrapper = app_mock.post("translation",
                                         json={
                                             "sourceLanguage": "de",
                                             "targetLanguage": "en",
                                             "texts": ["dummy_text"]})
        assert response_wrapper.status_code == 503
        assert response_wrapper.headers.get("Retry-After") == "5"
        assert response_wrapper.json == {"error": "Request limit exceeded"}

    def test_models_not_loaded_exception(self, integration_test_environment, app_mock):
        integration_test_environment.translator._models_loaded = False
        response_wrapper = app_mock.post("translation",
                                         json={
                                             "sourceLanguage": "de",
                                             "targetLanguage": "en",
                                             "texts": ["dummy_text"]})
        assert response_wrapper.status_code == 503
        assert response_wrapper.headers.get("Retry-After") == "5"
        assert response_wrapper.json == {"error": "Models have not been loaded yet."}
