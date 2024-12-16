import streamlit as st
import openai_api
from audiorecorder import audiorecorder # pip install streamlit-audiorecorder
from streamlit_chat import message as msg # pip install streamlit-chat


# pip install streamlit, streamlit-audiorecorder streamlit-chat
# ffmpeg(인코딩-디코딩 담당) 다운로드 https://www.gyan.dev/ffmpeg/builds/

def main():
    # 상단 제목
    st.set_page_config(
        page_title="🎙️Voice Chatbot🎙️",
        page_icon='⭐',
        layout = 'wide'
    )
    st.header('🎤Voice Chatbot🎤')
    st.markdown('---')

    # 챗봇 사용법
    with st.expander('🔵Voice Chatbot 프로그램을 사용하는 방법🔵', expanded=True):
        st.write(
            """
            1. 녹음하기 버튼을 눌러 질문을 녹음합니다.
            2. 녹음이 완료되면 자동으로 Whisper 모델이 음성을 텍스트로 변환 후 LLM에 질의합니다.
            3. LLM의 응답을 다시 TTS 모델을 사용해 음성으로 변환하고 이를 사용자에게 응답합니다.
            4. LLM은 OpenAI사의 GPT 모델을 사용합니다.
            5. 모든 질문/답변은 텍스트로도 제공합니다.
            """
        )
    st.markdown(' ') # 한줄 띄기

    system_instruction = '당신은 친절한 챗봇입니다.'

    # session state 초기화
    # - messages: LLM 질의를 위한 대화 내역/웹페이지 시각화용 대화내역
    # - check_reset: 초기화를 위한 플레그
    if 'chats' not in st.session_state:
        st.session_state['chats'] = [] # 선언

    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {'role': 'system', 'content': system_instruction}
        ]

    if 'check_reset' not in st.session_state:
        st.session_state['check_reset'] = False

    # 사이드 바 - 모델 선택
    with st.sidebar:
        model = st.radio(label='GPT 모델 선택', options=['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o'])
        print('모델: ', model)

        if st.button(label='초기화'):
            st.session_state['messages'] = [
                {'role': 'system', 'content': system_instruction}
            ]
            st.session_state['check_reset'] = True # 화면 정리(reset)

    # 녹음 / 질문 답변 칸
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('녹음하러 가기💨')

        audio = audiorecorder()

        if (audio.duration_seconds > 0) and (st.session_state['check_reset']==False):
            # 화면 상 재생 기능
            st.audio(audio.export().read()) # mp3꺼내서 전달 (재생할 수 있는 모양)
            # 사용자 음성 >> 텍스트 추출
            query = openai_api.stt(audio)  # speech->text
            print('Q: ', query)
            # LLM 질의
            st.session_state['messages'].append({'role': 'user', 'content': query}) # 추가
            response = openai_api.ask_gpt(st.session_state['messages'], model)
            print('A: ', response)
            st.session_state['messages'].append({'role': 'assistant', 'content': response})
            # 음성으로 변환
            audio_tag = openai_api.tts(response)
            st.html(audio_tag) # 시각화 없이 자동 재생

    with col2:
        st.subheader('질문/답변 💭')
        if (audio.duration_seconds > 0) and (st.session_state['check_reset'] == False):
            for i, message in enumerate(st.session_state['messages']):
                role = message['role']
                content = message['content']
                if role == 'user': # 사용자
                    msg(content, is_user = True, key=str(i))
                elif role == 'assistant': # ai 답변
                    msg(content, is_user = False, key=str(i))
        else:
            # 초기화 버튼 누르면, 화면이 정리되고, 다시 check_reset을 원상복구
            st.session_state['check_reset'] = False



if __name__ == '__main__':
    main()