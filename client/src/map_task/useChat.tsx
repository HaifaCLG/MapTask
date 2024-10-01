import { useContext, useState } from 'react';
import { callBot } from '../api';
import { AppContext } from '../AppContext';
import { ChatMsg } from '../Wrapper';
import { hh_end_modal_str } from '../common/strings';

export function useChat() {
    const { state, setState } = useContext(AppContext);
    const [inputTxt, setInputTxt] = useState('');
    const [botType, setBotType] = useState(false);

    const updateChatState = (newMsg: ChatMsg[]) => {
        const games = [...state.games];
        const chat = games[state.curr_game].chat.concat(newMsg);
        games[state.curr_game].chat = chat;
        setState({ ...state, games: games });
    };

    const updateChatAndFinish = (newMsg: ChatMsg[], endModalText: string) => {
        const games = [...state.games];
        const game_state = games[state.curr_game].game_state;
        game_state.end = true;
        game_state.end_modal_text = endModalText;
        const chat = games[state.curr_game].chat.concat(newMsg);
        games[state.curr_game].chat = chat;
        setState({ ...state, games: games });
    };

    const sendUserMsg = () => {
        if (!inputTxt) return;
        const user_map_path = state.games[state.curr_game].user_map_path;
        const curr_cell = user_map_path[user_map_path.length - 1];

        const selfChatMsg: ChatMsg = {
            msg: inputTxt,
            id: state.games[state.curr_game].game_config.game_role,
            timestamp: Date.now(),
            curr_nav_cell: curr_cell,
        };

        updateChatState([selfChatMsg]);
        setInputTxt('');

        setBotType(true);
        callBot(
            state.games[state.curr_game].game_config.guid,
            inputTxt,
            curr_cell,
            state.games[state.curr_game].map_metadata.map_idx,
            state.games[state.curr_game].game_config.game_role,
            addBotMsg,
        );
    };

    const addBotMsg = (data: any) => {
        setBotType(false);

        const msgs: string[] = data.res;
        const is_finish = data.is_finish;
        const chatMsgs = msgs.map((msg) => ({
            msg: msg,
            id: 1 - state.games[state.curr_game].game_config.game_role,
            timestamp: Date.now(),
        }));

        if (chatMsgs[0].msg == 'Something went wrong, try again') {
            alert('Something went wrong, try again');
            return;
        }
        if (is_finish) updateChatAndFinish(chatMsgs, hh_end_modal_str);
        else updateChatState(chatMsgs);
    };

    const onKeyPress = (e: any) => {
        if (e.keyCode == 13) {
            sendUserMsg();
        }
    };

    return { updateChatState, onKeyPress, botType, sendUserMsg, inputTxt, setInputTxt };
}
