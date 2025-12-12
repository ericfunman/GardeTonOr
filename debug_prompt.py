import json
from src.services.openai_service import OpenAIService


def debug_prompts():
    service = OpenAIService(api_key="dummy")

    types_to_check = ["electricite", "gaz"]

    for c_type in types_to_check:
        print(f"\n{'='*50}")
        print(f"DEBUG PROMPT FOR: {c_type.upper()}")
        print(f"{'='*50}\n")

        # Get schema
        schema = service._get_contract_schema(c_type)
        print(f"--- SCHEMA ({c_type}) ---")
        print(json.dumps(schema, indent=2, ensure_ascii=False))
        print("\n")

        # Build prompt with dummy text
        dummy_text = "[CONTENU DU PDF SIMULÉ ICI...]"
        prompt = service._build_extraction_prompt(c_type, dummy_text, schema)

        print(f"--- FULL PROMPT ({c_type}) ---")
        print(prompt)
        print("\n")


if __name__ == "__main__":
    debug_prompts()
