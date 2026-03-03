#!/usr/bin/env python3
"""
Qwen 3.5 Multi-Model Tentacles
Leverage different Qwen 3.5 model sizes for specialized autonomous tasks.

Each tentacle is a specialized sub-agent using the optimal model size for its task:
  - flagship (397B-A17B): Complex reasoning, architecture
  - large (122B-A10B): Code review, detailed analysis
  - medium (35B-A3B): Code completion, translation
  - standard (27B): General purpose, content
  - efficient (9B): Fast inference, classification
  - compact (4B): Edge tasks, filtering
  - tiny (0.8B): On-device, keyword extraction

Usage:
    python tentacles.py code-review <file_or_diff>
    python tentacles.py architect <description>
    python tentacles.py translate <text> --lang <zu|xh|af|st|tn>
    python tentacles.py vision <image_path> <prompt>
    python tentacles.py research <topic>
    python tentacles.py classify <text> --categories <cat1,cat2,...>
    python tentacles.py summarize <file_or_text>
    python tentacles.py auto <task_description>
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[3]
PAM_PATH = REPO_ROOT / "plugins" / "persistent-agent-memory"
MEMORY_SCRIPT = PAM_PATH / "scripts" / "write_agent_memory.py"

# Model registry - maps tentacle types to optimal Qwen 3.5 models
MODELS = {
    "flagship": {
        "id": "Qwen/Qwen3.5-397B-A17B",
        "hf_id": "Qwen/Qwen3.5-397B-A17B",
        "active_params": "17B",
        "total_params": "397B",
    },
    "large": {
        "id": "Qwen/Qwen3.5-122B-A10B",
        "hf_id": "Qwen/Qwen3.5-122B-A10B",
        "active_params": "10B",
        "total_params": "122B",
    },
    "medium": {
        "id": "Qwen/Qwen3.5-35B-A3B",
        "hf_id": "Qwen/Qwen3.5-35B-A3B",
        "active_params": "3B",
        "total_params": "35B",
    },
    "standard": {
        "id": "Qwen/Qwen3.5-27B",
        "hf_id": "Qwen/Qwen3.5-27B",
        "active_params": "27B",
        "total_params": "27B",
    },
    "efficient": {
        "id": "Qwen/Qwen3.5-9B",
        "hf_id": "Qwen/Qwen3.5-9B",
        "active_params": "9B",
        "total_params": "9B",
    },
    "compact": {
        "id": "Qwen/Qwen3.5-4B",
        "hf_id": "Qwen/Qwen3.5-4B",
        "active_params": "4B",
        "total_params": "4B",
    },
    "tiny": {
        "id": "Qwen/Qwen3.5-0.8B",
        "hf_id": "Qwen/Qwen3.5-0.8B",
        "active_params": "0.8B",
        "total_params": "0.8B",
    },
}

# Tentacle-to-model mapping: each tentacle uses the optimal model tier
TENTACLE_MODEL_MAP = {
    "code-review": "large",
    "architect": "flagship",
    "translate": "medium",
    "vision": "standard",
    "research": "flagship",
    "classify": "efficient",
    "summarize": "standard",
    "auto": "large",
}

# SA language codes for translation tentacle
SA_LANGUAGES = {
    "en": "English",
    "zu": "isiZulu",
    "xh": "isiXhosa",
    "af": "Afrikaans",
    "st": "Sesotho",
    "tn": "Setswana",
    "so": "Somali",
    "nso": "Sepedi",
    "ts": "Xitsonga",
    "ve": "Tshivenda",
    "nr": "isiNdebele",
}


def log_memory(entry: str):
    """Log tentacle activity to persistent memory."""
    try:
        subprocess.run(
            [
                sys.executable,
                str(MEMORY_SCRIPT),
                "--agent-id", "qwen-tentacle",
                "--entry", entry,
            ],
            cwd=str(PAM_PATH),
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass


def get_model_for_tentacle(tentacle: str) -> dict:
    """Get the optimal Qwen 3.5 model config for a tentacle type."""
    tier = TENTACLE_MODEL_MAP.get(tentacle, "standard")
    return MODELS[tier]


def build_inference_config(tentacle: str, prompt: str, **kwargs) -> dict:
    """Build an inference configuration for a tentacle task.

    Returns a config dict that can be used with any Qwen-compatible
    inference backend (vLLM, TGI, Ollama, HuggingFace Inference API, etc.)
    """
    model = get_model_for_tentacle(tentacle)

    config = {
        "model": model["hf_id"],
        "model_tier": TENTACLE_MODEL_MAP.get(tentacle, "standard"),
        "active_params": model["active_params"],
        "total_params": model["total_params"],
        "tentacle": tentacle,
        "prompt": prompt,
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
        },
    }

    # Tentacle-specific parameter tuning
    if tentacle == "code-review":
        config["parameters"]["temperature"] = 0.3
        config["parameters"]["max_tokens"] = 8192
    elif tentacle == "architect":
        config["parameters"]["temperature"] = 0.5
        config["parameters"]["max_tokens"] = 16384
    elif tentacle == "translate":
        config["parameters"]["temperature"] = 0.2
        config["parameters"]["max_tokens"] = 4096
        config["target_language"] = kwargs.get("lang", "zu")
    elif tentacle == "classify":
        config["parameters"]["temperature"] = 0.1
        config["parameters"]["max_tokens"] = 256
    elif tentacle == "research":
        config["parameters"]["temperature"] = 0.6
        config["parameters"]["max_tokens"] = 16384
    elif tentacle == "vision":
        config["multimodal"] = True
        config["image_path"] = kwargs.get("image_path", "")

    return config


def code_review(target: str):
    """Review code changes using the large Qwen 3.5 model."""
    target_path = Path(target)
    if target_path.exists():
        content = target_path.read_text()
        prompt = f"Review the following code for bugs, security issues, performance, and SA-specific considerations (ZAR currency, VAT 15%, multi-language support):\n\n```\n{content}\n```"
    else:
        # Treat as git diff reference
        prompt = f"Review the following diff for bugs, security issues, and best practices:\n\n{target}"

    config = build_inference_config("code-review", prompt)
    log_memory(f"Code review tentacle activated for: {target[:80]}")

    print(json.dumps(config, indent=2))
    print(f"\nTentacle: code-review")
    print(f"Model: {config['model']} ({config['active_params']} active)")
    print(f"Ready for inference via vLLM, TGI, Ollama, or HF Inference API")
    return config


def architect(description: str):
    """Design system architecture using the flagship model."""
    prompt = f"""Design a system architecture for the iHhashi food delivery platform (South Africa).

Requirements: {description}

Context:
- Tech stack: FastAPI + MongoDB (backend), React + Tailwind (frontend)
- Payment providers: Paystack, Yoco
- Auth: Supabase phone OTP
- Languages: English, Zulu, Xhosa, Afrikaans, Sotho, Tswana
- Delivery types: Car, Motorcycle, Scooter, Bicycle, On-foot, Wheelchair, Running, Rollerblade

Provide: architecture diagram (ASCII), component breakdown, data flow, scaling strategy."""

    config = build_inference_config("architect", prompt)
    log_memory(f"Architect tentacle activated: {description[:80]}")

    print(json.dumps(config, indent=2))
    print(f"\nTentacle: architect")
    print(f"Model: {config['model']} (flagship, {config['active_params']} active)")
    return config


def translate(text: str, lang: str = "zu"):
    """Translate content to South African languages."""
    lang_name = SA_LANGUAGES.get(lang, lang)
    prompt = f"Translate the following text to {lang_name} ({lang}). Maintain a friendly, casual tone suitable for a food delivery app in South Africa:\n\n{text}"

    config = build_inference_config("translate", prompt, lang=lang)
    log_memory(f"Translate tentacle: {lang_name} ({lang})")

    print(json.dumps(config, indent=2))
    print(f"\nTentacle: translate")
    print(f"Model: {config['model']} ({config['active_params']} active)")
    print(f"Target: {lang_name} ({lang})")
    return config


def vision(image_path: str, prompt: str = "Describe this image"):
    """Analyze images using Qwen 3.5 multimodal capabilities."""
    config = build_inference_config("vision", prompt, image_path=image_path)
    log_memory(f"Vision tentacle activated for: {image_path}")

    print(json.dumps(config, indent=2))
    print(f"\nTentacle: vision (multimodal)")
    print(f"Model: {config['model']} ({config['active_params']} active)")
    print(f"Image: {image_path}")
    return config


def research(topic: str):
    """Deep research using the flagship model."""
    prompt = f"""Conduct deep research on the following topic for the iHhashi food delivery platform (South Africa):

Topic: {topic}

Provide:
1. Current state analysis
2. Key findings and data points
3. Competitive landscape (Uber Eats SA, Mr D Food, OrderIn)
4. Recommendations for iHhashi
5. Implementation priorities"""

    config = build_inference_config("research", prompt)
    log_memory(f"Research tentacle activated: {topic[:80]}")

    print(json.dumps(config, indent=2))
    print(f"\nTentacle: research")
    print(f"Model: {config['model']} (flagship, {config['active_params']} active)")
    return config


def classify(text: str, categories: str = ""):
    """Fast classification using the efficient model."""
    cats = categories if categories else "bug,feature,question,documentation,performance,security"
    prompt = f"Classify the following into one of these categories [{cats}]:\n\n{text}"

    config = build_inference_config("classify", prompt)
    log_memory(f"Classify tentacle activated")

    print(json.dumps(config, indent=2))
    print(f"\nTentacle: classify")
    print(f"Model: {config['model']} ({config['active_params']} active, fast)")
    return config


def summarize(target: str):
    """Summarize documents or text."""
    target_path = Path(target)
    if target_path.exists():
        content = target_path.read_text()
        prompt = f"Summarize the following document concisely:\n\n{content}"
    else:
        prompt = f"Summarize the following:\n\n{target}"

    config = build_inference_config("summarize", prompt)
    log_memory(f"Summarize tentacle activated")

    print(json.dumps(config, indent=2))
    print(f"\nTentacle: summarize")
    print(f"Model: {config['model']} ({config['active_params']} active)")
    return config


def auto_select(task_description: str):
    """Automatically select the best tentacle and model for a task."""
    keywords_map = {
        "code-review": ["review", "bug", "lint", "quality", "security", "audit"],
        "architect": ["design", "architecture", "system", "scale", "infrastructure"],
        "translate": ["translate", "language", "zulu", "xhosa", "afrikaans", "i18n"],
        "vision": ["image", "screenshot", "photo", "visual", "ui", "mockup"],
        "research": ["research", "analyze", "compare", "market", "competitor"],
        "classify": ["classify", "categorize", "sort", "label", "tag"],
        "summarize": ["summarize", "summary", "brief", "tldr", "overview"],
    }

    task_lower = task_description.lower()
    best_tentacle = "auto"
    best_score = 0

    for tentacle, keywords in keywords_map.items():
        score = sum(1 for kw in keywords if kw in task_lower)
        if score > best_score:
            best_score = score
            best_tentacle = tentacle

    if best_tentacle == "auto":
        best_tentacle = "research"  # Default to research for ambiguous tasks

    print(f"Auto-selected tentacle: {best_tentacle} (confidence: {best_score} keyword matches)")
    model = get_model_for_tentacle(best_tentacle)
    print(f"Model: {model['hf_id']} ({model['active_params']} active)")
    log_memory(f"Auto-select: {best_tentacle} for task: {task_description[:80]}")

    config = build_inference_config(best_tentacle, task_description)
    print(json.dumps(config, indent=2))
    return config


def list_tentacles():
    """List all available tentacles and their models."""
    print("Available Qwen 3.5 Tentacles:")
    print("=" * 70)
    for tentacle, tier in TENTACLE_MODEL_MAP.items():
        model = MODELS[tier]
        print(f"  {tentacle:15s} -> {tier:10s} ({model['hf_id']}, {model['active_params']} active)")
    print()
    print("SA Languages for translate tentacle:")
    for code, name in SA_LANGUAGES.items():
        print(f"  {code:5s} {name}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        list_tentacles()
        sys.exit(0)

    command = sys.argv[1]

    if command == "code-review":
        code_review(sys.argv[2] if len(sys.argv) > 2 else "")
    elif command == "architect":
        architect(" ".join(sys.argv[2:]))
    elif command == "translate":
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        lang = "zu"
        if "--lang" in sys.argv:
            lang_idx = sys.argv.index("--lang") + 1
            if lang_idx < len(sys.argv):
                lang = sys.argv[lang_idx]
        translate(text, lang)
    elif command == "vision":
        image = sys.argv[2] if len(sys.argv) > 2 else ""
        prompt = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "Describe this image"
        vision(image, prompt)
    elif command == "research":
        research(" ".join(sys.argv[2:]))
    elif command == "classify":
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        categories = ""
        if "--categories" in sys.argv:
            cat_idx = sys.argv.index("--categories") + 1
            if cat_idx < len(sys.argv):
                categories = sys.argv[cat_idx]
        classify(text, categories)
    elif command == "summarize":
        summarize(sys.argv[2] if len(sys.argv) > 2 else "")
    elif command == "auto":
        auto_select(" ".join(sys.argv[2:]))
    elif command == "list":
        list_tentacles()
    else:
        print(f"Unknown tentacle: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
