"""
Google Flow & Veo Cinematic Director Package.
"""

__version__ = "1.1.0"
__author__ = "Agentic Marketing OS"

from flow_veo_director.builder import VeoShotBlueprint
from flow_veo_director.continuity import FlowSequence, FlowShot
from flow_veo_director.timing import evaluate_segment_timing, count_words
from flow_veo_director.validator import ScriptValidator
from flow_veo_director.agent import FlowVeoDirectorAgent, run_interactive_agent

__all__ = [
    "VeoShotBlueprint",
    "FlowSequence",
    "FlowShot",
    "evaluate_segment_timing",
    "count_words",
    "ScriptValidator",
    "FlowVeoDirectorAgent",
    "run_interactive_agent",
]
