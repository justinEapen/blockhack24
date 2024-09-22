import streamlit as st
import cohere
import pyttsx3  # For narration
import pygame   # For sound effects

# Initialize Cohere client
co = cohere.Client('GHyObF1CtNtzlgdHzrpdnXVq8lZRjporWOnGWo3Y')

# Initialize pygame for sound effects
pygame.mixer.init()

# Initialize pyttsx3 for text-to-speech
engine = pyttsx3.init()

# Function to generate personalized story elements
def generate_dynamic_story(chapter_title, role, progress):
    prompt = f"In a fantasy world, {role} embarks on Chapter {progress} titled '{chapter_title}'. Describe the challenges they face."
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=150
    )
    return response.generations[0].text

# Function to generate dynamic feedback for quiz answers
def generate_feedback(correct, role):
    if correct:
        prompt = f"As a {role}, after a victorious success in a challenge, describe how they feel and what their next goal is."
    else:
        prompt = f"As a {role}, after failing in a challenge, describe their determination to try again and how they plan to improve."
    
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=100
    )
    return response.generations[0].text

# Function to play sound effects
def play_sound(effect):
    sound_path = {
        'correct': 'correct_answer.wav',
        'incorrect': 'wrong_answer.wav',
        'victory': 'victory_sound.wav'
    }
    pygame.mixer.music.load(sound_path[effect])
    pygame.mixer.music.play()

# Function to narrate text
def narrate_text(text):
    engine.say(text)
    engine.runAndWait()

# Initialize the game state
if 'current_chapter' not in st.session_state:
    st.session_state['current_chapter'] = 1
    st.session_state['points'] = 0
    st.session_state['character'] = None
    st.session_state['leaderboard'] = []

# Character creation
if not st.session_state['character']:
    st.title("🧙‍♂️ Welcome to **Solidity Quest**!")
    st.subheader("Create Your Hero")
    
    name = st.text_input("📝 Enter your hero's name:")
    role = st.selectbox("🎯 Choose your path:", ["Wizard of Code 🧙‍♂️", "Blockchain Warrior 🛡️", "Smart Contract Alchemist 🔮"])
    
    if st.button("🚀 Begin Your Journey!"):
        if name:
            st.session_state['character'] = {"name": name, "role": role, "skills": []}
            st.success(f"✨ Welcome, {name}! The adventure awaits!")
            st.rerun()
        else:
            st.error("Please enter a name to start your journey.")

# Sidebar: Character and leaderboard display
if st.session_state['character']:
    st.sidebar.title("⚔️ Hero Stats")
    st.sidebar.write(f"Name: {st.session_state['character']['name']}")
    st.sidebar.write(f"Role: {st.session_state['character']['role']}")
    st.sidebar.write(f"Points: {st.session_state['points']}")

    st.sidebar.title("🏆 Leaderboard")
    if st.session_state['leaderboard']:
        for entry in sorted(st.session_state['leaderboard'], key=lambda x: x['points'], reverse=True):
            st.sidebar.write(f"{entry['name']}: {entry['points']} points")
    else:
        st.sidebar.write("No heroes have completed the quest yet.")

# Define chapters with story, tasks, and interactive quizzes
chapters = {
    1: {
        "title": "🌟 Chapter 1: The Call to Solidity",
        "task": "Your task is to create a public variable in Solidity that stores a number.",
        "code": """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;

        contract MyFirstContract {
            uint public myNumber = 42;
        }
        """,
        "quiz": {
            "question": "What keyword makes a variable visible to everyone on the blockchain?",
            "options": ["hidden", "private", "public", "external"],
            "answer": "public"
        }
    },
    2: {
        "title": "🔮 Chapter 2: Mastering Variables",
        "task": "Create a function to update the variable's value.",
        "code": """
        contract UpdateNumber {
            uint public number;

            function setNumber(uint _number) public {
                number = _number;
            }
        }
        """,
        "quiz": {
            "question": "Which keyword allows you to create a function that modifies the state of a contract?",
            "options": ["constant", "mutable", "view", "public"],
            "answer": "public"
        }
    },
    3: {
        "title": "⚔️ Chapter 3: The Logic of the Contract",
        "task": "Write a function that adds two numbers and returns the result.",
        "code": """
        contract AddNumbers {
            function add(uint a, uint b) public pure returns (uint) {
                return a + b;
            }
        }
        """,
        "quiz": {
            "question": "Which keyword is used to indicate a function won't modify the blockchain state?",
            "options": ["pure", "static", "view", "immutable"],
            "answer": "pure"
        }
    },
    4: {
        "title": "💡 Chapter 4: Conditional Magic",
        "task": "Write a function that checks if a number is even or odd and returns the result.",
        "code": """
        contract EvenOdd {
            function isEven(uint num) public pure returns (string memory) {
                if (num % 2 == 0) {
                    return "Even";
                } else {
                    return "Odd";
                }
            }
        }
        """,
        "quiz": {
            "question": "What operator is used to check if a number is divisible by another number?",
            "options": ["%", "*", "/", "+"],
            "answer": "%"
        }
    }
}

# Story progression logic
if st.session_state['character']:
    if st.session_state['current_chapter'] <= len(chapters):
        chapter = chapters[st.session_state['current_chapter']]
        
        # Generate dynamic story based on chapter and character
        dynamic_story = generate_dynamic_story(chapter['title'], st.session_state['character']['role'], st.session_state['current_chapter'])
        st.title(chapter['title'])
        st.write(dynamic_story)  # Display the dynamically generated story
        
        narrate_text(dynamic_story)  # Narrate the story

        # Show task and code for the chapter
        st.subheader("⚙️ Your Task")
        st.write(chapter['task'])
        st.code(chapter['code'], language="solidity")

        # Chapter quiz
        st.subheader("📚 Quiz Time")
        quiz = chapter['quiz']
        answer = st.radio(quiz['question'], quiz['options'])

        # Validate quiz answer
        if st.button("Submit Answer"):
            if answer == quiz['answer']:
                feedback = generate_feedback(True, st.session_state['character']['role'])  # Dynamic success feedback
                st.success(f"🎉 Correct! You've earned 20 points! {feedback}")
                play_sound('correct')  # Play correct answer sound
                st.session_state['points'] += 20
                st.session_state['current_chapter'] += 1
                st.rerun()  # Move to the next chapter
            else:
                feedback = generate_feedback(False, st.session_state['character']['role'])  # Dynamic failure feedback
                st.error(f"❌ Oops! Try again. {feedback}")
                play_sound('incorrect')  # Play incorrect answer sound

    else:
        # End of the story
        st.balloons()
        st.title("🎉 Victory! You've mastered the basics of Solidity!")
        play_sound('victory')  # Play victory sound
        
        # Add the current character's score to the leaderboard
        st.session_state['leaderboard'].append({
            "name": st.session_state['character']['name'],
            "points": st.session_state['points']
        })
        
        # Display the leaderboard
        st.subheader("🏆 Final Leaderboard")
        for entry in sorted(st.session_state['leaderboard'], key=lambda x: x['points'], reverse=True):
            st.write(f"{entry['name']}: {entry['points']} points")

        # Reset game state but keep the leaderboard
        st.session_state['current_chapter'] = 1
        st.session_state['points'] = 0
        st.session_state['character'] = None
        st.rerun()

# Reset the game
if st.sidebar.button("🔄 Restart Adventure"):
    st.session_state['current_chapter'] = 1
    st.session_state['points'] = 0
    st.session_state['character'] = None
    st.rerun()
