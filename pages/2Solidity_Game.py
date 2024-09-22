import streamlit as st

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
    for entry in sorted(st.session_state['leaderboard'], key=lambda x: x['points'], reverse=True):
        st.sidebar.write(f"{entry['name']}: {entry['points']} points")

# Define chapters with story, tasks, and interactive quizzes
chapters = {
    1: {
        "title": "🌟 Chapter 1: The Call to Solidity",
        "story": """
        In the kingdom of Ethereon, magic flows through smart contracts. To wield the power of Solidity, you must first learn its essence. 
        The ancient scrolls speak of a simple task to start your journey: Declare a magical number that others can see.
        """,
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
        "story": """
        The power of Solidity is in its ability to change the world—starting with numbers. 
        Now that you can declare a variable, can you command it to change?
        """,
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
        "story": """
        Now that you can declare and change numbers, your next challenge is to make Solidity perform calculations. 
        The spell of addition must be learned before you can progress.
        """,
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
        "story": """
        In this chapter, you must master the art of decision-making. Solidity can choose different paths based on conditions. 
        Wield the power of `if` to create logic in your contracts.
        """,
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
        st.title(chapter['title'])
        st.write(chapter['story'])

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
                st.success("🎉 Correct! You've earned 20 points!")
                st.session_state['points'] += 20
                st.session_state['current_chapter'] += 1
                st.rerun()  # Move to the next chapter
            else:
                st.error("❌ Oops! Try again.")

    else:
        # End of the story
        st.balloons()
        st.title("🎉 Victory! You've mastered the basics of Solidity!")
        st.session_state['leaderboard'].append({
            "name": st.session_state['character']['name'],
            "points": st.session_state['points']
        })
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
