#!/usr/bin/env python3
"""
Persistent Memory Skill
Integrates with jacklevin74/persistent-agent-memory
"""
import sqlite3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class MemoryEntry:
    timestamp: str
    agent_id: str
    task: str
    outcome: str
    context: Dict[str, Any]

class PersistentMemorySkill:
    """
    Skill for managing persistent agent memory across sessions
    """
    
    def __init__(self, base_path: str = "~/persistent-agent-memory"):
        self.base_path = os.path.expanduser(base_path)
        self.data_path = os.path.join(self.base_path, "data")
        self.memory_path = os.path.join(self.base_path, "memory", "agents")
        self.shared_brain_path = os.path.join(self.base_path, "shared-brain")
        
        # Ensure directories exist
        os.makedirs(self.memory_path, exist_ok=True)
        os.makedirs(self.shared_brain_path, exist_ok=True)
        
    def _get_db(self, db_name: str) -> sqlite3.Connection:
        """Get database connection"""
        db_path = os.path.join(self.data_path, f"{db_name}.db")
        return sqlite3.connect(db_path)
    
    def log_knowledge(self, fact: str, category: str = "general", 
                     source: str = "", agent_id: str = "kimi") -> bool:
        """Add a knowledge fact to the knowledge base"""
        try:
            conn = self._get_db("knowledge")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO knowledge (timestamp, category, fact, source, agent_id)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), category, fact, source, agent_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging knowledge: {e}")
            return False
    
    def recall_knowledge(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Search knowledge base"""
        try:
            conn = self._get_db("knowledge")
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT * FROM knowledge 
                    WHERE category = ? AND fact LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (category, f"%{query}%", limit))
            else:
                cursor.execute("""
                    SELECT * FROM knowledge 
                    WHERE fact LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (f"%{query}%", limit))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error recalling knowledge: {e}")
            return []
    
    def write_agent_memory(self, agent_id: str, entry: str, 
                          tags: List[str] = None) -> bool:
        """
        Write to agent's daily memory log
        """
        try:
            agent_dir = os.path.join(self.memory_path, agent_id)
            os.makedirs(agent_dir, exist_ok=True)
            
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(agent_dir, f"{today}.md")
            
            timestamp = datetime.now().strftime("%H:%M")
            tags_str = " ".join([f"#{tag}" for tag in (tags or [])])
            
            log_entry = f"\n## [{timestamp}] {tags_str}\n{entry}\n"
            
            with open(log_file, "a") as f:
                f.write(log_entry)
            
            return True
        except Exception as e:
            print(f"Error writing agent memory: {e}")
            return False
    
    def read_agent_memory(self, agent_id: str, days: int = 2) -> List[str]:
        """
        Read agent's memory from last N days
        """
        try:
            agent_dir = os.path.join(self.memory_path, agent_id)
            if not os.path.exists(agent_dir):
                return []
            
            memories = []
            for i in range(days):
                date = datetime.now()
                if i > 0:
                    from datetime import timedelta
                    date = date - timedelta(days=i)
                
                date_str = date.strftime("%Y-%m-%d")
                log_file = os.path.join(agent_dir, f"{date_str}.md")
                
                if os.path.exists(log_file):
                    with open(log_file, "r") as f:
                        memories.append(f.read())
            
            return memories
        except Exception as e:
            print(f"Error reading agent memory: {e}")
            return []
    
    def update_shared_brain(self, brain_file: str, data: Dict) -> bool:
        """
        Update shared brain JSON files for cross-agent communication
        """
        try:
            brain_path = os.path.join(self.shared_brain_path, f"{brain_file}.json")
            
            # Read existing
            existing = {}
            if os.path.exists(brain_path):
                with open(brain_path, "r") as f:
                    existing = json.load(f)
            
            # Update
            existing.update(data)
            existing["lastUpdatedAt"] = datetime.now().isoformat()
            existing["lastUpdatedBy"] = "kimi"
            
            # Write back
            with open(brain_path, "w") as f:
                json.dump(existing, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating shared brain: {e}")
            return False
    
    def read_shared_brain(self, brain_file: str) -> Dict:
        """Read from shared brain"""
        try:
            brain_path = os.path.join(self.shared_brain_path, f"{brain_file}.json")
            
            if os.path.exists(brain_path):
                with open(brain_path, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error reading shared brain: {e}")
            return {}
    
    def boot_context(self, agent_id: str) -> str:
        """
        Generate boot context for an agent
        Loads memory and relevant shared brain data
        """
        context_parts = []
        
        # Load recent memory
        memories = self.read_agent_memory(agent_id, days=2)
        if memories:
            context_parts.append("## Recent Memory\n" + "\n".join(memories))
        
        # Load shared brain files relevant to this agent
        brain_files = ["intel-feed.json", "agent-handoffs.json"]
        for bf in brain_files:
            data = self.read_shared_brain(bf)
            if data.get("entries"):
                context_parts.append(f"## {bf}\n" + json.dumps(data["entries"][-5:], indent=2))
        
        return "\n\n".join(context_parts)
    
    def log_crm_contact(self, name: str, platform: str, 
                       notes: str = "", status: str = "active") -> bool:
        """Log a CRM contact"""
        try:
            conn = self._get_db("crm")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO contacts (name, platform, notes, status, last_contact, first_contact)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name, platform) DO UPDATE SET
                    notes = excluded.notes,
                    status = excluded.status,
                    last_contact = excluded.last_contact
            """, (name, platform, notes, status, datetime.now().isoformat(), 
                  datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging CRM contact: {e}")
            return False

# Global instance
_memory = None

def get_memory() -> PersistentMemorySkill:
    global _memory
    if _memory is None:
        _memory = PersistentMemorySkill()
    return _memory
