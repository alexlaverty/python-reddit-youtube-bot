"""Functions to extract key phrases out of text."""
import logging
from typing import List

from multi_rake import Rake

logger = logging.getLogger(__name__)


def get_keywords(text) -> List[str]:
    """Extract key phrases out of a block of text.

    Args:
        text: The text to be processed.

    Returns:
        A selection of key phrases.
    """
    rake: Rake = Rake()
    keywords: List[str] = rake.apply(text)
    return keywords


if __name__ == "__main__":
    text = (
        "Compatibility of systems of linear constraints over the set of "
        "natural numbers. Criteria of compatibility of a system of linear "
        "Diophantine equations, strict inequations, and nonstrict inequations "
        "are considered. Upper bounds for components of a minimal set of "
        "solutions and algorithms of construction of minimal generating sets "
        "of solutions for all types of systems are given. These criteria and "
        "the corresponding algorithms for constructing a minimal supporting "
        "set of solutions can be used in solving all the considered types of "
        "systems and systems of mixed types."
    )

    keywords: List[str] = get_keywords(text)
    logger.info(keywords[:10])
