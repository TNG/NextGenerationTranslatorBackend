

class TestTranslationSteps:
    """
    Tests the integration of translator service and translator with respect to the service
    calling the translator with the correct expected steps from source to target language.

    """

    def test_translation_direct(self, app_mock):
        """ Test the /translation endpoint for a direct translation en->de.
         Should prefer MockA model.
         """

        response_wrapper = app_mock.post("translation",
                                          json={
                                              "sourceLanguage": "de",
                                              "targetLanguage": "en",
                                              "texts": ["dummy_text"]})
        assert response_wrapper.status_code == 200

        assert response_wrapper.json == {'texts': ['dummy_text[mockA;de->en]']}

    def test_translation_steps(self, app_mock):
        """ Test the /translation endpoint for a step-wise translation de->fr->en.
        Should do both steps using the MockA model."""

        response_wrapper = app_mock.post("translation",
                                          json={
                                              "sourceLanguage": "en",
                                              "targetLanguage": "de",
                                              "texts": ["dummy_text"]})
        assert response_wrapper.status_code == 200

        assert response_wrapper.json == {'texts': ['dummy_text[mockA;en->fr][mockA;fr->de]']}

    def test_translation_steps_model_change(self, app_mock):
        """ Test the /translation endpoint for a step-wise translation en->de->es.
         Should do the first step using the MockA model, and the second step using MockB."""

        response_wrapper = app_mock.post("translation",
                                          json={
                                              "sourceLanguage": "de",
                                              "targetLanguage": "es",
                                              "texts": ["dummy_text"]})
        assert response_wrapper.status_code == 200

        assert response_wrapper.json == {'texts': ['dummy_text[mockA;de->en][mockB;en->es]']}
