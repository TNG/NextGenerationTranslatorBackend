import logging
import math
from typing import Tuple, Dict, List, Optional, Set, Type

from dijkstra import Graph, DijkstraSPF

from translator_models.translator_model import TranslatorModel
_logger = logging.getLogger(__name__)

class TranslationGraph:
    def __init__(self, model_classes: Optional[List[Type[TranslatorModel]]]):
        self.translation_models: Dict[Tuple[str, str], Type[TranslatorModel]] = {}
        self.translation_graph = Graph()
        if model_classes:
            for model in model_classes:
                self.add_model(model)

    def add_model(self, model_class: Type[TranslatorModel]):
        for language_pair in model_class.available_language_pairs:
            self._add_translation_model(language_pair, model_class)

    def __contains__(self, language: str):
        """ Returns true if the translation graph contains the language as node. """
        return language in self.translation_graph.get_nodes()

    def _add_translation_model(self, language_pair: Tuple[str, str], model_class: Type[TranslatorModel]):
        if language_pair in self.translation_models.keys():
            current_translation_grade = self.translation_models[language_pair].translation_quality_grade
            new_translation_grade = model_class.translation_quality_grade
            if current_translation_grade <= new_translation_grade:
                _logger.info(
                    f"Not adding {model_class.model_name} to the translation graph for {language_pair}, since {self.translation_models[language_pair].model_name} is a better option.")
                return

        self.translation_models[language_pair] = model_class
        self.translation_graph.add_edge(language_pair[0], language_pair[1], model_class.translation_quality_grade)

    def find_optimal_translation_path(self, source_language, target_language):
        translation_path_finder = DijkstraSPF(self.translation_graph, source_language)
        translation_path = translation_path_finder.get_path(target_language)

        translation_steps = [(intermediate_translations, self.translation_models[intermediate_translations]) for
                             intermediate_translations in zip(translation_path[:-1], translation_path[1:])]
        return translation_steps

    @staticmethod
    def format_translation_path(translation_path, source_language, target_language) -> str:
        translation_string = source_language
        for language_pair, translation_model in translation_path:
            translation_string += f" --|{translation_model.model_name}|--> {language_pair[1]}"
        return f"Translating from {source_language} to {target_language} via {translation_string}"

    @property
    def _inverted_translation_graph(self) -> Graph:
        """
        :return: The translation graph with edge-directions inverted.
        """
        adjacent_nodes = {n: self.translation_graph.get_adjacent_nodes(n)
                          for n in self.translation_graph.get_nodes()}
        inverted_graph = Graph()
        for u, neighbors in adjacent_nodes.items():
            for v in neighbors:
                inverted_graph.add_edge(v, u, self.translation_graph.get_edge_weight(u, v))
        return inverted_graph

    def get_strongly_connected_component(self, root_language: str) -> Set[str]:
        """ Obtains the strongly connected component for a given root language, i.e. all languages
        that are reachable (translatable) _from_ this language as well as _to_ this
        language.

        :param root_language:
        :return:
        """

        root_dijkstra = DijkstraSPF(self.translation_graph, root_language)
        root_reachable_nodes = {n for n in self.translation_graph.get_nodes()
                                if root_dijkstra.get_distance(n) < math.inf}

        inverted_dijkstra = DijkstraSPF(self._inverted_translation_graph, root_language)

        nodes_reaching_root = {n for n in self.translation_graph.get_nodes()
                               if inverted_dijkstra.get_distance(n) < math.inf}

        return nodes_reaching_root & root_reachable_nodes


