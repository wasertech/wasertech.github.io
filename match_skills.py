#!/usr/bin/env python3
"""
match_skills.py — Moteur de matching offre → preuves

Analyse une offre d'emploi (offre.md) et score les preuves du réservoir
(data/evidence/evidence.toml) pour produire un "brief" JSON utilisé par
generate_pdf.py (CV sur mesure) et gen_letters.py (lettre sur mesure).

Usage:
    python match_skills.py contacts/<entreprise>/offre.md [--top 8] [--json]

Sortie (par défaut): résumé lisible dans le terminal.
Avec --json: brief JSON complet (consommé par generate_pdf.py / gen_letters.py).
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # Python < 3.11

PROJECT_ROOT = Path(__file__).resolve().parent
EVIDENCE_PATH = PROJECT_ROOT / "data" / "evidence" / "evidence.toml"

# ──────────────────────────────────────────────────────────────
# Extraction de mots-clés depuis l'offre
# ──────────────────────────────────────────────────────────────

# Paires (mot-clé normalisé, synonymes/tags correspondants)
# Le matching est fait sur les `tags` des preuves, pas sur le texte libre.
SYNONYM_MAP = {
    # GPU / inference
    "gpu": ["gpu", "cuda", "nvidia", "multi-gpu"],
    "cuda": ["cuda", "kernels", "gpu"],
    "inference": ["inference", "serving", "llm", "optimization"],
    "llm": ["llm", "transformers", "huggingface", "rag", "prompt-engineering"],
    "llms": ["llm", "transformers", "huggingface"],
    "large language model": ["llm", "transformers", "huggingface"],
    "large language models": ["llm", "transformers", "huggingface"],
    "vllm": ["inference", "serving", "llm"],
    "llama.cpp": ["inference", "llm", "local"],
    "llama": ["inference", "llm"],
    "quantization": ["quantization", "awq", "gptq", "kernels"],
    "quantisation": ["quantization", "awq", "gptq", "kernels"],
    "awq": ["quantization", "awq"],
    "gptq": ["quantization", "gptq"],
    "gguf": ["quantization", "inference"],
    "speculative decoding": ["inference", "optimization", "multi-gpu"],
    "pytorch": ["pytorch", "transformers", "kernels", "sft"],
    "torch": ["pytorch", "transformers"],
    "kernels": ["kernels", "cuda", "quantization"],
    "kernel": ["kernels", "cuda", "quantization"],
    "c++": ["c++", "cuda", "kernels"],
    "cpp": ["c++", "cuda", "kernels"],
    "nvidia": ["gpu", "cuda", "nvidia"],
    "tensorrt": ["inference", "optimization", "gpu"],
    "serving": ["serving", "inference", "deployment"],
    "model serving": ["serving", "inference"],
    "latency": ["latency", "optimization", "real-time"],
    "latency optimization": ["latency", "optimization", "real-time"],
    "performance": ["performance", "optimization", "linux"],
    "optimization": ["optimization", "performance", "inference"],
    "optimisation": ["optimization", "performance"],
    # LLM / agents
    "agent": ["multi-agent", "ai-agent", "orchestration", "mcp", "tools"],
    "agents": ["multi-agent", "ai-agent", "orchestration", "mcp", "tools"],
    "agentic": ["multi-agent", "ai-agent", "orchestration"],
    "multi-agent": ["multi-agent", "ai-agent", "orchestration"],
    "orchestration": ["multi-agent", "orchestration", "mcp"],
    "mcp": ["mcp", "tools", "multi-agent"],
    "tool use": ["mcp", "tools", "multi-agent"],
    "tools": ["mcp", "tools", "multi-agent"],
    "rag": ["rag", "retrieval", "embedding", "vector-database"],
    "retrieval": ["rag", "retrieval", "embedding"],
    "retrieval-augmented": ["rag", "retrieval"],
    "retrieval-augmented generation": ["rag", "retrieval"],
    "embedding": ["embedding", "rag", "vector-database"],
    "embeddings": ["embedding", "rag", "vector-database"],
    "vector database": ["vector-database", "embedding", "rag"],
    "vector databases": ["vector-database", "embedding", "rag"],
    "vector": ["vector-database", "embedding"],
    "prompt": ["prompt-engineering", "llm"],
    "prompts": ["prompt-engineering", "llm"],
    "prompt engineering": ["prompt-engineering", "llm"],
    "prompt injection": ["prompt-engineering", "llm", "security"],
    "fine-tuning": ["sft", "fine-tuning", "training"],
    "finetuning": ["sft", "fine-tuning", "training"],
    "fine tuning": ["sft", "fine-tuning", "training"],
    "fine-tune": ["sft", "fine-tuning", "training"],
    "sft": ["sft", "fine-tuning", "training"],
    "rlhf": ["sft", "fine-tuning", "training"],
    "dpo": ["sft", "fine-tuning", "training"],
    "training": ["training", "sft", "fine-tuning", "model-training"],
    "model training": ["training", "model-training", "sft"],
    "hugging face": ["huggingface", "transformers", "datasets"],
    "huggingface": ["huggingface", "transformers", "datasets"],
    "transformers": ["transformers", "huggingface", "pytorch"],
    "tokenizers": ["tokenizers", "huggingface"],
    "nlp": ["nlp", "speech", "translation", "llm"],
    "natural language": ["nlp", "llm", "translation"],
    "language model": ["llm", "transformers"],
    "language models": ["llm", "transformers"],
    "foundation model": ["llm", "transformers", "training"],
    "foundation models": ["llm", "transformers", "training"],
    "genai": ["llm", "rag", "prompt-engineering"],
    "generative ai": ["llm", "rag", "prompt-engineering", "tts"],
    "generative": ["llm", "rag", "tts"],
    "ai": ["llm", "ai-agent", "ml", "nlp", "speech"],
    "artificial intelligence": ["llm", "ai-agent", "ml", "nlp"],
    "machine learning": ["ml", "sft", "training", "data-pipeline"],
    "ml": ["ml", "sft", "training", "data-pipeline"],
    "deep learning": ["ml", "pytorch", "training", "sft"],
    "evaluation": ["evaluation", "sft", "llm"],
    "evaluations": ["evaluation", "sft", "llm"],
    "llm evaluation": ["evaluation", "llm", "sft"],
    "observability": ["monitoring", "devops", "production"],
    "monitoring": ["monitoring", "devops", "production"],
    # Speech
    "speech": ["speech", "asr", "tts", "audio", "whisper"],
    "voice": ["speech", "tts", "voice-cloning", "audio"],
    "asr": ["asr", "speech", "stt"],
    "stt": ["stt", "speech", "asr"],
    "speech recognition": ["asr", "speech", "stt"],
    "speech-to-text": ["asr", "speech", "stt", "whisper"],
    "text-to-speech": ["tts", "speech", "voice-cloning"],
    "tts": ["tts", "speech", "voice-cloning"],
    "whisper": ["whisper", "speech", "asr"],
    "transcription": ["asr", "speech", "stt", "whisper"],
    "audio": ["audio", "speech", "tts"],
    "voice cloning": ["voice-cloning", "tts", "speech"],
    "real-time": ["real-time", "websocket", "latency", "speech"],
    "realtime": ["real-time", "websocket", "latency"],
    "telephony": ["voice", "telephony", "real-time", "speech"],
    "conversational": ["multi-agent", "llm", "voice", "nlp"],
    "dialogue": ["multi-agent", "llm", "nlp"],
    # Data
    "data": ["data-pipeline", "analytics", "python", "pandas"],
    "data engineering": ["data-pipeline", "analytics", "python"],
    "data engineer": ["data-pipeline", "analytics", "python"],
    "data pipeline": ["data-pipeline", "analytics"],
    "data pipelines": ["data-pipeline", "analytics"],
    "pipelines": ["data-pipeline", "sft", "automation"],
    "pipeline": ["data-pipeline", "sft", "automation"],
    "analytics": ["analytics", "data-pipeline", "predictive-models"],
    "analytic": ["analytics", "data-pipeline"],
    "predictive": ["predictive-models", "ml", "training"],
    "pandas": ["pandas", "data-pipeline", "python"],
    "numpy": ["python", "data-pipeline"],
    "jupyter": ["python", "data-pipeline"],
    "sql": ["python", "data-pipeline"],
    "sqlite": ["python", "data-pipeline"],
    "databases": ["python", "data-pipeline", "vector-database"],
    "database": ["python", "data-pipeline", "vector-database"],
    "etl": ["data-pipeline", "analytics"],
    "ingestion": ["data-pipeline", "analytics"],
    "datasets": ["datasets", "sft", "huggingface"],
    "dataset": ["datasets", "sft", "huggingface"],
    "data quality": ["datasets", "sft", "data-pipeline"],
    "time series": ["data-pipeline", "analytics", "trading"],
    "trading": ["trading", "quantitative", "ml"],
    "quantitative": ["trading", "quantitative", "ml"],
    "finance": ["trading", "quantitative"],
    "financial": ["trading", "quantitative"],
    "backtesting": ["trading", "backtesting", "ml"],
    "backtest": ["trading", "backtesting"],
    "blockchain": ["blockchain", "solana", "smart-contracts"],
    "solana": ["blockchain", "solana"],
    "smart contract": ["blockchain", "smart-contracts"],
    "smart contracts": ["blockchain", "smart-contracts"],
    "web3": ["blockchain", "solana"],
    # DevOps
    "docker": ["docker", "containerization", "gpu"],
    "kubernetes": ["docker", "devops", "deployment", "infrastructure"],
    "k8s": ["docker", "devops", "deployment"],
    "devops": ["devops", "docker", "infrastructure", "cicd"],
    "ci/cd": ["cicd", "ci", "cd", "automation"],
    "cicd": ["cicd", "ci", "cd"],
    "ci": ["cicd", "ci", "automation"],
    "cd": ["cicd", "cd", "deployment"],
    "deployment": ["deployment", "devops", "docker", "production"],
    "deploy": ["deployment", "devops"],
    "linux": ["linux", "systemd", "devops"],
    "unix": ["linux", "devops"],
    "systemd": ["systemd", "linux", "devops"],
    "git": ["git", "cicd"],
    "github": ["git", "cicd", "github", "open-source"],
    "gitlab": ["git", "cicd", "gitlab"],
    "cloud": ["cloud", "devops", "infrastructure", "docker"],
    "aws": ["cloud", "devops", "infrastructure"],
    "gcp": ["cloud", "devops", "infrastructure"],
    "azure": ["cloud", "devops", "infrastructure"],
    "infrastructure": ["infrastructure", "devops", "docker"],
    "platform": ["infrastructure", "devops", "platform", "production"],
    "platforms": ["infrastructure", "devops", "platform"],
    "mlops": ["mlops", "devops", "sft", "training", "deployment"],
    "ml platform": ["mlops", "infrastructure", "platform"],
    "api": ["rest", "fastapi", "django", "api"],
    "apis": ["rest", "fastapi", "django", "api"],
    "rest": ["rest", "fastapi", "django", "api"],
    "fastapi": ["fastapi", "rest", "python"],
    "django": ["django", "rest", "python"],
    "websocket": ["websocket", "real-time"],
    "sse": ["real-time", "websocket"],
    "microservices": ["docker", "devops", "infrastructure"],
    "microservice": ["docker", "devops", "infrastructure"],
    "secrets": ["devops", "security", "infrastructure"],
    "secrets management": ["devops", "security"],
    "access control": ["security", "api"],
    "authentication": ["security", "api"],
    "authorization": ["security", "api"],
    "security": ["security", "devops"],
    "logging": ["devops", "monitoring", "production"],
    "audit": ["devops", "monitoring", "security"],
    "audit logging": ["devops", "monitoring", "security"],
    "cost management": ["optimization", "performance", "trading"],
    "finops": ["optimization", "performance", "cloud"],
    "lifecycle": ["devops", "deployment", "mlops"],
    "lifecycle management": ["devops", "deployment", "mlops"],
    "routing": ["inference", "serving", "llm"],
    "model routing": ["inference", "serving", "llm"],
    "model lifecycle": ["mlops", "deployment", "training"],
    "retraining": ["training", "sft", "mlops"],
    "model monitoring": ["monitoring", "mlops", "production"],
    # Web / fullstack
    "python": ["python", "django", "fastapi", "ml"],
    "javascript": ["javascript", "fullstack", "web"],
    "typescript": ["javascript", "fullstack", "web"],
    "node": ["javascript", "fullstack"],
    "node.js": ["javascript", "fullstack"],
    "html": ["html", "fullstack", "web"],
    "css": ["css", "fullstack", "web"],
    "frontend": ["fullstack", "web", "html", "css"],
    "front-end": ["fullstack", "web", "html", "css"],
    "backend": ["fullstack", "rest", "fastapi", "django"],
    "back-end": ["fullstack", "rest", "fastapi", "django"],
    "full-stack": ["fullstack", "web", "rest"],
    "fullstack": ["fullstack", "web", "rest"],
    "web": ["web", "fullstack", "rest"],
    "web application": ["fullstack", "web", "rest"],
    "web applications": ["fullstack", "web", "rest"],
    "responsive": ["fullstack", "web", "html", "css"],
    "ui": ["fullstack", "web", "html", "css"],
    "ux": ["fullstack", "web"],
    "translation": ["translation", "nlp", "i18n"],
    "i18n": ["i18n", "translation"],
    "localization": ["i18n", "translation"],
    "multilingual": ["multilingual", "translation", "speech"],
    "multilingue": ["multilingual", "translation"],
    "languages": ["multilingual", "french", "english"],
    "french": ["french", "multilingual"],
    "english": ["english", "multilingual"],
    "spanish": ["spanish", "multilingual"],
    "german": ["german", "multilingual"],
    "allemand": ["german", "multilingual"],
    "français": ["french", "multilingual"],
    "anglais": ["english", "multilingual"],
    # Soft skills / management
    "leadership": ["leadership", "entrepreneurship", "management"],
    "lead": ["leadership", "management", "stakeholders"],
    "team": ["leadership", "management", "stakeholders"],
    "management": ["leadership", "management", "stakeholders"],
    "stakeholder": ["stakeholders", "communication", "leadership"],
    "stakeholders": ["stakeholders", "communication", "leadership"],
    "communication": ["communication", "stakeholders", "presentation"],
    "presentation": ["communication", "presentation", "stakeholders"],
    "mentoring": ["leadership", "communication", "stakeholders"],
    "mentorship": ["leadership", "communication"],
    "supervision": ["leadership", "management", "stakeholders"],
    "consultant": ["leadership", "stakeholders", "communication"],
    "consultants": ["leadership", "stakeholders"],
    "c-suite": ["stakeholders", "leadership", "communication"],
    "executive": ["stakeholders", "leadership"],
    "product": ["product", "prototyping", "rnd"],
    "product requirements": ["product", "stakeholders", "rnd"],
    "prototyping": ["prototyping", "rnd", "rapid"],
    "prototype": ["prototyping", "rnd"],
    "r&d": ["rnd", "prototyping", "research"],
    "research": ["rnd", "research", "evaluation"],
    "innovation": ["rnd", "prototyping", "entrepreneurship"],
    "entrepreneur": ["entrepreneurship", "founder"],
    "founder": ["entrepreneurship", "founder"],
    "startup": ["entrepreneurship", "founder", "rnd"],
    "scale-up": ["entrepreneurship", "rnd", "product"],
    "autonomy": ["autonomy", "entrepreneurship", "independent"],
    "autonomous": ["autonomy", "entrepreneurship"],
    "self-directed": ["autonomy", "entrepreneurship"],
    "independent": ["independent", "entrepreneurship"],
    "open source": ["open-source", "github", "community"],
    "open-source": ["open-source", "github", "community"],
    "open source contributions": ["open-source", "github", "community"],
    "community": ["community", "open-source"],
    "documentation": ["open-source", "communication"],
    "docling": ["document", "nlp", "python"],
    "document": ["document", "nlp", "rag"],
    "documents": ["document", "nlp", "rag"],
    "pdf": ["document", "python"],
    "scraping": ["python", "automation", "web"],
    "web scraping": ["python", "automation", "web"],
    "search": ["rag", "retrieval", "python"],
    "search engine": ["rag", "retrieval"],
    "crawling": ["python", "automation"],
    "automation": ["automation", "mcp", "tools", "cicd"],
    "automated": ["automation", "mcp", "tools"],
    "workflow": ["automation", "data-pipeline", "mcp"],
    "workflows": ["automation", "data-pipeline", "mcp"],
    "testing": ["cicd", "python", "automation"],
    "test": ["cicd", "python"],
    "quality": ["cicd", "datasets", "sft"],
    "agile": ["product", "rnd", "prototyping"],
    "scrum": ["product", "rnd"],
    "jira": ["product", "automation"],
    "linux administration": ["linux", "systemd", "devops"],
    "system administration": ["linux", "systemd", "devops"],
    "bash": ["linux", "shell", "automation"],
    "shell": ["linux", "shell", "automation"],
    "scripting": ["python", "bash", "automation"],
}


def extract_keywords(offer_text: str) -> dict[str, list[str]]:
    """Extrait les mots-clés de l'offre et les mappe vers des tags de preuves.

    Retourne {tag: [mots_cles_source]} — chaque tag est un tag de preuve
    qui correspond à au moins un mot-clé de l'offre.
    """
    text = offer_text.lower()
    tag_map: dict[str, list[str]] = {}

    for keyword, tags in SYNONYM_MAP.items():
        # Recherche avec mots entiers (pas de sous-chaîne)
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text):
            for tag in tags:
                tag_map.setdefault(tag, []).append(keyword)

    return tag_map


def load_evidence() -> list[dict]:
    """Charge le réservoir de preuves."""
    with open(EVIDENCE_PATH, "rb") as f:
        data = tomllib.load(f)
    return data.get("evidence", [])


def score_evidence(evidence: list[dict], tag_map: dict[str, list[str]]) -> list[dict]:
    """Score chaque preuve selon le nombre de tags qui matchent l'offre."""
    scored = []
    for ev in evidence:
        ev_tags = set(ev.get("tags", []))
        matched_tags = ev_tags & set(tag_map.keys())
        # Score = nombre de tags matchés × poids de la preuve
        score = len(matched_tags) * ev.get("weight", 3)
        if score > 0:
            scored.append({
                **ev,
                "score": score,
                "matched_tags": sorted(matched_tags),
                "matched_keywords": sorted(set(k for t in matched_tags for k in tag_map[t])),
            })
    scored.sort(key=lambda x: (-x["score"], -x.get("weight", 0)))
    return scored


def build_brief(offer_path: Path, top_n: int = 8) -> dict:
    """Construit le brief complet pour une offre."""
    offer_text = offer_path.read_text(encoding="utf-8")
    tag_map = extract_keywords(offer_text)
    evidence = load_evidence()
    scored = score_evidence(evidence, tag_map)
    top = scored[:top_n]

    # Détecter la langue de l'offre
    fr_indicators = ["français", "français", "francophone", "suisse romande", "lausanne", "genève", "neuchâtel", "fribourg", "vaud", "valais", "vaudois", "vaudoise", "candidature", "poste", "entreprise", "expérience", "compétences", "diplôme", "formation", "langues", "allemand", "anglais", "espagnol", "italien"]
    en_indicators = ["english", "french", "german", "spanish", "italian", "switzerland", "swiss", "lausanne", "geneva", "neuchatel", "fribourg", "valais", "vaud", "candidature", "poste", "entreprise", "expérience", "compétences", "diplôme", "formation", "langues", "allemand", "anglais", "espagnol", "italien"]
    text_lower = offer_text.lower()
    fr_score = sum(1 for w in fr_indicators if w in text_lower)
    en_score = sum(1 for w in en_indicators if w in text_lower)
    # Si l'offre contient des mots typiquement français (accents, mots spécifiques)
    if re.search(r'[éèêëàâçùûüôîï]', text_lower):
        fr_score += 3
    language = "fr" if fr_score >= en_score else "en"

    return {
        "offer_path": str(offer_path),
        "language": language,
        "keywords_found": len(tag_map),
        "tag_map": {k: sorted(set(v)) for k, v in tag_map.items()},
        "evidence": top,
        "all_scored": scored,
    }


def main():
    parser = argparse.ArgumentParser(description="Match offre → preuves")
    parser.add_argument("offer", help="Chemin vers offre.md")
    parser.add_argument("--top", type=int, default=8, help="Nombre de preuves top (défaut: 8)")
    parser.add_argument("--json", action="store_true", help="Sortie JSON complète")
    args = parser.parse_args()

    offer_path = Path(args.offer)
    if not offer_path.exists():
        print(f"ERREUR: {offer_path} introuvable", file=sys.stderr)
        sys.exit(1)

    brief = build_brief(offer_path, args.top)

    if args.json:
        print(json.dumps(brief, ensure_ascii=False, indent=2))
    else:
        print(f"📄 Offre: {offer_path.name}")
        print(f"🌐 Langue détectée: {brief['language'].upper()}")
        print(f"🔑 Mots-clés trouvés: {brief['keywords_found']}")
        print(f"📊 Preuves matchées: {len(brief['all_scored'])} (top {len(brief['evidence'])})")
        print()
        for i, ev in enumerate(brief["evidence"], 1):
            print(f"  {i}. [{ev['score']:>3}] {ev['skill']} (w={ev['weight']})")
            print(f"       Tags: {', '.join(ev['matched_tags'][:6])}")
            print(f"       Metrics: {', '.join(ev['metrics'][:4])}")
            print()


if __name__ == "__main__":
    main()
