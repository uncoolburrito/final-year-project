import json
import os
import logging
from typing import List, Dict, Optional
from src.common.models import Snippet, Profile, Settings
from src.common.constants import DATA_DIR

logger = logging.getLogger(__name__)

class Store:
    def __init__(self):
        self.snippets_file = os.path.join(DATA_DIR, "snippets.json")
        self.profiles_file = os.path.join(DATA_DIR, "profiles.json")
        self.settings_file = os.path.join(DATA_DIR, "settings.json")
        
        self.snippets: List[Snippet] = []
        self.profiles: List[Profile] = []
        self.settings: Settings = Settings()
        
        self._ensure_data_dir()
        self.load()

    def _ensure_data_dir(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def load(self):
        self.snippets = self._load_file(self.snippets_file, Snippet, default=[])
        self.profiles = self._load_file(self.profiles_file, Profile, default=[])
        self.settings = self._load_file(self.settings_file, Settings, default=Settings())
        logger.info("Data loaded successfully")

    def save(self):
        self._save_file(self.snippets_file, [s.model_dump(mode='json') for s in self.snippets])
        self._save_file(self.profiles_file, [p.model_dump(mode='json') for p in self.profiles])
        self._save_file(self.settings_file, self.settings.model_dump(mode='json'))
        logger.info("Data saved successfully")

    def _load_file(self, path: str, model_cls, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(default, list):
                return [model_cls(**item) for item in data]
            else:
                return model_cls(**data)
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return default

    def _save_file(self, path: str, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save {path}: {e}")

    # CRUD Operations
    def add_snippet(self, snippet: Snippet):
        self.snippets.append(snippet)
        self.save()

    def update_snippet(self, snippet: Snippet):
        for i, s in enumerate(self.snippets):
            if s.id == snippet.id:
                self.snippets[i] = snippet
                break
        self.save()

    def delete_snippet(self, snippet_id: str):
        self.snippets = [s for s in self.snippets if s.id != snippet_id]
        self.save()

    def get_snippet_by_abbreviation(self, abbr: str) -> Optional[Snippet]:
        # Simple linear search for now, can be optimized with a map
        for s in self.snippets:
            if s.is_active and s.abbreviation == abbr:
                return s
        return None
