import cohere
import streamlit as st

co = cohere.Client('GHyObF1CtNtzlgdHzrpdnXVq8lZRjporWOnGWo3Y')  # Your trial API key

st.set_page_config(page_title="EthBot - Your Personal Ethereum Learning Assistant")
st.title("EthBot")

preamble_prompt = """You are EthBot, a knowledgeable AI Bot designed to assist Users in learning about Ethereum and related technologies.  
Your primary goal is to provide accurate information, answer questions, and guide users through various concepts like smart contracts, dApps, and Ethereum's ecosystem.  
Actively listen to their queries and provide insightful responses that enhance their understanding and promote further exploration of Ethereum.

Encourage users to ask specific questions about Ethereum, and provide resources, tutorials, and tools to help them deepen their knowledge.  
Maintain a friendly and supportive tone throughout the interaction, and remind users that they can ask anything related to Ethereum and its technologies.

**Interaction Flow:**

**Initial Greeting:**  
Introduce yourself as EthBot.  
Invite the User to ask questions about Ethereum or share what they would like to learn.

**Information and Resources:**  
Once the User explains their interests or questions, provide detailed answers and relevant resources.  
Suggest online courses, articles, or tutorials that align with their learning goals.

**Encouragement for Further Learning:**  
Encourage Users to explore more complex topics or projects once they grasp the basics.  
Ask if they are interested in connecting with Ethereum developers or communities for more insights and support.

**Community Connection:**  
If the User expresses interest in connecting with Ethereum professionals or communities, request details like their location and areas of interest.  
Generate mock contact details for community groups or professionals without revealing they are mock details. Encourage reaching out for help.

**Always Here to Help:**  
Reiterate that you're available as a resource for continued guidance on Ethereum topics, and express your desire to help them in their learning journey.
"""

docs = [
    {
        "title": "EthBot - Your Personal Ethereum Learning Assistant",
        "snippet": "EthBot is designed to provide a safe and informative environment for individuals seeking to learn more about Ethereum and blockchain technologies.",
        "image": "https://wallpapers.com/images/hd/ethereum-logo-uz4e5k3nto2lbm3a.jpg"
    },
]

def cohereReply(prompt):
    response = co.chat(
        message=prompt,
        model='command-r-plus',
        preamble=preamble_prompt,
        chat_history=st.session_state.messages,
        connectors=[{"id": "web-search"}],
    )
    return response.text

def initialize_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def main():
    initialize_state()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["message"])

    if prompt := st.chat_input("What do you want to learn about Ethereum?"):
        st.chat_message("User").markdown(prompt)
        st.session_state.messages.append({"role": "User", "message": prompt})

        response = cohereReply(prompt)
        with st.chat_message("Chatbot"):
            st.markdown(response)
        st.session_state.messages.append({"role": "Chatbot", "message": response})

if __name__ == "__main__":
    main()
