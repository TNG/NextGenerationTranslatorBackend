from unittest.mock import Mock

from translator_models.translator_model import TranslatorModel
from utils.translation_graph import TranslationGraph


class TestTranslationGraph:

    def test_get_strongly_connected_component(self):
        model = Mock(spec=TranslatorModel)

        model.available_language_pairs = [
            ("a", "b"),
            ("a", "c"),
            ("a", "d"),
            ("b", "a"),
            ("b", "e"),
            ("c", "b"),
            ("c", "e"),
            ("e", "f")
        ]
        model.translation_quality_grade = 1
        graph = TranslationGraph([model])

        assert graph.get_strongly_connected_component("a") == {"a", "b", "c"}

    def test_find_optimal_translation_path(self):
        model = Mock(spec=TranslatorModel)

        model.available_language_pairs = [
            ("a", "b"),
            ("a", "c"),
            ("a", "d"),
            ("b", "a"),
            ("b", "e"),
            ("e", "f")
        ]
        model.translation_quality_grade = 1
        graph = TranslationGraph([model])

        assert graph.find_optimal_translation_path("a", "f") == [(("a", "b"), model),
                                                                 (("b", "e"), model),
                                                                 (("e", "f"), model),
                                                                 ]
