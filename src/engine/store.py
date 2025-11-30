import json
import os
import logging
from typing import List, Dict, Optional
from src.common.models import Snippet, Profile, Settings
from src.common.constants import DATA_DIR

logger = logging.getLogger(__name__)

class Store:
    def __init__(self):
        self.store_file = os.path.join(DATA_DIR, "store.json")
        self.snippets: List[Snippet] = []
        self._ensure_data_dir()
        self.load()

    def _ensure_data_dir(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def load(self) -> None:
        if not os.path.exists(self.store_file):
            self.snippets = []
            return

        try:
            with open(self.store_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.snippets = [Snippet.from_dict(item) for item in data]
            logger.info(f"Loaded {len(self.snippets)} snippets from {self.store_file}")
        except Exception as e:
            logger.error(f"Failed to load store: {e}")
            self.snippets = []

    def save(self) -> None:
        try:
            data = [s.to_dict() for s in self.snippets]
            with open(self.store_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info("Store saved successfully")
        except Exception as e:
            logger.error(f"Failed to save store: {e}")

    def add_snippet(self, snippet: Snippet) -> None:
        if not snippet.id:
            import uuid
            snippet.id = uuid.uuid4().hex
        self.snippets.append(snippet)
        self.save()

    def update_snippet(self, snippet: Snippet) -> None:
        for i, s in enumerate(self.snippets):
            if s.id == snippet.id:
                self.snippets[i] = snippet
                break
        self.save()

    def delete_snippet(self, snippet_id: str) -> None:
        self.snippets = [s for s in self.snippets if s.id != snippet_id]
        self.save()

    def get_snippet_by_abbreviation(self, abbr: str) -> Optional[Snippet]:
        for s in self.snippets:
            if s.is_active and s.abbreviation == abbr:
                return s
        return None
