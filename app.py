
from   b   import Flask, request, jsonify, render_template_string
from nltk.tokenize import wordpunct_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

app = Flask(__name__)

# ---------------- FAQ DATA ----------------

faqs = [
    {
        "question": "What courses are available?",
        "answer": "We offer courses such as BCA, BBA, B.Tech and other undergraduate programs. Contact the college for the official list."
    },
    {
        "question": "How can I apply for admission?",
        "answer": "Visit the college's official admission portal, fill out the application form, and follow the admission instructions."
    },
    {
        "question": "What is the college fee?",
        "answer": "The fee depends on the selected course. Please contact the college office for the latest fee structure."
    },
    {
        "question": "What are the admission requirements?",
        "answer": "Admission requirements depend on the course. Check the official college website for eligibility and required documents."
    },
    {
        "question": "How can I contact the college?",
        "answer": "You can contact the college administration through its official website or visit the college office."
    },
    {
        "question": "What are the college opening hours?",
        "answer": "Please check the college's official website or contact the administration for current working hours."
    },
    {
        "question": "Does the college provide placements?",
        "answer": "The placement cell may provide career guidance, interview preparation, and recruitment opportunities. Contact the college for details."
    },
    {
        "question": "Where is the college located?",
        "answer": "Please visit the official college website for its address and directions."
    }
]

# ---------------- NLP PREPROCESSING ----------------

stop_words = {
    "is", "am", "are", "the", "a", "an", "what", "how",
    "do", "does", "can", "i", "you", "my", "your", "to",
    "for", "of", "in", "on", "and", "please", "me", "tell"
}

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = wordpunct_tokenize(text)

    return " ".join(
        word for word in tokens
        if word not in stop_words and len(word) > 1
    )

questions = [faq["question"] for faq in faqs]
processed_questions = [preprocess(q) for q in questions]

vectorizer = TfidfVectorizer()
faq_vectors = vectorizer.fit_transform(processed_questions)

# ---------------- CHATBOT UI ----------------

html_page = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FAQ Chatbot</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #e0e7ff, #f8fafc);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
}

.chat-container {
    width: 100%;
    max-width: 480px;
    height: 650px;
    max-height: 92vh;
    background: white;
    border-radius: 18px;
    box-shadow: 0 10px 35px #00000020;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.header {
    background: #4f46e5;
    color: white;
    padding: 20px;
}

.header h2 {
    margin: 0 0 8px;
}

.header p {
    margin: 0;
    font-size: 13px;
}

.clear-btn {
    margin-top: 12px;
    background: transparent;
    color: white;
    border: 1px solid white;
    padding: 7px 12px;
    border-radius: 6px;
    cursor: pointer;
}

.chat-box {
    flex: 1;
    overflow-y: auto;
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.message {
    max-width: 85%;
    padding: 12px 14px;
    border-radius: 14px;
    line-height: 1.5;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
}

.bot {
    background: #f1f5f9;
    color: #1e293b;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}

.user {
    background: #4f46e5;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

.suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    padding: 0 14px 12px;
}

.suggestions button {
    border: 1px solid #c7d2fe;
    background: #eef2ff;
    color: #4338ca;
    border-radius: 20px;
    padding: 8px 10px;
    cursor: pointer;
}

.chat-form {
    display: flex;
    gap: 8px;
    padding: 14px;
    border-top: 1px solid #e2e8f0;
}

.chat-form input {
    flex: 1;
    min-width: 0;
    padding: 12px;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    outline: none;
}

.chat-form input:focus {
    border-color: #4f46e5;
}

.send-btn {
    padding: 0 18px;
    border: none;
    border-radius: 10px;
    background: #4f46e5;
    color: white;
    cursor: pointer;
}

.send-btn:disabled {
    opacity: 0.6;
    cursor: wait;
}
</style>
</head>

<body>
<div class="chat-container">

    <div class="header">
        <h2>FAQ Assistant</h2>
        <p>Ask me anything. I'm here to help!</p>
        <button class="clear-btn" id="clearBtn">Clear Chat</button>
    </div>

    <div class="chat-box" id="chatBox" aria-live="polite"></div>

    <div class="suggestions">
        <button data-question="What courses are available?">Courses</button>
        <button data-question="How can I apply for admission?">Admission</button>
        <button data-question="What is the college fee?">Fees</button>
    </div>

    <form class="chat-form" id="chatForm">
        <input
            type="text"
            id="userInput"
            placeholder="Type your question..."
            autocomplete="off"
            required
        >
        <button type="submit" class="send-btn" id="sendBtn">Send</button>
    </form>
</div>

<script>
const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

function addMessage(text, sender) {
    const message = document.createElement("div");
    message.className = "message " + sender;
    message.textContent = text;
    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
    return message;
}

function welcome() {
    addMessage(
        "Hello! Welcome to the FAQ Assistant. How can I help you today?",
        "bot"
    );
}

chatForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const message = userInput.value.trim();

    if (!message || sendBtn.disabled) return;

    addMessage(message, "user");
    userInput.value = "";
    sendBtn.disabled = true;

    const loading = addMessage("Finding the best answer...", "bot");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: message})
        });

        if (!response.ok) throw new Error("Request failed");

        const data = await response.json();
        loading.textContent = data.answer;
    } catch (error) {
        loading.textContent =
            "Unable to connect. Please check that the server is running.";
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});

document.querySelectorAll("[data-question]").forEach(button => {
    button.addEventListener("click", function() {
        userInput.value = button.dataset.question;
        chatForm.requestSubmit();
    });
});

document.getElementById("clearBtn").addEventListener("click", function() {
    chatBox.replaceChildren();
    welcome();
});

welcome();
</script>
</body>
</html>
"""

# ---------------- FLASK ROUTES ----------------

@app.route("/")
def home():
    return render_template_string(html_page)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"answer": "Please enter a question."})

    processed_message = preprocess(user_message)

    if not processed_message:
        return jsonify({
            "answer": "Please enter a question with meaningful words."
        })

    user_vector = vectorizer.transform([processed_message])

    similarities = cosine_similarity(
        user_vector, faq_vectors
    ).flatten()

    best_index = similarities.argmax()
    best_score = similarities[best_index]

    if best_score < 0.15:
        answer = (
            "Sorry, I couldn't find a matching FAQ. "
            "Please try asking another question."
        )
    else:
        answer = faqs[best_index]["answer"]

    return jsonify({"answer": answer})


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
