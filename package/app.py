'''Frontend application'''
import random
import requests
import streamlit as st
import streamlit_javascript as st_js


screen_width = st_js.st_javascript("screen.width")
screen_height = st_js.st_javascript("screen.height")

try:
    font_size = "24pt" if (screen_width / screen_height) < 1 else "34pt"
except:
    font_size = "34pt"

# import South Park font
# with open( "font.css" ) as css:
#    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

# move title up vertically
st.markdown("""
    <style>
    #welcome-to-south-park {
        margin-top: -70px !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# centered and resized title
st.markdown(f"""
    <h1 style='text-align: center;
    color: white;
    font-size: {font_size};
    '>Welcome to South Park</h1>
    """,
    unsafe_allow_html=True
)

# 100% transparant chat widget
INPUT_CHAT = """
    <style>
    .st-emotion-cache-1uj96rm {
        background-color: unset;
    }
    .st-emotion-cache-13k62yr {
        background: unset;
    }
    .st-emotion-cache-vj1c9o {
        background-color: rgba(0,0,0,0) !important;
    }
    .st-emotion-cache-vj1c9o ea3mdgi6
        background-color: rgba(0,0,0,0) !important;
    }
    .st-emotion-cache-ea3mdgi1 {
        background-color: rgba(0,0,0,0) !important;
    }
    </style>
"""
st.markdown(INPUT_CHAT, unsafe_allow_html=True)

# all text white
custom_css = """
<style>
    body, h1, h2, h3, h4, h5, h6, p, .st-emotion-cache-4oy321, .stChatMessage>div>div>input, .stTextInput>div>div>input, .stSelectbox>div>div>select {
        color: #ffffff;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = []

URL_API = "http://34.116.231.56:8000/reply"
AVATAR_URL = "https://lh3.googleusercontent.com/drive-viewer/AKGpihbbAs05bCjniJ4eSfLZ92o3Hd4NqFr6GOeayVDZyQvJY-TAon6qgUTzavwS_AcYR_XiSw6f-bne6lliYb9k107vC826Fg=s2560"
USER_AVATAR = "https://lh3.googleusercontent.com/drive-viewer/AKGpihaL6MFQ-kZhHpA312L6PTit1S8V0ZHd6tAqXcTELfjxB2iFeZ_SI6LjL1VRpHmM07nv9q0sVQ1ZLk7SUv6cDDZSWCBdVw=s2560"

# create function to get messages
def llm_messages(**kwargs):
    '''Function to get LLM input on user prompt'''

    history = kwargs['history']
    prompt = st.session_state.user_input
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "avatar": USER_AVATAR
    })
    history.append({"role": "user", "content": f"user: {prompt}"})

    # random number of replies from characters, max 3
    chat_length = random.choice([0,1,1,1,2,2,2])
    character_select = "user"

    for i in range(chat_length+1):

        data = {
            "counter": i,
            "chat_length": chat_length,
            "history": history,
            "character_select": character_select
        }

        r = requests.post(
            URL_API,
            json=data,
            timeout=None
        )
        llm_answer = r.json()
        character_select = llm_answer['character_select']
        history = llm_answer['history']

        # add assistant response to streamlit chat history
        st.session_state.messages.append({
            "role": "South Park",
            "content": history[-1]['content'],
            "avatar": AVATAR_URL
        })

        if character_select == "user":
            break


# accept user input and initialize function to get LLM messages
st.chat_input(
    "What's up?",
    on_submit=llm_messages,
    key="user_input",
    kwargs={'history': st.session_state.history}
)

# display chat messages from history on app rerun
for message in st.session_state.messages:
    # create a chat bubble for role
    with st.chat_message(
        name=message["role"],
        avatar=message.get("avatar")
    ):
        # write text of messages in chat bubble for that role
        st.markdown(message["content"])

# set background
URL_DESKTOP = "https://lh3.googleusercontent.com/drive-viewer/AKGpihYZkUX4z4WAvzHfMcpEeASpI1_5RLW9LBAtWw3lYP8iYBQDs1P3Vi77K3Rx1MgZ3BRfXJtjoiTtwX7JG72LCzzzBi89=s1600"
URL_MOBILE = "https://lh3.googleusercontent.com/drive-viewer/AKGpihauOpILrTPlPWjyf1de3U-CSx7I6ocuox36agcCk4UHq4QjG9Iv9YYlANhD45LxRMdkv1FPLHogjvqoOtYphtRGL380_A=s1600"

try:
    URL = URL_MOBILE if (screen_width / screen_height) < 1 else URL_DESKTOP
except:
    URL = URL_DESKTOP

background_image = f"""
    <style>
    [data-testid='stAppViewContainer'] {{
        background-image: url({URL});
        background-size: cover;
        background-position: bottom;
    }}
    [data-testid="stHeader"] {{
        background-color: rgba(0,0,0,0);
    }}
    </style>
    """
st.markdown(background_image, unsafe_allow_html=True)

# auto scroll to bottom
scroll_script = """
    <script>
    window.scrollTo(0,document.body.scrollHeight);
    </script>
"""
st.markdown(scroll_script, unsafe_allow_html=True)
