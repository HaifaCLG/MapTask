import streamlit as st
from streamlit_elements import dashboard, mui, elements, html
from PIL import Image, ImageDraw, ImageFont
import json
import os
import datetime
from pages.common.versions import *
from pages.common.gt_path import *
from pages.common.dialog_analysis import *


def read_raw_data():
    data_list = []
    for file_name in os.listdir(root_folder):
        json_file = open(os.path.join(root_folder, file_name), encoding='utf8')
        data = json.load(json_file)
        for game_data in data['games_data']:
            # fix chat times
            chat = game_data['chat']
            for chat_ele in chat:
                timestamp = chat_ele['timestamp']

                date_obj = datetime.datetime.fromtimestamp(timestamp / 1000.0)
                date_of_chat = date_obj.strftime("%D")
                chat_ele['time'] = date_obj.strftime("%H:%M:%S")
                data['date'] = date_of_chat

        data_list.append(data)
    return data_list


data_list = read_raw_data()
st.set_page_config(page_title="singleDialog", page_icon="📈", layout="wide")
st.sidebar.success("Single Dialog")

if 'file_idx' not in st.session_state:
    st.session_state.file_idx = 0
if 'game_idx' not in st.session_state:
    st.session_state.game_idx = 0
if 'search_id' not in st.session_state:
    st.session_state.search_id = ''


def next_call_click():
    if st.session_state.file_idx == len(data_list) - 1:
        return
    st.session_state.file_idx += 1
    st.session_state.game_idx = 0


def last_call_click():
    if st.session_state.file_idx == 0:
        return
    st.session_state.file_idx -= 1
    st.session_state.game_idx = 0


def next_game_click():
    games_data = data_list[st.session_state.file_idx]['games_data']
    if st.session_state.game_idx == len(games_data) - 1:
        return
    st.session_state.game_idx += 1


def last_game_click():
    if st.session_state.game_idx == 0:
        return
    st.session_state.game_idx -= 1


def search_by_pid():
    new_pid = st.session_state.search_id

    found = False
    for idx, data_ele in enumerate(data_list):
        if data_ele['prolific']['prolific_id'] == new_pid:
            st.session_state.file_idx = idx
            st.session_state.game_idx = 0
            found = True
            break

    if not found:
        st.warning(f"pid: '{new_pid}' doesnt exist", icon="⚠️")


def clear_text():
    search_by_pid()
    st.session_state.search_id = ""


# keep in first render
st.text_input('Search Prolific Id', key='search_id', on_change=clear_text, placeholder="Type here")
st.header(f"Participant: {st.session_state.file_idx + 1}/{len(data_list)}")
map_img_col, general_info_col, nav_btns_col = st.columns([0.4, 0.4, 0.4])


def draw_nav_path(im, user_path: list, map_idx: int):
    font_size = 50 if map_idx == 2 else 100
    fnt = ImageFont.truetype("font/arial.ttf", font_size)
    rows = 18
    cols = 24

    draw = ImageDraw.Draw(im)
    width, height = im.size
    col_size = width / cols
    row_size = height / rows
    for idx, user_coord in enumerate(user_path):

        if idx % 4 == 0:
            color = 'white'
        elif idx % 4 == 1:
            color = 'red'
        elif idx % 4 == 2:
            color = 'cyan'
        else:
            color = (124, 252, 0)

        row = user_coord['r']
        col = user_coord['c']
        text = f'{idx + 1}'
        x = col_size * col
        y = row_size * row
        draw.text((x, y), text, font=fnt, fill=color)


with map_img_col:
    map_idx = st.session_state.game_idx
    image = Image.open(f"maps/map{map_idx + 1}_1.jpg")

    call_data = data_list[st.session_state.file_idx]
    curr_game_data = call_data['games_data'][st.session_state.game_idx]
    img_width = 500
    if curr_game_data['config']['game_role'] == 'navigator':
        draw_nav_path(image, curr_game_data['user_map_path'], map_idx)
        # draw_nav_path(image, gt_maps[map_idx], map_idx)

    st.image(image, width=img_width, caption=f'Map: {map_idx + 1}')

    call_data = data_list[st.session_state.file_idx]
    version = call_data['server_version']

    st.text(f"Version: {version} ")
    st.text(f"Prolific id: {call_data['prolific']['prolific_id']} ")
    st.text(f"Experiment - {experiments_short_names[version]}: {version_details.get(version, '')}")
    st.text(f"Date: {call_data['date']} 📅")
    st.text(f"Code-switch strategy: {call_data['cs_strategy']} ")
    st.text(f"Game time: {curr_game_data['game_time']} seconds ⌛")

with general_info_col:
    call_data = data_list[st.session_state.file_idx]
    curr_game_data = call_data['games_data'][st.session_state.game_idx]
    version = call_data['server_version']

    role = curr_game_data['config']['game_role']
    user_dialog, bot_dialog = analysis_game_chat(role, curr_game_data['chat'])

    st.subheader('General info')
    st.text(f"Human role: {role} 🧭")

    if user_dialog is not None:
        for dialog_key in user_dialog:
            if 'mean' in dialog_key:
                val = f"{user_dialog[dialog_key]:.2f}"
            elif '%' in dialog_key:
                val = f'{round(user_dialog[dialog_key] * 100, 2)}%'
            else:
                val = user_dialog[dialog_key]

            if any(l in dialog_key for l in cong_cs_labels) and val == 0:
                continue
            st.text(f"user - {dialog_key}: {val} 💪️")

    is_nav = curr_game_data['config']['game_role'] == 'navigator'
    if is_nav:
        dist_score = path_dist(st.session_state.game_idx, curr_game_data['user_map_path'])
        st.text(f"Dist Score: {dist_score:.2f} ")

with nav_btns_col:
    st.subheader('Navigate')

    prev_col, next_col = st.columns([0.5, 0.5])
    with prev_col:
        last_call = st.button('⏮️ Previous Participant ', on_click=last_call_click)
        last_game = st.button('⏮️⏮️ Previous Map', on_click=last_game_click)
    with next_col:
        next_call = st.button('Next Participant ⏭️️', on_click=next_call_click)
        next_game = st.button('Next Map ⏭️⏭️️', on_click=next_game_click)

    # st.divider()

    for dialog_key in bot_dialog:
        val = f"{bot_dialog[dialog_key]:.2f}" if 'mean' in dialog_key else bot_dialog[dialog_key]
        st.text(f"bot - {dialog_key}: {val} 🦾")


def render_chat():
    curr_game_data = data_list[st.session_state.file_idx]['games_data'][st.session_state.game_idx]
    curr_chat = curr_game_data['chat']
    human_role = curr_game_data['config']['game_role']
    is_nav = human_role == 'navigator'

    with mui.Paper(key="dialog", sx={
        "display": 'flex',
        "flexDirection": 'column',
        "overflowY": 'auto'}):
        with mui.Typography:
            for chat_ele in curr_chat:
                is_human = human_role == chat_ele['id']

                side = 'flex-end' if not is_human else 'flex-start'
                textAlign = 'end' if not is_human else 'start'
                bg_color = 'rgb(72, 70, 68)' if not is_human else 'rgb(63, 81, 181)'

                chat_map_path_idx = ''
                if is_nav and chat_ele['id'] == 'navigator':
                    coord = chat_ele['curr_nav_cell']
                    chat_map_path_idx = curr_game_data['user_map_path'].index(coord) + 1
                    chat_map_path_idx = f"path idx: {chat_map_path_idx}"

                ins_cs_switch = ''
                if chat_ele['cong_cs']:
                    nouns = [f'{noun}-{label}' for label, noun in chat_ele['cong_cs']]
                    ins_cs_switch = ' '.join(nouns)

                html.div(
                    html.div(
                        html.p(f"{chat_ele['id']}: ", css={'fontWeight': '700'}),
                        html.p(f"{chat_ele['msg']}"),
                        html.p(f"{chat_ele['time']}", css={'font-size': '13px', 'margin-bottom': '14px'}),
                        html.p(f"{chat_ele['lang']}", css={'font-size': '13px', 'margin-bottom': '14px'}),
                        html.p(ins_cs_switch, css={'font-size': '13px', 'margin-bottom': '14px'}),
                        html.p(chat_map_path_idx, css={'font-size': '13px', 'margin-bottom': '14px', 'font-style': 'italic'}),

                        css={
                            "display": "flex",
                            "gap": '0.5em',
                            "align-items": 'center',
                            "padding": '0.5em',
                            "margin": '0.5em',
                            'color': 'white',
                            'background-color': bg_color,
                            'border-radius': '8px',
                            'width': 'fit-content',
                            'text-align': textAlign
                        },
                    ),
                    css={
                        "display": "flex",
                        'justify-content': side,
                    }
                )


def render_survey(dash_key: str):
    call_data = data_list[st.session_state.file_idx]

    if call_data['clinet_version'] >= '2.3.9_p':
        map_survey_data = call_data['map_survey']
        map_survey_header = 'Map survey'
    else:
        curr_game_data = call_data['games_data'][st.session_state.game_idx]
        map_idx = st.session_state.game_idx
        map_survey_data = curr_game_data['survey']
        map_survey_header = f'Game survey - map: {map_idx + 1}'

    survey_header = 'General survey:' if dash_key == 'general_survey' else map_survey_header
    survey_data = call_data['general_survey'] if dash_key == 'general_survey' else map_survey_data

    with mui.Paper(key=dash_key, sx={
        "display": 'flex',
        "flexDirection": 'column',
        "overflowY": 'auto'}):
        html.p(f'{survey_header}', css={'font-size': '18px', 'fontWeight': '700'})
        for qa in survey_data:
            html.div(
                html.p(f"Q: {qa['question']}", css={'margin': '0.5em'}),
                html.p(f"A: {qa['answer']}", css={'margin': '0.5em'}),
                css={
                    "display": "flex",
                    "flexDirection": 'column',
                    "width": 'fit-content',
                    'border-bottom': '1px solid gray',
                    'margin': '0.5em'
                },
            )


with elements("dashboard"):
    layout = [
        # Parameters: element_identifier, x_pos, y_pos, width, height, [item properties...]
        # https://react-grid-layout.github.io/react-grid-layout/examples/0-showcase.html
        dashboard.Item("general_survey", 0, 0, 4, 3, isDraggable=False, moved=False, isResizable=False),
        dashboard.Item("dialog", 4, 0, 6, 3, isDraggable=False, moved=False, isResizable=False),
        dashboard.Item("game_survey", 0, 6, 10, 3, isDraggable=False, moved=False, isResizable=False),
    ]

    with dashboard.Grid(layout):
        render_survey('general_survey')
        render_survey('game_survey')
        render_chat()
