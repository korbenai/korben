"""Entropy task - explains entropy and writes a haiku about it."""

import controlflow as cf


def run(**kwargs):
    """Run the entropy task with scientist and poet agents."""
    scientist = cf.Agent(name="Scientist", instructions="Explain scientific concepts.")
    poet = cf.Agent(name="Poet", instructions="Write poetic content.")
    
    result = cf.run(
        "Explain entropy briefly, then write a haiku about it",
        agents=[scientist, poet]
    )
    
    return result