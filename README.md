# NSBEUOFT Hacks 2025 - 2nd Place

Demo: (https://www.youtube.com/watch?v=-O3PqlDuvXU)
Devpost Link (For More Information/Screenshots): https://devpost.com/software/stud-io

## Inspiration
The inspiration behind *Stud.io* came from the challenges students face when preparing for exams. We wanted to create a tool that not only generates flashcards from lecture notes but also adapts to each student's learning needs using AI and machine learning (reinforcement learning). We aimed to blend the convenience of automated flashcard creation with personalized learning insights to help students study smarter.

## What it does
Stud.io is an intelligent flashcard generation app designed to help students enhance their learning by transforming lecture notes, and other study materials into interactive questions. The app leverages Q-learning, a model-free reinforcement learning technique, to track student performance, identifying areas of difficulty and prioritizing those topics for future study sessions. Students can specify what interactive questions they want - multiple choice, fill in the blanks, and more!

Flashcards are vectorized and stored in a vector database, enabling rapid retrieval of similar questions through vector search using cosine similarity. This ensures that students are consistently tested on concepts they struggle with, reinforcing their understanding and closing knowledge gaps over time.

Stud.io integrates large language models (LLMs) to generate high-quality flashcards from study materials and evaluate student responses, providing instant feedback and personalized insights. The app offers two distinct modes: Study Mode, where students are presented with questions they have answered least accurately to focus on weak areas, and Review Mode, which helps students build a solid understanding of general concepts.

With continuous question generation from LLMs and real-time performance tracking through Q-learning, Stud.io ensures a dynamic and tailored learning experience. The app also notifies students when their performance in specific topics needs improvement, encouraging consistent study habits and ultimately leading to better academic outcomes.

The app has a minimum threshold that students must perform on in general topics they're being tested on. If the reinforcement learning model indicates that a student is performing very poorly in a certain subject, the app will notify them and prioritize flashcards on the student's weakest topics.

## How we built it
We built *Stud.io* using Next.js for the frontend and Flask for the backend. MongoDB Atlas serves as our database, where we store user performance data, flashcards, and vector embeddings. Reinforcement learning with Q-tables tracks user performance, while vector search helps retrieve similar flashcards. LLMs like GPT-4-turbo handle flashcard generation and evaluation of answers from input materials and test questions respectively.

## Challenges we ran into
One major challenge was integrating reinforcement learning with a scalable backend. Ensuring that user performance data updated dynamically without slowing down the app was tricky. Implementing vector search was another hurdle, as we had to register the vector index in MongoDB Atlas and had to create the embeddings to search through with OpenAI. Additionally, working with LLM APIs introduced latency challenges that we had to optimize.

## Accomplishments that we're proud of
We're proud of creating a seamless user experience where students can upload their lecture notes and instantly get personalized flashcards. Successfully integrating reinforcement learning and vector search into an educational tool is a significant accomplishment. Our app's ability to adapt to each user's needs and continuously generate new study materials is something we take pride in.

## What we learned
We learned a lot about reinforcement learning and its practical applications in education. Handling large datasets with vector search taught us how to optimize database queries for performance. Integrating LLMs into a dynamic app also provided valuable insights into prompt engineering and API management.

## What's next for Stud.io
Next, we plan to enhance *Stud.io* by adding more support for different input formats like handwritten notes and images. We aim to refine our reinforcement learning algorithms for even better personalization. Adding social features like study groups and collaborative flashcard creation is also on our roadmap. Ultimately, we envision *Stud.io* becoming a comprehensive study companion for students worldwide.

