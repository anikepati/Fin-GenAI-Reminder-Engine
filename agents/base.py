# cmbs_reminder_system/agents/base.py
import redis
import json
import datetime
from pydantic import BaseModel
from typing import Optional, Any

# Configure Redis connection
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

class Agent:
    """Base class for all agents to provide common functionalities."""
    def __init__(self, name: str):
        self.name = name
        print(f"[{self.name}] Initialized.")

    def _get_redis_key(self, obj_type: str, obj_id: str) -> str:
        return f"{obj_type}:{obj_id}"

    def _save_to_redis(self, obj_type: str, obj: BaseModel):
        key = self._get_redis_key(obj_type, getattr(obj, f'{obj_type}_id'))
        r.set(key, obj.model_dump_json())

    def _load_from_redis(self, obj_type: str, obj_id: str, model_class: type[BaseModel]) -> Optional[BaseModel]:
        key = self._get_redis_key(obj_type, obj_id)
        obj_json = r.get(key)
        if obj_json:
            return model_class.model_validate_json(obj_json)
        return None

    def _update_in_redis(self, obj_type: str, obj_id: str, updates: dict):
        key = self._get_redis_key(obj_type, obj_id)
        obj_json = r.get(key)
        if obj_json:
            obj_data = json.loads(obj_json)
            obj_data.update(updates)
            r.set(key, json.dumps(obj_data))
            return True
        return False