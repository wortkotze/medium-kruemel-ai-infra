#!/usr/bin/env python3
"""
Synchronizes config/skills.yaml into LiteLLM PostgreSQL Skills & Plugins Database
"""
import os
import sys
import json
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_SKILLS = ROOT_DIR / "config" / "skills.yaml"

async def sync():
    try:
        import yaml
    except ImportError:
        yaml = None

    if not CONFIG_SKILLS.exists():
        print("No config/skills.yaml found.")
        return

    skills = []
    if yaml:
        with open(CONFIG_SKILLS, "r") as f:
            data = yaml.safe_load(f)
            skills = data.get("skills", [])
    
    if not skills:
        print("No skills defined in config/skills.yaml.")
        return

    # Use Prisma inside container
    try:
        from prisma import Prisma
    except ImportError:
        print("Prisma not available in local environment, will run inside container.")
        return

    db = Prisma()
    await db.connect()
    
    for skill in skills:
        skill_id = skill.get("skill_id")
        name = skill.get("display_title", skill_id)
        desc = skill.get("description", "")
        metadata = skill.get("metadata", {})
        version = metadata.get("version", "1.0.0")
        
        manifest = {
            "name": name,
            "description": desc,
            "version": version,
            "category": metadata.get("category", "productivity"),
            "instructions": skill.get("instructions", ""),
            "source": {"type": "local", "path": skill.get("source", "")}
        }
        
        existing = await db.litellm_claudecodeplugintable.find_unique(where={"id": skill_id})
        if existing:
            await db.litellm_claudecodeplugintable.update(
                where={"id": skill_id},
                data={
                    "name": name,
                    "version": version,
                    "description": desc,
                    "manifest_json": json.dumps(manifest),
                    "enabled": True
                }
            )
            print(f"  ✓ Updated skill: {name} ({skill_id})")
        else:
            await db.litellm_claudecodeplugintable.create(
                data={
                    "id": skill_id,
                    "name": name,
                    "version": version,
                    "description": desc,
                    "manifest_json": json.dumps(manifest),
                    "files_json": json.dumps({}),
                    "enabled": True
                }
            )
            print(f"  ✓ Created skill: {name} ({skill_id})")

    await db.disconnect()
    print("✅ All skills synchronized with LiteLLM database.")

if __name__ == "__main__":
    asyncio.run(sync())
