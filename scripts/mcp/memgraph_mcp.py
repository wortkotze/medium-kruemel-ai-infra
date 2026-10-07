#!/usr/bin/env python3
"""
Memgraph Knowledge Graph & Multi-Hop Reasoning FastMCP Server.
Allows Architect, DevOps, and Product Owner agents to query and enrich the live
system knowledge graph, map dependencies, and perform relation-based reasoning.
"""
import os
import re
import sys
from pathlib import Path

# Add vendor directory for pure-python neo4j driver
VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase

BOLT_URL = os.getenv("MEMGRAPH_BOLT_URL", "bolt://memgraph:7687")
BOLT_USER = os.getenv("MEMGRAPH_USER", "")
BOLT_PASSWORD = os.getenv("MEMGRAPH_PASSWORD", "")

mcp = FastMCP("Memgraph Knowledge Graph MCP")


def _get_driver():
    """Create or return Neo4j Bolt driver connected to Memgraph."""
    auth = (BOLT_USER, BOLT_PASSWORD) if BOLT_USER else None
    return GraphDatabase.driver(BOLT_URL, auth=auth)


def _serialize_value(val):
    """Serialize Neo4j/Memgraph data types to standard JSON types."""
    if hasattr(val, "_properties"):
        return dict(val._properties)
    elif isinstance(val, (list, tuple)):
        return [_serialize_value(v) for v in val]
    elif isinstance(val, dict):
        return {k: _serialize_value(v) for k, v in val.items()}
    return val


def _sanitize_identifier(identifier: str) -> str:
    """Ensure Cypher labels and relation types contain only safe alphanumeric characters."""
    clean = re.sub(r"[^\w]+", "_", identifier.strip())
    if not clean or clean[0].isdigit():
        clean = f"Entity_{clean}"
    return clean


@mcp.tool()
def query_graph(cypher: str) -> dict:
    """Execute arbitrary Cypher queries on the Memgraph Knowledge Graph.

    Args:
        cypher: Cypher query to execute (e.g. 'MATCH (n:Service) RETURN n.name, n.port').
    """
    driver = None
    try:
        driver = _get_driver()
        with driver.session() as session:
            result = session.run(cypher)
            records = []
            for record in result:
                row = {}
                for key, val in record.items():
                    row[key] = _serialize_value(val)
                records.append(row)

            return {
                "status": "success",
                "query": cypher,
                "record_count": len(records),
                "records": records
            }
    except Exception as e:
        return {"status": "error", "query": cypher, "error": f"Cypher query execution failed: {str(e)}"}
    finally:
        if driver:
            driver.close()


@mcp.tool()
def add_graph_entity(label: str, name: str, properties: dict = None) -> dict:
    """Add or update an entity node (Service, Database, Agent, Model, Spec) in the knowledge graph.

    Args:
        label: Node label/category (e.g. 'Service', 'Tool', 'Agent', 'Database', 'Component').
        name: Unique primary name of the entity (e.g. 'qdrant-vector', 'agent-coder').
        properties: Additional key-value attributes (e.g. {'port': 6333, 'ram_limit': '512M'}).
    """
    driver = None
    try:
        clean_label = _sanitize_identifier(label)
        props = properties if properties else {}
        props["name"] = name.strip()

        driver = _get_driver()
        query = f"""
        MERGE (n:{clean_label} {{name: $name}})
        SET n += $props
        RETURN n, labels(n) as labels
        """
        with driver.session() as session:
            res = session.run(query, name=name.strip(), props=props)
            record = res.single()
            if not record:
                return {"status": "error", "error": f"Failed to merge entity '{name}'."}

            return {
                "status": "success",
                "entity": _serialize_value(record["n"]),
                "labels": record["labels"]
            }
    except Exception as e:
        return {"status": "error", "error": f"Failed to add entity: {str(e)}"}
    finally:
        if driver:
            driver.close()


@mcp.tool()
def add_graph_relation(source: str, target: str, relation: str) -> dict:
    """Create a directional relationship between two existing entities.

    Args:
        source: Name of the origin entity (e.g. 'agent-coder').
        target: Name of the destination entity (e.g. 'sandbox_mcp').
        relation: Relationship type (e.g. 'DEPENDS_ON', 'CALLS', 'MANAGES', 'COMMUNICATES_WITH').
    """
    driver = None
    try:
        clean_rel = _sanitize_identifier(relation).upper()
        driver = _get_driver()
        query = f"""
        MATCH (a {{name: $source}}), (b {{name: $target}})
        MERGE (a)-[r:{clean_rel}]->(b)
        RETURN a.name as source, type(r) as relation, b.name as target
        """
        with driver.session() as session:
            res = session.run(query, source=source.strip(), target=target.strip())
            record = res.single()
            if not record:
                return {
                    "status": "error",
                    "error": f"Could not link '{source}' -> '{target}'. Ensure both nodes exist with exact matching names."
                }

            return {
                "status": "success",
                "source": record["source"],
                "relation": record["relation"],
                "target": record["target"]
            }
    except Exception as e:
        return {"status": "error", "error": f"Failed to create relation: {str(e)}"}
    finally:
        if driver:
            driver.close()


@mcp.tool()
def get_system_dependencies(service_name: str) -> dict:
    """Inspect all incoming and outgoing dependencies of a service or component in the graph.

    Args:
        service_name: Name of the service to inspect (e.g. 'LiteLLM Gateway', 'Langfuse', 'n8n').
    """
    driver = None
    try:
        driver = _get_driver()
        query = """
        MATCH (target)
        WHERE toLower(target.name) = toLower($name)
        OPTIONAL MATCH (target)-[r_out]->(downstream)
        OPTIONAL MATCH (upstream)-[r_in]->(target)
        RETURN
            target.name as service,
            labels(target) as labels,
            collect(DISTINCT {relation: type(r_out), target: downstream.name}) as outgoing,
            collect(DISTINCT {relation: type(r_in), source: upstream.name}) as incoming
        """
        with driver.session() as session:
            res = session.run(query, name=service_name.strip())
            record = res.single()
            if not record or not record["service"]:
                return {"status": "error", "error": f"Service '{service_name}' not found in knowledge graph."}

            # Filter null entries from collect
            outgoing = [o for o in record["outgoing"] if o.get("target") is not None]
            incoming = [i for i in record["incoming"] if i.get("source") is not None]

            return {
                "status": "success",
                "service": record["service"],
                "labels": record["labels"],
                "outgoing_dependencies": outgoing,
                "incoming_dependencies": incoming
            }
    except Exception as e:
        return {"status": "error", "error": f"Failed to retrieve dependencies: {str(e)}"}
    finally:
        if driver:
            driver.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")
