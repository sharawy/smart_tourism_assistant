# Smart UAE Tourism Agent

## Overview
The **Smart UAE Tourism Agent** is a modular LangChain-based assistant designed to provide tourists with information about the UAE. It integrates multiple tools to answer questions, recommend activities, and provide real-time data such as prayer times and trip budgets.

---

## Features
1. **Custom Tools**:
   - `UAEKnowledgeSearchTool`: Searches a local JSON knowledge base for city-specific or general UAE information.
   - `PrayerTimeTool`: Fetches prayer times for a given UAE city and date.
   - `TripBudgetPlanner`: Estimates trip costs based on the city, number of days, and travel style.

2. **LLM-Based Recommendations**:
   - Provides day-by-day itineraries and activity suggestions using a Large Language Model (LLM).

3. **Interactive Agent**:
   - Combines tools and LLM to answer user queries dynamically.

---

## Descriptions of Each Custom Tool

### 1. UAEKnowledgeSearchTool
- **Purpose**: Searches the `uae_knowledge.json` file for information about UAE cities, attractions, cultural tips, and activities.
- **Input**: A query string (e.g., "What are the top attractions in Dubai?").
- **Output**: Relevant information from the knowledge base.
- **Example**:
  - **Query**: `What are the top attractions in Dubai?`
  - **Output**:
    ```
    Information about Dubai:
    {
      "top_attractions": [
        "Burj Khalifa",
        "The Dubai Mall",
        "Dubai Marina",
        "Palm Jumeirah",
        "Dubai Creek",
        "Desert Safari"
      ],
      "cultural_tips": [
        "Dress modestly in public places.",
        "Public displays of affection are discouraged.",
        "Friday is a day of prayer and many businesses open late.",
        "Respect Ramadan customs if visiting during the holy month."
      ]
    }
    ```

---

### 2. PrayerTimeTool
- **Purpose**: Provides prayer times for a specific UAE city and date.
- **Input**: JSON with `city` and optional `date` (e.g., `{"city": "Dubai", "date": "2025-08-24"}`).
- **Output**: Prayer times for the specified city and date.
- **Example**:
  - **Query**: `Prayer times in Abu Dhabi on 2025-08-24`
  - **Output**:
    ```
    Prayer times for Abu Dhabi on 2025-08-24:
    Fajr: 04:20
    Dhuhr: 12:28
    Asr: 15:58
    Maghrib: 18:47
    Isha: 20:06
    ```

---

### 3. TripBudgetPlanner
- **Purpose**: Estimates the cost of a trip based on the city, number of days, and travel style.
- **Input**: JSON with `city`, `days`, and `style` (e.g., `{"city": "Sharjah", "days": 5, "style": "standard"}`).
- **Output**: Estimated cost in AED.
- **Example**:
  - **Query**: `Budget for 3 days in Ras Al Khaimah, luxury`
  - **Output**:
    ```
    Estimated cost for 3 day(s) in Ras Al Khaimah (luxury): 3000 AED (1000 AED/day).
    ```

---

## Explanation of LLM-Based Tourist Recommendations
The agent uses an LLM to generate personalized tourist recommendations and itineraries. These recommendations are based on user prompts and follow a structured format:
- **Input**: A user query requesting an itinerary or activity suggestions (e.g., "Plan a 2-day trip to Abu Dhabi").
- **Output**: A day-by-day plan with 3-5 activities per day, including short descriptions.
- **Example**:
  - **Query**: `Plan a 2-day trip to Abu Dhabi`
  - **Output**:
    ```
    Day 1:
    - Visit Sheikh Zayed Grand Mosque: A stunning architectural masterpiece.
    - Explore Louvre Abu Dhabi: A world-class art and culture museum.
    - Relax at Corniche Beach: Enjoy the sunset and a peaceful evening.

    Day 2:
    - Tour Qasr Al Watan: Discover the UAE's presidential palace.
    - Experience Ferrari World: Thrilling rides and attractions.
    - Dine at a local Emirati restaurant: Savor traditional cuisine.
    ```

---

## API Keys Used
The agent supports multiple LLM providers and APIs. Below are the required keys:
1. **OpenAI**:
   - **Environment Variable**: `OPENAI_API_KEY`
   - **Usage**: For OpenAI's GPT models.
2. **Google Generative AI (Gemini)**:
   - **Environment Variable**: `GOOGLE_API_KEY`
   - **Usage**: For Gemini models.
3. **Aladhan Prayer Times API**:
   - **Environment Variable**: `ALADHAN=1` (to enable API calls).
   - **Optional**: `PRAYER_METHOD` (to specify calculation method).

---

## Example Queries and Expected Outputs

| **Query**                                   | **Tool Used**         | **Expected Output**                                                                 |
|---------------------------------------------|-----------------------|-------------------------------------------------------------------------------------|
| `What are the top attractions in Dubai?`    | UAEKnowledgeSearchTool | List of attractions from `uae_knowledge.json`.                                      |
| `Prayer times in Abu Dhabi on 2025-08-24`   | PrayerTimeTool         | Prayer times for Abu Dhabi on the specified date.                                   |
| `Budget for 3 days in Ras Al Khaimah, luxury` | TripBudgetPlanner      | Estimated cost: `3000 AED`.                                                        |
| `Plan a 2-day trip to Abu Dhabi`            | LLM                   | A detailed 2-day itinerary with activities and descriptions.                        |

---

## How to Run
1. Install dependencies: ``` pip install -r requirements.txt```
2. Set up API keys:
   - Export the required keys as environment variables.
3. Run the agent: ``` python smart_uae_agent.py```
4. Use the interactive demo to test queries.