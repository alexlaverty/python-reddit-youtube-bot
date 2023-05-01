"""Functions to extract key phrases out of text."""
from multi_rake import Rake


def get_keywords(text):
    """Extract key phrases out of a block of text.

    Args:
        text: The text to be processed.

    Returns:
        A selection of key phrases.
    """
    rake = Rake()
    keywords = rake.apply(text)
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

    keywords = get_keywords(text)
    print(keywords[:10])
