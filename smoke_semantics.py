# This is a smoke test for testing the semantic model loading and working properly

import asyncio

from app.semantic.parser import load_definitions_from_directory
from app.semantic.registry import SemanticRegistry
from app.semantic.search import Metric_Search_Engine

async def main(self):
    