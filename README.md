# 🏚️ AI Home Renovation Planner (Full-Stack Multi-Agent System)

An end-to-end, multi-agent AI system that analyzes photos of your space, creates personalized renovation plans, and generates photorealistic renderings. Built using Google ADK and powered by Gemini Pro's multimodal capabilities, this project demonstrates complex AI orchestration combined with a premium full-stack web application.

---

## 🚀 Tech Stack

- **Backend / AI Orchestration:** Python, FastAPI, Google ADK (Agent Development Kit)
- **AI Models:** Gemini Pro (Multimodal Vision & Generation)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Custom Glassmorphism UI)
- **Architecture:** Coordinator/Dispatcher Pattern, Sequential Pipelines, REST API

---

## 🏗️ Architecture & Interview Talking Points

This project goes beyond simple LLM wrappers by implementing a production-ready **Multi-Agent Architecture**:

1. **Coordinator/Dispatcher Pattern**: 
   - A root "Router" agent acts as the brain, analyzing the user's intent. It routes general Q&A to a quick Info Agent, and complex design tasks to a specialized Planning Pipeline.
2. **Sequential Planning Pipeline**:
   - **Visual Assessor 📸:** Ingests user-uploaded photos, extracts the structural layout, estimates current condition, and parses styling preferences from inspiration images.
   - **Design Planner 🎨:** Takes the visual constraints and cross-references them with the user's budget. It generates a highly specific, actionable design specification.
   - **Project Coordinator 🏗️:** Compiles the design plan into a realistic timeline and budget breakdown, and uses generative tools to output a final photorealistic rendering of the renovated space.
3. **Full-Stack Execution & State Management**:
   - Features a high-performance **FastAPI backend** that handles multipart form data, asynchronous streaming, and session persistence.
   - The frontend is built from scratch without bulky frameworks, showcasing deep CSS knowledge through a **Premium Glassmorphism UI** with micro-animations and drag-and-drop file handling.

---

## ✨ Features

- **🔍 Smart Image Analysis**: Automatically detects room dimensions, layout, and style from uploaded current/inspiration photos.
- **🎨 Photorealistic Rendering**: Generates professional-quality images of the proposed renovated space using generative vision models.
- **💰 Budget-Aware Planning**: Tailors material recommendations and scope to strictly adhere to user budget constraints.
- **📊 Complete Roadmap**: Provides an actionable timeline, cost breakdown, and contractor hiring checklist.
- **✏️ Iterative Refinement**: Maintains session state, allowing users to iteratively chat and edit renderings (e.g., *"Make the cabinets cream instead"*).

---

## 💻 Setup & Installation

1. **Install dependencies**
   ```bash
   pip install -r renovation_agent/requirements.txt
   ```

2. **Set up your API key**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
   *(Get a free key at [Google AI Studio](https://aistudio.google.com/apikey))*

3. **Run the Server**
   ```bash
   python ui/server.py
   ```

4. **Open the App**
   Navigate to **http://127.0.0.1:3001** in your browser.

---

## 🛠️ Usage Scenarios

| Scenario | Example Input |
|----------|---------|
| **Current room + budget** | Upload kitchen photo + *"What can I improve with a $5k budget?"* |
| **Room + inspiration** | Upload your kitchen + Pinterest photo + *"Transform my kitchen to look like this."* |
| **Text only** | *"Renovate my 10x12 kitchen with oak cabinets. I want a modern farmhouse style. Budget: $30k"* |
| **Iterative refinement** | After initial rendering: *"Make the cabinets cream and add pendant lights."* |

---

## 📄 ATS-Friendly Resume Points

- **Architected a Coordinator/Dispatcher Multi-Agent System (Google ADK)** that intelligently routes user intents to a Sequential Planning Pipeline for specialized execution.
- **Engineered specialized AI agents (Visual Assessor & Design Planner)** utilizing Gemini Pro Multimodal to extract structural layouts from photos and generate strict, budget-aware renovation blueprints.
- **Developed an asynchronous FastAPI & custom Glassmorphism UI**, orchestrating real-time data streaming, dynamic photorealistic image generation, and robust end-to-end session state management.
