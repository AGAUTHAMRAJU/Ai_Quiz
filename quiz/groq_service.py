import json
import re

from groq import Groq
from django.conf import settings

client = Groq(
    api_key=settings.GROQ_API_KEY
)

MODEL = "llama-3.3-70b-versatile"

def generate_feedback(topic, score, total):

    prompt = f"""
You are an expert mentor.

A student completed an assessment.

Topic:
{topic}

Score:
{score}/{total}

Write feedback in less than 80 words.

Mention:

1. Strength
2. Weakness
3. Suggestion

Return plain text only.
"""

    last_exception = None

    for attempt in range(3):

        try:

            response = client.chat.completions.create(

                model=MODEL,

                temperature=0.3,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content.strip()

        except Exception as e:

            last_exception = e

    raise last_exception

def generate_assessment(topic, difficulty, mcqs, theory):

    prompt = f"""
You are an expert university professor.

Generate an assessment.

TOPIC

{topic}

DIFFICULTY

{difficulty}

VERY IMPORTANT

Generate EXACTLY

MCQs = {mcqs}

Theory Questions = {theory}

Return ONLY valid JSON.

Do NOT return markdown.

Do NOT explain anything.

Do NOT write any text outside JSON.

Return EXACTLY this schema.

{{
    "mcqs":[
        {{
            "question":"",

            "options":[
                "",
                "",
                "",
                ""
            ],

            The "answer" field MUST contain the FULL TEXT of the correct option.

Example

Options

[
"Dog",
"Cat",
"Cow",
"Lion"
]

Correct JSON

"answer":"Cat"

Never return

"answer":"2"

Never return option numbers.,

            "explanation":""
        }}
    ],

    "theory":[
        {{
            "question":"",

            "expected_answer":""
        }}
    ]
}}

Rules

Every MCQ must contain

- question
- four options
- answer
- explanation

Every Theory Question must contain

- question
- expected_answer
"""

    last_exception = None

    for attempt in range(3):

        try:

            response = client.chat.completions.create(

                model=MODEL,

                temperature=0,

                response_format={
                    "type": "json_object"
                },

                messages=[
                    {
                        "role": "system",
                        "content": "Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            data = json.loads(
                response.choices[0].message.content
            )

            data.setdefault("mcqs", [])
            data.setdefault("theory", [])

            if len(data["mcqs"]) != mcqs:

                raise Exception(

                    f"Expected {mcqs} MCQs but received {len(data['mcqs'])}"

                )

            if len(data["theory"]) != theory:

                raise Exception(

                    f"Expected {theory} Theory Questions but received {len(data['theory'])}"

                )

            for mcq in data["mcqs"]:

                options = mcq.get("options", [])

                while len(options) < 4:

                    options.append("")

                mcq["options"] = options

                mcq.setdefault(
                    "answer",
                    ""
                )

                mcq.setdefault(
                    "explanation",
                    "No explanation provided."
                )

            for theory_question in data["theory"]:

                theory_question.setdefault(
                    "expected_answer",
                    ""
                )

            return data

        except Exception as e:

            last_exception = e

    raise last_exception


def generate_assessment_from_pdf(pdf_text, mcqs, theory):

    pdf_text = pdf_text[:12000]

    prompt = f"""
You are an expert university professor.

Read ONLY the PDF content below.

==========================
PDF CONTENT
==========================

{pdf_text}

==========================
TASK
==========================

Generate EXACTLY

{mcqs} Multiple Choice Questions

AND

{theory} Theory Questions

VERY IMPORTANT

1. Generate EXACTLY {mcqs} DIFFERENT MCQs.
2. Generate EXACTLY {theory} DIFFERENT Theory Questions.
3. Do NOT generate fewer questions.
4. Do NOT repeat questions.
5. Do NOT skip any question.

Each MCQ MUST contain

- question
- options (exactly 4)
- answer
- explanation

The answer MUST be the FULL TEXT of the correct option.

Example

{{
    "question":"Which language is used for web development?",
    "options":[
        "Python",
        "Java",
        "C",
        "PHP"
    ],
    "answer":"Python",
    "explanation":"Python is widely used for web development using Django and Flask."
}}

NEVER RETURN

"answer":"1"

or

"answer":"2"

or

"answer":"3"

or

"answer":"4"

Return ONLY valid JSON.

Return EXACTLY this format.

{{
    "mcqs":[
        {{
            "question":"",
            "options":[
                "",
                "",
                "",
                ""
            ],
            "answer":"",
            "explanation":""
        }}
    ],
    "theory":[
        {{
            "question":"",
            "expected_answer":""
        }}
    ]
}}

Do NOT write markdown.

Do NOT write ```json.

Return ONLY JSON.
"""

    last_exception = None

    for attempt in range(3):

        try:

            response = client.chat.completions.create(

                model=MODEL,

                temperature=0,

                max_completion_tokens=7000,

                response_format={
                    "type": "json_object"
                },

                messages=[
                    {
                        "role": "system",
                        "content": "Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.choices[0].message.content

            print("\n================ PDF RAW RESPONSE ================\n")
            print(content)
            print("\n==================================================\n")

            data = json.loads(content)

            data.setdefault("mcqs", [])
            data.setdefault("theory", [])

            while len(data["mcqs"]) < mcqs:

                data["mcqs"].append({

                    "question": "",

                    "options": [
                        "",
                        "",
                        "",
                        ""
                    ],

                    "answer": "",

                    "explanation": "No explanation."

                })

            while len(data["theory"]) < theory:

                data["theory"].append({

                    "question": "",

                    "expected_answer": ""

                })

            data["mcqs"] = data["mcqs"][:mcqs]
            data["theory"] = data["theory"][:theory]

            for mcq in data["mcqs"]:

                options = mcq.get("options", [])

                while len(options) < 4:

                    options.append("")

                mcq["options"] = options[:4]

                mcq.setdefault(
                    "answer",
                    ""
                )

                mcq.setdefault(
                    "explanation",
                    "No explanation provided."
                )

            for theory_question in data["theory"]:

                theory_question.setdefault(
                    "expected_answer",
                    ""
                )

            return data

        except Exception as e:

            last_exception = e

            if attempt < 2:

                continue

    raise last_exception


def evaluate_theory_answers(theory_questions, student_answers):

    prompt = f"""
You are an expert university professor.

Evaluate every theory answer.

Return ONLY valid JSON.

Return EXACTLY this format.

{{
    "results":[
        {{
            "question":"",
            "student_answer":"",
            "expected_answer":"",
            "score":0,
            "feedback":""
        }}
    ]
}}

Maximum score = 10.

Theory Questions

{json.dumps(theory_questions,indent=2)}

Student Answers

{json.dumps(student_answers,indent=2)}

Return ONLY JSON.
"""

    last_exception = None

    for attempt in range(3):

        try:

            response = client.chat.completions.create(

                model=MODEL,

                temperature=0,

                response_format={
                    "type":"json_object"
                },

                messages=[
                    {
                        "role":"system",
                        "content":"Return only valid JSON."
                    },
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            data = json.loads(
                response.choices[0].message.content
            )

            results = data.get("results", [])

            for item in results:

                item.setdefault(
                    "question",
                    ""
                )

                item.setdefault(
                    "student_answer",
                    ""
                )

                item.setdefault(
                    "expected_answer",
                    ""
                )

                item.setdefault(
                    "feedback",
                    "No feedback."
                )

                try:

                    item["score"] = float(
                        item.get("score",0)
                    )

                except:

                    item["score"] = 0

            return results

        except Exception as e:

            last_exception = e

    raise last_exception


def generate_pdf_mcqs(pdf_text, mcqs):

    pdf_text = pdf_text[:25000]

    prompt = f"""
You are an expert university professor.

Read ONLY the PDF content.

PDF CONTENT

{pdf_text}

Generate EXACTLY {mcqs} MULTIPLE CHOICE QUESTIONS.

VERY IMPORTANT

Return ONLY valid JSON.

Each MCQ must have

- question
- options (exactly 4)
- answer
- explanation

The answer MUST be the FULL TEXT of the correct option.

Example

{{
    "mcqs":[
        {{
            "question":"What is Python?",
            "options":[
                "Programming Language",
                "Snake",
                "Bird",
                "Car"
            ],
            "answer":"Programming Language",
            "explanation":"Python is a programming language."
        }}
    ]
}}

Do NOT generate theory questions.

Return ONLY

{{
    "mcqs":[]
}}
"""

    last_exception = None

    for attempt in range(3):

        try:

            response = client.chat.completions.create(

                model=MODEL,

                temperature=0,

                max_completion_tokens=6000,

                response_format={
                    "type":"json_object"
                },

                messages=[
                    {
                        "role":"system",
                        "content":"Return only valid JSON."
                    },
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            data = json.loads(
                response.choices[0].message.content
            )

            data.setdefault("mcqs", [])

            for mcq in data["mcqs"]:

                options = mcq.get("options", [])

                while len(options) < 4:

                    options.append("")

                mcq["options"] = options[:4]

                mcq.setdefault("answer", "")

                mcq.setdefault(
                    "explanation",
                    "No explanation provided."
                )

            return data

        except Exception as e:

            last_exception = e

    raise last_exception

def generate_pdf_theory(pdf_text, theory, previous_questions=None):
    if previous_questions is None:

        previous_questions = []

    previous_text = "\n".join(

        f"- {q}"

        for q in previous_questions

    )

    pdf_text = pdf_text[:25000]

    prompt = f"""
You are an expert university professor.

Read ONLY the PDF content.

====================
PDF CONTENT
====================

{pdf_text}

Generate EXACTLY {theory} THEORY QUESTIONS.

VERY IMPORTANT

Each question MUST contain

- question
- expected_answer

Return ONLY valid JSON.

Return EXACTLY

{{
    "theory":[
        {{
            "question":"",
            "expected_answer":""
        }}
    ]
}}

Do NOT generate MCQs.

Return ONLY JSON.
"""

    last_exception = None

    for attempt in range(3):

        try:

            response = client.chat.completions.create(

                model=MODEL,

                temperature=0,

                max_completion_tokens=4000,

                response_format={
                    "type":"json_object"
                },

                messages=[
                    {
                        "role":"system",
                        "content":"Return only valid JSON."
                    },
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            data = json.loads(
                response.choices[0].message.content
            )

            data.setdefault("theory", [])

            for q in data["theory"]:

                q.setdefault(
                    "question",
                    ""
                )

                q.setdefault(
                    "expected_answer",
                    ""
                )

            return data

        except Exception as e:

            last_exception = e

            if attempt < 2:

                continue

    raise last_exception

def generate_pdf_mcqs(pdf_text, mcqs, previous_questions=None):

    if previous_questions is None:

        previous_questions = []

    pdf_text = pdf_text[:25000]

    previous_text = "\n".join(

        f"- {q}"

        for q in previous_questions

    )

    prompt = f"""
You are an expert university professor.

Read ONLY the PDF below.

====================
PDF CONTENT
====================

{pdf_text}

====================
PREVIOUSLY GENERATED QUESTIONS
====================

{previous_text}

VERY IMPORTANT

The questions above have ALREADY been used.

DO NOT generate them again.

DO NOT paraphrase them.

DO NOT generate similar questions.

Choose DIFFERENT concepts from the PDF.

Generate EXACTLY {mcqs} UNIQUE MCQs.

Each MCQ must contain

- question
- options (4)
- answer
- explanation

The answer MUST be the FULL TEXT of the option.

Return ONLY JSON.

{{
    "mcqs":[
        {{
            "question":"",
            "options":[
                "",
                "",
                "",
                ""
            ],
            "answer":"",
            "explanation":""
        }}
    ]
}}
"""

    response = client.chat.completions.create(

        model=MODEL,

        temperature=0.8,

        max_completion_tokens=6000,

        response_format={

            "type":"json_object"

        },

        messages=[

            {

                "role":"system",

                "content":"Return only valid JSON."

            },

            {

                "role":"user",

                "content":prompt

            }

        ]

    )

    data = json.loads(

        response.choices[0].message.content

    )

    data.setdefault(

        "mcqs",

        []

    )

    return data












