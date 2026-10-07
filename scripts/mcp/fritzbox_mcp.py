#!/usr/bin/env python3
"""
FRITZ!Box Home Network, Diagnostics & Smart Home MCP Server
Built with Python FastMCP (communicates directly with FRITZ!Box TR-064 API)
Requires only standard library (urllib, xml.etree, hashlib, ssl)
"""
import os
import sys
import json
import ssl
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from mcp.server.fastmcp import FastMCP

FRITZBOX_HOST = os.getenv("FRITZBOX_HOST", "192.168.178.1")
FRITZBOX_PORT = int(os.getenv("FRITZBOX_PORT", "49443"))
raw_user = os.getenv("FRITZBOX_USER", "")
# Automatically extract username if user specified an email address (e.g. steve@hatkeineAhnung.de -> steve)
FRITZBOX_USER = raw_user.split("@")[0] if "@" in raw_user else raw_user
FRITZBOX_PASSWORD = os.getenv("FRITZBOX_PASSWORD", "")
FRITZBOX_USE_SSL = os.getenv("FRITZBOX_USE_SSL", "true").lower() in ("true", "1", "yes")

mcp = FastMCP("FRITZ!Box Network & Smart Home MCP")

def _get_base_url() -> str:
    scheme = "https" if FRITZBOX_USE_SSL else "http"
    return f"{scheme}://{FRITZBOX_HOST}:{FRITZBOX_PORT}"

def _build_opener():
    handlers = []
    if FRITZBOX_USE_SSL:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        handlers.append(urllib.request.HTTPSHandler(context=ctx))

    if FRITZBOX_PASSWORD:
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        base = _get_base_url()
        password_mgr.add_password(None, base, FRITZBOX_USER, FRITZBOX_PASSWORD)
        handlers.append(urllib.request.HTTPDigestAuthHandler(password_mgr))

    return urllib.request.build_opener(*handlers)

def _soap_call(service_type: str, control_url: str, action: str, arguments: dict = None) -> dict:
    base_url = _get_base_url()
    url = f"{base_url.rstrip('/')}{control_url}"

    args_xml = ""
    if arguments:
        for k, v in arguments.items():
            args_xml += f"<{k}>{v}</{k}>"

    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:{action} xmlns:u="{service_type}">
      {args_xml}
    </u:{action}>
  </s:Body>
</s:Envelope>"""

    headers = {
        "Content-Type": 'text/xml; charset="utf-8"',
        "SoapAction": f'"{service_type}#{action}"',
        "User-Agent": "LiteLLM-FritzBox-MCP/2.0"
    }

    opener = _build_opener()
    req = urllib.request.Request(url, data=soap_body.encode("utf-8"), headers=headers, method="POST")

    try:
        with opener.open(req, timeout=12) as response:
            xml_data = response.read().decode("utf-8")
            return _parse_soap_response(xml_data)
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        if e.code == 401:
            return {
                "error": "Authentication failed (HTTP 401).",
                "hint": f"Check user '{FRITZBOX_USER}' and password in .env. Port={FRITZBOX_PORT}, SSL={FRITZBOX_USE_SSL}"
            }
        # Check if UPnP error XML
        if "<UPnPError" in err_msg:
            try:
                root = ET.fromstring(err_msg)
                code = root.findtext(".//errorCode") or root.findtext(".//{urn:dslforum-org:control-1-0}errorCode")
                desc = root.findtext(".//errorDescription") or root.findtext(".//{urn:dslforum-org:control-1-0}errorDescription")
                return {"error": f"UPnPError {code}: {desc}"}
            except Exception:
                pass
        return {"error": f"HTTP {e.code}", "details": err_msg[:300]}
    except Exception as e:
        return {"error": str(e)}

def _parse_soap_response(xml_str: str) -> dict:
    try:
        root = ET.fromstring(xml_str)
        body = None
        for elem in root:
            if elem.tag.endswith("Body"):
                body = elem
                break
        if body is None or len(body) == 0:
            return {"raw_response": xml_str}

        response_node = body[0]
        result = {}
        for child in response_node:
            tag_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            result[tag_name] = child.text or ""
        return result
    except Exception as e:
        return {"error": f"Failed to parse XML: {str(e)}", "raw": xml_str}

# ─── 1. System, Logs & Device Info ──────────────────────────────────────────

@mcp.tool()
def get_fritzbox_info() -> dict:
    """Retrieve FRITZ!Box hardware model, serial number, firmware version, and uptime."""
    info = _soap_call(
        service_type="urn:dslforum-org:service:DeviceInfo:1",
        control_url="/upnp/control/deviceinfo",
        action="GetInfo"
    )
    if "error" not in info:
        uptime = int(info.get("NewUpTime", 0))
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        return {
            "model_name": info.get("NewModelName", "FRITZ!Box"),
            "manufacturer": info.get("NewManufacturerName", "AVM"),
            "software_version": info.get("NewSoftwareVersion", ""),
            "serial_number": info.get("NewSerialNumber", ""),
            "hardware_version": info.get("NewHardwareVersion", ""),
            "uptime_seconds": uptime,
            "uptime_human": f"{days}d {hours}h {minutes}m"
        }
    return info

@mcp.tool()
def get_system_logs(filter_keyword: str = "", max_entries: int = 50) -> dict:
    """Retrieve the recent system event log (System-Ereignisse) from the FRITZ!Box.
    
    Args:
        filter_keyword: Optional keyword to filter log lines (e.g. 'WLAN', 'IPv6', 'Internet', 'DHCP', 'Fehler').
        max_entries: Maximum number of recent log entries to return (default: 50).
    """
    res = _soap_call(
        service_type="urn:dslforum-org:service:DeviceInfo:1",
        control_url="/upnp/control/deviceinfo",
        action="GetDeviceLog"
    )
    if "error" in res:
        return res

    raw_log = res.get("NewDeviceLog", "")
    lines = [line.strip() for line in raw_log.split("\n") if line.strip()]

    if filter_keyword:
        kw = filter_keyword.lower()
        lines = [line for line in lines if kw in line.lower()]

    recent = lines[:max_entries]
    return {
        "filter": filter_keyword or "none",
        "returned_entries": len(recent),
        "total_available_entries": len(lines),
        "log_entries": recent
    }

# ─── 2. Internet / WAN & Fiber Diagnostics ──────────────────────────────────

@mcp.tool()
def get_wan_status() -> dict:
    """Retrieve WAN / Internet connection status, external IPv4/IPv6 addresses, DNS servers, and link bitrates."""
    ip_info = _soap_call(
        service_type="urn:dslforum-org:service:WANIPConnection:1",
        control_url="/upnp/control/wanipconnection1",
        action="GetInfo"
    )
    if "error" in ip_info:
        ip_info = _soap_call(
            service_type="urn:dslforum-org:service:WANPPPConnection:1",
            control_url="/upnp/control/wanpppconn1",
            action="GetInfo"
        )

    link_info = _soap_call(
        service_type="urn:dslforum-org:service:WANCommonInterfaceConfig:1",
        control_url="/upnp/control/wancommonifconfig1",
        action="GetCommonLinkProperties"
    )

    result = {}
    if "error" not in ip_info:
        result.update({
            "external_ip": ip_info.get("NewExternalIPAddress", ""),
            "connection_status": ip_info.get("NewConnectionStatus", ""),
            "uptime_seconds": ip_info.get("NewUptime", ""),
            "dns_servers": ip_info.get("NewDNSServers", ""),
            "nat_enabled": ip_info.get("NewNATEnabled") == "1",
        })
    else:
        result["ip_error"] = ip_info

    if "error" not in link_info:
        down_bps = int(link_info.get("NewLayer1DownstreamMaxBitRate", 0))
        up_bps = int(link_info.get("NewLayer1UpstreamMaxBitRate", 0))
        result.update({
            "physical_link_status": link_info.get("NewPhysicalLinkStatus", ""),
            "max_downstream_mbps": round(down_bps / 1_000_000, 2) if down_bps else "N/A",
            "max_upstream_mbps": round(up_bps / 1_000_000, 2) if up_bps else "N/A",
        })

    return result

@mcp.tool()
def get_fiber_diagnostics() -> dict:
    """Retrieve Optical Fiber (Glasfaser) SFP module information, optical signal levels, and wavelength."""
    res = _soap_call(
        service_type="urn:dslforum-org:service:X_AVM-DE_WANFiber:1",
        control_url="/upnp/control/x_wanfiber",
        action="GetInfo"
    )
    if "error" in res:
        return res

    return {
        "sfp_vendor": res.get("NewSFPVendor", ""),
        "sfp_serial_number": res.get("NewSFPSerialNumber", ""),
        "tx_wavelength_nm": res.get("NewTXWaveLength", ""),
        "optical_signal_level": res.get("NewOpticalSignalLevel", ""),
        "transmit_optical_level": res.get("NewTransmitOpticalLevel", ""),
        "fiber_mode": res.get("NewFiberMode", "")
    }

@mcp.tool()
def reconnect_wan() -> dict:
    """Request a reconnection of the Internet/WAN link (renews the external IP address)."""
    res = _soap_call(
        service_type="urn:dslforum-org:service:WANIPConnection:1",
        control_url="/upnp/control/wanipconnection1",
        action="ForceTermination"
    )
    if "error" in res:
        res = _soap_call(
            service_type="urn:dslforum-org:service:WANPPPConnection:1",
            control_url="/upnp/control/wanpppconn1",
            action="ForceTermination"
        )
    if "error" in res:
        return res
    return {"success": True, "message": "WAN reconnection triggered. A new IP address will be assigned."}

# ─── 3. Local Network Devices & Topology ─────────────────────────────────────

@mcp.tool()
def list_network_devices(active_only: bool = True, limit: int = 50) -> dict:
    """Scan and list all devices connected to the home network (IP, MAC, Hostname, Ethernet/WLAN, Active state).
    
    Args:
        active_only: If True, returns only currently active/online devices (default: True).
        limit: Maximum number of devices to return (default: 50).
    """
    from concurrent.futures import ThreadPoolExecutor

    count_res = _soap_call(
        service_type="urn:dslforum-org:service:Hosts:1",
        control_url="/upnp/control/hosts",
        action="GetHostNumberOfEntries"
    )
    if "error" in count_res:
        return count_res

    num_entries = int(count_res.get("NewHostNumberOfEntries", 0))
    # Scan up to 60 indices concurrently in ~1 second
    scan_count = min(num_entries, 60)

    def _fetch_single(idx: int):
        return _soap_call(
            service_type="urn:dslforum-org:service:Hosts:1",
            control_url="/upnp/control/hosts",
            action="GetGenericHostEntry",
            arguments={"NewIndex": str(idx)}
        )

    with ThreadPoolExecutor(max_workers=10) as executor:
        raw_entries = list(executor.map(_fetch_single, range(scan_count)))

    devices = []
    for entry in raw_entries:
        if not entry or "error" in entry:
            continue
        is_active = entry.get("NewActive") == "1"
        if active_only and not is_active:
            continue

        devices.append({
            "hostname": entry.get("NewHostName", "Unknown"),
            "ip_address": entry.get("NewIPAddress", ""),
            "mac_address": entry.get("NewMACAddress", ""),
            "interface_type": entry.get("NewInterfaceType", ""),
            "active": is_active,
            "lease_time_remaining": entry.get("NewLeaseTimeRemaining", "")
        })
        if len(devices) >= limit:
            break

    return {
        "total_hosts_in_table": num_entries,
        "scanned_indices": scan_count,
        "returned_devices_count": len(devices),
        "devices": devices
    }

@mcp.tool()
def get_device_details(identifier: str) -> dict:
    """Retrieve detailed network information for a specific host by its IP or MAC address.
    
    Args:
        identifier: Either an IPv4 address (e.g. '192.168.178.21') or a MAC address (e.g. '00:17:88:7A:92:13').
    """
    # Check if identifier looks like an IP address
    if "." in identifier and not ":" in identifier:
        entry = _soap_call(
            service_type="urn:dslforum-org:service:Hosts:1",
            control_url="/upnp/control/hosts",
            action="GetSpecificHostEntry",
            arguments={"NewIPAddress": identifier.strip()}
        )
        if "error" not in entry:
            return {
                "hostname": entry.get("NewHostName", "Unknown"),
                "ip_address": identifier.strip(),
                "mac_address": entry.get("NewMACAddress", ""),
                "interface_type": entry.get("NewInterfaceType", ""),
                "active": entry.get("NewActive") == "1",
                "lease_time_remaining": entry.get("NewLeaseTimeRemaining", "")
            }

    # MAC lookup or fallback
    mac_clean = identifier.strip().upper()
    count_res = _soap_call(
        service_type="urn:dslforum-org:service:Hosts:1",
        control_url="/upnp/control/hosts",
        action="GetHostNumberOfEntries"
    )
    num_entries = int(count_res.get("NewHostNumberOfEntries", 0)) if "error" not in count_res else 0
    for i in range(min(num_entries, 150)):
        entry = _soap_call(
            service_type="urn:dslforum-org:service:Hosts:1",
            control_url="/upnp/control/hosts",
            action="GetGenericHostEntry",
            arguments={"NewIndex": str(i)}
        )
        if entry.get("NewMACAddress", "").upper() == mac_clean or entry.get("NewIPAddress") == identifier.strip():
            return {
                "hostname": entry.get("NewHostName", "Unknown"),
                "ip_address": entry.get("NewIPAddress", ""),
                "mac_address": entry.get("NewMACAddress", ""),
                "interface_type": entry.get("NewInterfaceType", ""),
                "active": entry.get("NewActive") == "1",
                "lease_time_remaining": entry.get("NewLeaseTimeRemaining", "")
            }

    return {"error": f"Device with identifier '{identifier}' not found in network host table."}

@mcp.tool()
def wake_on_lan(mac_address: str) -> dict:
    """Send a Wake-on-LAN magic packet from the FRITZ!Box to start up a local computer/server.
    
    Args:
        mac_address: MAC address of target device (e.g. '00:11:22:33:44:55').
    """
    clean_mac = mac_address.strip().upper()
    res = _soap_call(
        service_type="urn:dslforum-org:service:Hosts:1",
        control_url="/upnp/control/hosts",
        action="X_AVM-DE_WakeOnLANByMACAddress",
        arguments={"NewMACAddress": clean_mac}
    )
    if "error" in res:
        return res
    return {
        "success": True,
        "message": f"Wake-on-LAN packet successfully sent to {clean_mac}."
    }

@mcp.tool()
def get_mesh_topology() -> dict:
    """Retrieve full structured Mesh Topology (Repeaters, Access Points, Powerline, and connected client paths)."""
    res = _soap_call(
        service_type="urn:dslforum-org:service:Hosts:1",
        control_url="/upnp/control/hosts",
        action="X_AVM-DE_GetMeshListPath"
    )
    if "error" in res:
        return res

    path = res.get("NewX_AVM-DE_MeshListPath", "")
    if not path:
        return {"error": "No MeshListPath returned by FRITZ!Box."}

    opener = _build_opener()
    url = f"{_get_base_url()}{path}"
    try:
        with opener.open(url, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            nodes = data.get("nodes", [])
            summary = []
            for n in nodes:
                summary.append({
                    "device_name": n.get("device_name", ""),
                    "model": n.get("model", ""),
                    "manufacturer": n.get("manufacturer", ""),
                    "interfaces_count": len(n.get("node_interfaces", [])),
                    "links_count": len(n.get("node_links", []))
                })
            return {
                "schema_version": data.get("schema_version", ""),
                "mesh_nodes_count": len(nodes),
                "nodes_summary": summary,
                "raw_topology": data
            }
    except Exception as e:
        return {"error": f"Failed to fetch mesh JSON: {str(e)}"}

# ─── 4. Wi-Fi Management (2.4GHz, 5GHz & Guest Wi-Fi) ───────────────────────

@mcp.tool()
def get_wifi_status(band: str = "all") -> dict:
    """Inspect Wi-Fi configuration and active clients on 2.4 GHz, 5 GHz, or Guest network.
    
    Args:
        band: '2.4ghz', '5ghz', 'guest', or 'all' (default: 'all').
    """
    mapping = {
        "2.4ghz": ("urn:dslforum-org:service:WLANConfiguration:1", "/upnp/control/wlanconfig1", "2.4 GHz"),
        "5ghz": ("urn:dslforum-org:service:WLANConfiguration:2", "/upnp/control/wlanconfig2", "5 GHz"),
        "guest": ("urn:dslforum-org:service:WLANConfiguration:3", "/upnp/control/wlanconfig3", "Gast-WLAN"),
    }

    targets = mapping.items() if band == "all" else [(band, mapping.get(band))]
    results = {}

    for key, (svc, ctl, label) in targets:
        info = _soap_call(service_type=svc, control_url=ctl, action="GetInfo")
        assoc = _soap_call(service_type=svc, control_url=ctl, action="GetTotalAssociations")
        if "error" not in info:
            results[key] = {
                "label": label,
                "enabled": info.get("NewEnable") == "1",
                "status": info.get("NewStatus", ""),
                "ssid": info.get("NewSSID", ""),
                "channel": info.get("NewChannel", ""),
                "beacon_type": info.get("NewBeaconType", ""),
                "connected_devices": int(assoc.get("NewTotalAssociations", 0)) if "error" not in assoc else "N/A"
            }
        else:
            results[key] = {"error": info}

    return results

@mcp.tool()
def set_guest_wifi(enabled: bool) -> dict:
    """Enable or disable the Guest Wi-Fi (Gastnetz).
    
    Args:
        enabled: True to turn guest Wi-Fi on, False to turn it off.
    """
    val = "1" if enabled else "0"
    res = _soap_call(
        service_type="urn:dslforum-org:service:WLANConfiguration:3",
        control_url="/upnp/control/wlanconfig3",
        action="SetEnable",
        arguments={"NewEnable": val}
    )
    if "error" in res:
        return res
    return {
        "success": True,
        "message": f"Guest Wi-Fi successfully {'enabled' if enabled else 'disabled'}."
    }

# ─── 5. Phone / Call List ────────────────────────────────────────────────────

@mcp.tool()
def get_call_list(max_entries: int = 25) -> dict:
    """Retrieve the recent telephony call history (missed, incoming, and outgoing calls).
    
    Args:
        max_entries: Maximum number of calls to retrieve (default: 25).
    """
    res = _soap_call(
        service_type="urn:dslforum-org:service:X_AVM-DE_OnTel:1",
        control_url="/upnp/control/x_contact",
        action="GetCallList"
    )
    if "error" in res:
        return res

    call_url = res.get("NewCallListURL", "")
    if not call_url:
        return {"error": "No CallListURL returned."}

    opener = _build_opener()
    try:
        with opener.open(call_url, timeout=8) as r:
            xml_data = r.read().decode("utf-8")
            root = ET.fromstring(xml_data)
            calls = []
            type_names = {"1": "Eingehend", "2": "Verpasst", "3": "Ausgehend"}
            for c in root.findall("Call")[:max_entries]:
                raw_type = c.findtext("Type", "")
                calls.append({
                    "type": type_names.get(raw_type, raw_type),
                    "date": c.findtext("Date", ""),
                    "caller_number": c.findtext("Caller", ""),
                    "caller_name": c.findtext("Name", ""),
                    "called_number": c.findtext("Called", ""),
                    "duration_minutes": c.findtext("Duration", "")
                })
            return {
                "total_calls": len(calls),
                "calls": calls
            }
    except Exception as e:
        return {"error": f"Failed to download or parse call list XML: {str(e)}"}

# ─── 6. Smart Home (DECT) ───────────────────────────────────────────────────

@mcp.tool()
def get_smarthome_devices() -> dict:
    """Retrieve Smart Home devices (DECT plugs, radiator thermostats, switches, temperature sensors)."""
    res = _soap_call(
        service_type="urn:dslforum-org:service:X_AVM-DE_Homeauto:1",
        control_url="/upnp/control/x_homeauto",
        action="GetGenericDeviceInfos",
        arguments={"NewIndex": "0"}
    )
    if "error" in res:
        return {
            "devices_count": 0,
            "devices": [],
            "note": "No DECT Smart Home devices registered or service returned: " + str(res.get("error", ""))
        }
    return res

if __name__ == "__main__":
    mcp.run(transport="stdio")
