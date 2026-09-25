from dotenv import load_dotenv
load_dotenv()   # MUST be before any core/ imports

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions


def main():
    """Run a manual end-to-end smoke check against a supplied media source."""
    source = input("Enter YouTube URL or local file path: ").strip()
    if not source:
        raise ValueError("A YouTube URL or local file path is required.")
    language = input("Language (english/hinglish): ").strip() or "english"



    chunks = process_input(source)


    transcript = transcribe_all(chunks, language=language)
    print("\n" + "=" * 60)
    print("📝 TRANSCRIPT")
    print("=" * 60)
    print(transcript[:500] + "..." if len(transcript) > 500 else transcript)


    title = generate_title(transcript)
    summary = summarize(transcript)

    print("\n" + "=" * 60)
    print(f"📌 TITLE: {title}")
    print("=" * 60)
    print("\n📋 SUMMARY")
    print("-" * 60)
    print(summary)



    action_items = extract_action_items(transcript)
    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)

    print("\n" + "=" * 60)
    print("✅ ACTION ITEMS")
    print("=" * 60)
    print(action_items)

    print("\n" + "=" * 60)
    print("🔑 KEY DECISIONS")
    print("=" * 60)
    print(decisions)

    print("\n" + "=" * 60)
    print("❓ OPEN QUESTIONS")
    print("=" * 60)
    print(questions)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        if status_code == 429:
            print(
                "Mistral rate limit reached (HTTP 429). Wait for the limit to reset, "
                "check your Mistral account's usage and rate limits, then run this script again."
            )
        else:
            raise
