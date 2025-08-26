from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, Field, PrivateAttr
from typing import ClassVar

# LangChain core
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool




def _make_llm() -> Any:
    """Return a chat LLM based on env var LLM_PROVIDER.

    Supported providers:
      • openai  → langchain_openai.ChatOpenAI (gpt-4o-mini or similar)
      • gemini  → langchain_google_genai.ChatGoogleGenerativeAI
      • groq    → langchain_groq.ChatGroq
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        # Adjust model/temperature to keep responses fast & grounded
        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), temperature=0.2)

    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"), temperature=0.2)

    raise ValueError("Unsupported LLM_PROVIDER. Use openai | gemini | groq")


# -----------------------------
# Tool 1 — UAEKnowledgeSearchTool
# -----------------------------


class UAEKnowledgeQuery(BaseModel):
    query: str = Field(..., description="Tourist question to search in the UAE knowledge base")


@dataclass
class KnowledgeItem:
    id: str
    city: Optional[str]
    tags: List[str]
    title: str
    description: str




class UAEKnowledgeSearchTool(BaseTool):
    name: str = "uae_knowledge_search"  # Add type annotation
    description: str = (
        "Searches facts, attractions, cultural tips, and FAQs from uae_knowledge.json. "
        "Use this for *any factual* UAE question."
    )
    args_schema: type[BaseModel] = UAEKnowledgeQuery  # Add type annotation

    _knowledge_path: str = PrivateAttr()  # Define as a private attribute

    def __init__(self, knowledge_path: str):
        super().__init__()
        self._knowledge_path = knowledge_path

    def search_knowledge_base(self, knowledge: dict, query: str) -> str:
        """Search the knowledge base JSON for relevant information based on the query."""
        query = query.lower()

        # Define mappings for sections and subcategories
        mappings = {
            "cultural tips": ("cities", "cultural_tips"),
            "top attractions": ("cities", "top_attractions"),
            "general info": ("general_info", None),
            "activities": ("activities", None),
        }

        # Match query to a section and subcategory
        for key, (section, subcategory) in mappings.items():
            if key in query:
                if section in knowledge:
                    if subcategory:
                        # Search within subcategories of cities
                        results = []
                        for city, data in knowledge.get(section, {}).items():
                            if subcategory in data:
                                results.append(f"{city}: {', '.join(data[subcategory])}")
                        return "\n".join(results) if results else "No relevant information found."
                    return json.dumps(knowledge[section], indent=2)
                return f"Section '{section}' not found in the knowledge base."

        return "Query not understood. Please rephrase."

    def _run(self, query: str) -> str:
        try:
            with open(self._knowledge_path, "r", encoding="utf-8") as f:
                knowledge = json.load(f)
            results = self.search_knowledge_base(knowledge, query)
            if results:
                print("Knowledge tool")
                return "\n".join(results)
            return "No relevant information found in the knowledge base."
        except Exception as e:
            return f"Error accessing knowledge base: {e}"

    async def _arun(self, query: str) -> str:
        return self._run(query)  # Tool 2 — PrayerTimeTool


# -----------------------------


class PrayerTimeArgs(BaseModel):
    city: str = Field(..., description="UAE city name, e.g., Dubai")
    date: Optional[str] = Field(
        default=None,
        description="Date in YYYY-MM-DD. Defaults to today if omitted.",
    )


class PrayerTimeArgs(BaseModel):
    city: str = Field(..., description="UAE city name, e.g., Dubai")
    date: Optional[str] = Field(
        default=None,
        description="Date in YYYY-MM-DD. Defaults to today if omitted.",
    )

class PrayerTimeTool(BaseTool):
    name: str = "prayer_times"
    description: str = (
        "Returns prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha) for a UAE city and date. "
        "Input should be a JSON string with 'city' and optional 'date'."
    )
    is_single_input: bool = True
    args_schema: type[BaseModel] = PrayerTimeArgs

    _use_api: bool = PrivateAttr()

    def __init__(self, t=""):
        super().__init__()
        self._use_api = os.getenv("ALADHAN", "0").strip() == "1"
        self._static = {
            "dubai": {"Fajr": "04:16", "Dhuhr": "12:24", "Asr": "15:54", "Maghrib": "18:44", "Isha": "20:03"},
            "abu dhabi": {"Fajr": "04:20", "Dhuhr": "12:28", "Asr": "15:58", "Maghrib": "18:47", "Isha": "20:06"},
            "sharjah": {"Fajr": "04:17", "Dhuhr": "12:24", "Asr": "15:54", "Maghrib": "18:44", "Isha": "20:03"},
        }

    def _run(self, city: str, date: Optional[str]) -> str:
        try:
            if not city:
                return "City is required for prayer times."
            if self._use_api:
                return self._api_run(city, date)
            return self._static_run(city, date)
        except json.JSONDecodeError:
            return "Invalid input format. Provide a JSON string with 'city' and optional 'date'."

    def _static_run(self, city: str, date: Optional[str]) -> str:
        city_key = city.lower().strip()
        times = self._static.get(city_key)
        if not times:
            return (
                f"No static times for '{city}'. Enable ALADHAN=1 to call the API or use Dubai/Abu Dhabi/Sharjah."
            )
        d = date or datetime.now().strftime("%Y-%m-%d")
        return (
            f"Prayer times for {city.title()} on {d}:\n"
            f"Fajr: {times['Fajr']}\nDhuhr: {times['Dhuhr']}\nAsr: {times['Asr']}\nMaghrib: {times['Maghrib']}\nIsha: {times['Isha']}"
        )

    def _api_run(self, city: str, date: Optional[str]) -> str:
        d = date or datetime.now().strftime("%Y-%m-%d")
        method = os.getenv("PRAYER_METHOD", "2")
        url = (
            "https://api.aladhan.com/v1/timingsByCity"
            f"?city={city}&country=AE&method={method}&date={d}"
        )
        try:
            resp = requests.get(url, timeout=10, verify=False)
            resp.raise_for_status()
            data = resp.json()
            t = data["data"]["timings"]
            return (
                f"[Prayer Tool] Prayer times for {city.title()} on {d}:\n"
                f"Fajr: {t['Fajr']}\nDhuhr: {t['Dhuhr']}\nAsr: {t['Asr']}\nMaghrib: {t['Maghrib']}\nIsha: {t['Isha']}"
            )
        except Exception as e:
            return f"Failed to fetch from Aladhan: {e}"

    async def _arun(self, query: str) -> str:
        return self._run(query)


# -----------------------------
# Tool 3 — TripBudgetPlanner
# -----------------------------


class BudgetArgs(BaseModel):
    city: str = Field(..., description="City of the trip (for echo only)")
    days: int = Field(..., gt=0, description="Trip length in days")
    style: str = Field(..., description="budget | standard | luxury")




class TripBudgetPlanner(BaseTool):
    name: str = "trip_budget"  # Add type annotation
    description: str = (
        "Returns a simple AED cost estimate given city, days, and travel style: "
        "budget=150/day, standard=400/day, luxury=1000/day."
    )
    args_schema: type[BaseModel] = BudgetArgs  # Add type annotation

    RATES: ClassVar[dict[str, int]] = {"budget": 150, "standard": 400, "luxury": 1000}  # Mark as ClassVar

    def _run(self, city: str, days: int, style: str) -> str:
        s = style.lower().strip()
        if s not in self.RATES:
            return "Style must be one of: budget, standard, luxury."
        per_day = self.RATES[s]
        total = per_day * int(days)
        return (
            f"Estimated cost for {days} day(s) in {city.title()} ({s}): {total} AED "
            f"({per_day} AED/day)."
        )

    async def _arun(self, city: str, days: int, style: str) -> str:
        return self._run(city, days, style)


# -----------------------------
# Agent setup
# -----------------------------


SYSTEM_RULES = (
    "You are the UAE Smart Tourism Assistant."
    "\nRules:"
    "\n1) For factual questions about UAE, ALWAYS use the uae_knowledge_search tool."
    "\n2) For prayer times, ALWAYS use the prayer_times tool."
    "\n3) For budget estimates, ALWAYS use the trip_budget tool."
    "\n4) Only use your own reasoning (no tools) to produce TOUR RECOMMENDATIONS/ITINERARIES."
    "\n5) If information is not found in the knowledge base or tools, say so and ask the user to rephrase."
    "\n6) Keep replies concise, friendly, and helpful."
)


def build_agent(knowledge_path: str = "uae_knowledge.json"):
    llm = _make_llm()

    tools = [
        UAEKnowledgeSearchTool(knowledge_path=knowledge_path),
        PrayerTimeTool(),
        TripBudgetPlanner(),
    ]

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key="input",  # Optional: specify the input key if needed
        output_key="output"  # Optional: specify the output key if needed
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=3,
        early_stopping_method="generate",
        memory=memory,
        agent_kwargs={
            "system_message": SYSTEM_RULES,
        },
    )
    return agent


# -----------------------------
# High-level helper for LLM tourist recommendations
# -----------------------------


def llm_recommendations(llm: Any, prompt: str) -> str:
    """Ask the LLM for itinerary-style suggestions.

    This bypasses the tools explicitly (Core Feature). The system rules instruct
    the agent when to do this; here we expose a convenience function for apps/UX.
    """
    # A lightweight meta-prompt to keep structure tidy and quick to generate
    instruction = (
        "You are an expert UAE trip planner. Provide a concise, day-by-day suggestion "
        "with 3-5 bullet points per day. Include short descriptions. Do not invent facts."
    )
    try:
        # All supported Chat* LLMs share .invoke in LC
        messages = [
            ("system", instruction),
            ("user", prompt),
        ]
        # langchain v0.2+ uses .invoke with a dict or list of messages
        resp = llm.invoke(messages)
        return getattr(resp, "content", str(resp))
    except Exception as e:
        return f"Failed to generate recommendations: {e}"


# -----------------------------
# CLI Demo
# -----------------------------


def _print_banner():
    print("\n=== UAE Smart Tourism Assistant (LangChain) ===")
    print("Type 'quit' to exit. Examples:")
    print("  • What are top cultural tips when visiting the UAE?")
    print("  • Prayer times in Dubai on 2025-08-24")
    print("  • Budget for 3 days in Ras Al Khaimah, luxury")
    print("  • Plan a 2-day trip to Abu Dhabi")
    print()


def interactive_demo():
    agent = build_agent()
    llm = _make_llm()
    _print_banner()

    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if user.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        itinerary_triggers = [
            "plan my", "itinerary", "what can i do", "things to do", "day trip", "trip plan",
        ]
        if any(t in user.lower() for t in itinerary_triggers):
            print("\n[LLM Recommendations]\n")
            print(llm_recommendations(llm, user))
            print()
            continue

        # Otherwise, let the ReAct agent decide and use tools
        try:
            answer = agent.invoke(user)  # Updated from `run` to `invoke`
        except Exception as e:
            answer = f"Agent error: {e}"
        print(f"\n{answer['output']}\n")


if __name__ == "__main__":
    interactive_demo()
