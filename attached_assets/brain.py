import sys
from conversation_engine import ConversationEngine
from memory_engine import MemoryEngine  # Updated
import datetime
import os
import logging
import requests
from bs4 import BeautifulSoup
from web_crawler import extract_from_urls
# brain.py (or equivalent bootstrap)
from json_guardian import JSONGuardian
from boot_guardian import BootGuardian

def boot():
    # Sovereign self-check before anything else happens
    guardian = BootGuardian(memory_dir="memory", schema_dir="schemas")
    guardian.run_full_validation()

    # Continue normal boot if everything passed
    print("🚀 Derek boot sequence continuing...")
    # load models, services, memory embeddings, etc.

def boot():
    guardian = JSONGuardian()
    guardian.validate_all()
    print("✅ All JSON memory files validated successfully.")
    # then continue with loading memory, models, etc.

# Set up logging
logger = logging.getLogger(__name__)

# Try to import optional modules with fallbacks
try:
    from intent_engine import detect_intent
except ImportError:
    logger.warning("intent_engine not found, using basic intent detection")

    def detect_intent(text):
        return "general"


try:
    from executor import execute_task
except ImportError:
    logger.warning("executor not found, using basic task execution")

    def execute_task(text, intent, context):
        return f"I received your message: {text}"


try:
    from tts_bridge import speak_response
except ImportError:
    logger.warning("tts_bridge not found, speech output disabled")

    def speak_response(text):
        print(f"[SPEECH]: {text}")


# Create a simple learning coordinator fallback
try:
    from derek_learning_coordinator import derek_coordinator, start_derek_learning
except ImportError:
    logger.warning("derek_learning_coordinator not found, using fallback")

    class DummyCoordinator:
        def start(self):
            logger.info("Learning coordinator fallback active")

    derek_coordinator = DummyCoordinator()

    def start_derek_learning():
        derek_coordinator.start()


logger = logging.getLogger(__name__)

# ensure the project root is in Python's import path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from ai_learning_engine import learn_from_text

    logger.info("✅ ai_learning_engine imported successfully")
except Exception as e:
    logger.warning(f"⚠️ Failed to import ai_learning_engine: {e}")

    def learn_from_text(text):
        logger.info("Learning module unavailable, skipping text ingestion")


class Derek:
    def __init__(self, file_path: str = "./memory/memory_store.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        self.memory_engine = MemoryEngine(file_path=file_path)
        self.conversation_engine = ConversationEngine()
        self.avatar_engine = None
        self.learning_coordinator = derek_coordinator

        logger.info(f"Derek initialized successfully with memory file: {file_path}")

    def generate_greeting(self) -> str:
        """
        Returns a startup greeting when Derek Dashboard launches.
        Can be made dynamic later, but static is fine to unblock startup.
        """
        return "Hello, I’m Derek — ready to assist you."

    def connect_conversation_engine(self, conversation_engine):
        self.conversation_engine = conversation_engine

    def attach_avatar_engine(self, avatar_engine):
        self.avatar_engine = avatar_engine

    def get_current_mood(self):
        if self.conversation_engine and hasattr(
            self.conversation_engine, "emotional_state"
        ):
            return self.conversation_engine.emotional_state
        return {}

    def start_learning(self):
        """Activate Derek's coordinated learning systems."""
        try:
            start_derek_learning()
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to start learning systems: %s", exc)
        else:
            logger.info("Derek is now learning autonomously")
    
    def _search_web(self, query: str) -> str:
        """Performs a web search and returns a summary of the top result."""
        logger.info(f"Performing web search for: {query}")
        try:
            # Prepare the search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }

            # Get the search results page
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()

            # --- Parse links from the HTML ---
            soup = BeautifulSoup(response.text, "html.parser")
            link_tags = soup.find_all(
                "a", href=lambda href: href and href.startswith("/url?q=")
            )
            urls = [
                tag["href"].split("/url?q=")[1].split("&sa=U")[0]
                for tag in link_tags[:3]
            ]

            # Extract content from top 3 links
            article_data = extract_from_urls(urls)

            summaries = []
            for i, item in enumerate(article_data):
                title = item.get("title", "No Title")
                text = item.get("text", "")
                summary = f"{i+1}. {title}: {text[:200]}..."
                summaries.append(summary)

                # Auto-ingest what Derek reads
                learn_from_text(text)

            summary_output = "\n\n".join(summaries)

            # Save original search HTML for debugging
            with open("google_search_results.html", "w", encoding="utf-8") as file:
                file.write(response.text)

            return summary_output

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            print(f"Web search failed with error: {e}")
            return (
                "I had trouble searching the web. Please check my connection and logs."
            )

    def think(self, input_text: str):
        # Step 1: Detect Intent
        intent = detect_intent(input_text)

        # --- Smarter question detection ---
        question_keywords = [
            "who is",
            "what is",
            "what's",
            "when did",
            "where is",
            "why is",
            "how is",
            "weather in",
        ]
        is_question = any(kw in input_text.lower() for kw in question_keywords)

        if is_question:
            logger.info("Question detected, performing web search.")
            repaired_result = self._search_web(input_text)
        else:
            # Non-search tasks use local context
            memory_context = self.memory_engine.query(input_text, intent)
            raw_result = execute_task(input_text, intent, memory_context)
            repaired_result = self.run_self_repair(input_text, raw_result)

        # Step 5: Speak the Output
        speak_response(repaired_result)
        if self.avatar_engine:
            self.avatar_engine.speak(repaired_result)

        # Step 6: Save to Memory and Log
        self.memory_engine.save(
            {"input": input_text, "output": repaired_result, "intent": intent}
        )
        self.log_interaction(input_text, repaired_result)

        return {
            "intent": intent,
            "context": "Web Search" if is_question else "Memory",
            "response": repaired_result,
            "mood": self.get_current_mood(),
        }

    def run_self_repair(self, user_input, derek_output):
        """Detect canned or low-depth responses and trigger auto-improvement."""
        canned_indicators = [
            "you got it",
            "happy to help",
            "sounds good",
            "let me know",
            "here’s how",
            "you’re doing great",
            "as an ai language model",
            "i'm here to assist",
        ]

        if any(phrase in derek_output.lower() for phrase in canned_indicators):
            return (
                f"⚠️ [Self-Repair Triggered]\n"
                f"Your last response lacked depth and originality.\n\n"
                f"🧠 USER INPUT:\n{user_input.strip()}\n\n"
                f"🛠️ DEREK'S IMPROVED RESPONSE:\n"
                f"[Insert real, contextual, emotionally intelligent response here]"
            )
        return derek_output

    def log_interaction(self, user_input, derek_output):
        """Logs every conversation exchange to a markdown file."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = (
            f"## {timestamp}\n"
            f"**Input:** {user_input}\n"
            f"**Output:** {derek_output[:150]}...\n\n"
        )

        os.makedirs("logs", exist_ok=True)
        with open("logs/study_log.md", "a") as f:
            f.write(log_entry)


# -------------------------------------------------------------
# Global Derek instance (fixed)
# -------------------------------------------------------------
derek = Derek(file_path="./memory/memory_store.json")

