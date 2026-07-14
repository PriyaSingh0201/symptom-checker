# utils/knowledge_base.py – Dynamic medical evidence retrieval engine
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import logging
import re
from utils.medical_sources import retrieve_sources

logger = logging.getLogger(__name__)

# Optional API keys (loaded from .env — all are optional, free endpoints used by default)
WHO_API_KEY = os.environ.get("WHO_API_KEY", "").strip()
CDC_API_KEY = os.environ.get("CDC_API_KEY", "").strip()
MEDLINEPLUS_API_KEY = os.environ.get("MEDLINEPLUS_API_KEY", "").strip()
NHS_API_KEY = os.environ.get("NHS_API_KEY", "").strip()
OPENFDA_API_KEY = os.environ.get("OPENFDA_API_KEY", "").strip()

def query_medlineplus(term: str) -> list:
    """
    Queries NLM MedlinePlus Web Service for keyword search.
    Returns list of dicts with: source, title, summary, url
    """
    if not term:
        return []
    try:
        encoded_term = urllib.parse.quote(term.strip())
        # MEDLINEPLUS_API_KEY is optional — the public endpoint works without it
        url = f"https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term={encoded_term}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-Clinical-Intelligence/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        results = []
        for doc in root.findall(".//document"):
            url_val = doc.attrib.get("url", "")
            title_node = doc.find(".//content[@name='title']")
            summary_node = doc.find(".//content[@name='FullSummary']")

            title = title_node.text if title_node is not None else ""
            summary = summary_node.text if summary_node is not None else ""

            if summary:
                # Strip HTML tags
                summary = re.sub(r"<[^<]+?>", "", summary)
                # Decode HTML entities if any
                summary = summary.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
                if len(summary) > 200:
                    summary = summary[:197] + "..."

            if title and url_val:
                results.append({
                    "source": "MedlinePlus",
                    "title": title,
                    "summary": summary or f"Consumer health topic for {title}.",
                    "url": url_val
                })
                if len(results) >= 2: # Keep list short to avoid huge prompt payloads
                    break
        return results
    except Exception as e:
        logger.warning("MedlinePlus query failed: %s", e)
        return []

def query_openfda(term: str) -> list:
    """
    Queries openFDA for drug labeling details matching search term in indications_and_usage.
    Returns list of dicts with: source, title, summary, url
    """
    if not term:
        return []
    try:
        # OPENFDA_API_KEY raises the rate limit but is not required
        encoded_term = urllib.parse.quote(f'"{term.strip()}"')
        key_param = f"&api_key={OPENFDA_API_KEY}" if OPENFDA_API_KEY else ""
        url = f"https://api.fda.gov/drug/label.json?search=indications_and_usage:{encoded_term}&limit=1{key_param}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 AI-Clinical-Intelligence/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        results = []
        for result in data.get("results", []):
            openfda = result.get("openfda", {})
            brand_names = openfda.get("brand_name", [])
            generic_names = openfda.get("generic_name", [])
            indications = result.get("indications_and_usage", [""])

            brand_title = brand_names[0] if brand_names else ""
            generic_title = generic_names[0] if generic_names else ""
            title = brand_title or generic_title or "FDA Approved Drug Information"

            summary = indications[0] if indications else ""
            if summary:
                summary = re.sub(r"<[^<]+?>", "", summary)
                if len(summary) > 200:
                    summary = summary[:197] + "..."

            results.append({
                "source": "OpenFDA",
                "title": f"FDA Drug Labeling: {title}",
                "summary": summary or "Retrieved from FDA approved drug database.",
                "url": "https://open.fda.gov"
            })
        return results
    except Exception as e:
        logger.warning("openFDA query failed: %s", e)
        return []

NO_EVIDENCE_MESSAGE = "Limited medical reference data found. AI response generated using available clinical reasoning."

def retrieve_medical_evidence(primary_symptom: str, secondary_symptoms: str = "", suspected_condition: str = "") -> list:
    """
    Retrieves evidence dynamically from:
    - NLM MedlinePlus
    - openFDA
    - Curated offline WHO, CDC, and NHS resources.
    
    Combines them into a flat list of evidence reference dictionaries.
    """
    evidence = []

    # 1. Search term formulation
    search_term = suspected_condition or primary_symptom or "fever"
    
    # 2. Query Live APIs
    medline_results = query_medlineplus(search_term)
    if not medline_results and primary_symptom:
        # Retry with primary symptom if condition returned nothing
        medline_results = query_medlineplus(primary_symptom)
    evidence.extend(medline_results)

    fda_results = query_openfda(search_term)
    if not fda_results and primary_symptom:
        fda_results = query_openfda(primary_symptom)
    evidence.extend(fda_results)

    # 3. Retrieve Curated CDC, WHO, NHS references
    cond_term = suspected_condition or search_term
    offline_sources = retrieve_sources(cond_term)

    for source_name in ["WHO", "CDC", "NHS"]:
        if source_name in offline_sources:
            src_info = offline_sources[source_name]
            evidence.append({
                "source": source_name,
                "title": src_info["title"],
                "summary": src_info["summary"],
                "url": src_info["url"]
            })

    if not evidence:
        logger.info("No medical evidence retrieved for '%s'. Using clinical reasoning fallback.", search_term)
        evidence.append({
            "source": "System",
            "title": "Limited Reference Data",
            "summary": NO_EVIDENCE_MESSAGE,
            "url": ""
        })

    return evidence
