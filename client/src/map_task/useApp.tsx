import { useContext, useEffect } from 'react';
import { AppContext } from '../AppContext';
import { useNavigate } from 'react-router-dom';
import { finish_btn_modal_str } from '../common/strings';

export function useApp() {
    const { state, setState } = useContext(AppContext);
    const navigate = useNavigate();

    useEffect(() => {
        if (!state.consent) navigate('/');
    }, []);

    const open_ending_modal = (text: string) => {
        const games = [...state.games];

        const game_state = games[state.curr_game].game_state;
        game_state.end = true;
        game_state.end_modal_text = text;

        setState({ ...state, games });
    };

    const finish_early = () => {
        open_ending_modal(finish_btn_modal_str);
    };

    const navigate_to_end_page = () => {
        navigate('/next');
    };

    return { open_ending_modal, navigate_to_end_page, finish_early };
}
