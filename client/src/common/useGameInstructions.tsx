import { useContext } from 'react';
import { AppContext } from '../AppContext';

export function useGameInstructions() {
    const { state, setState } = useContext(AppContext);

    const setGameInstructions = (val: boolean) => {
        const games = [...state.games];
        const game_state = games[state.curr_game].game_state;
        game_state.started = true;
        setState({ ...state, games: games, open_instructions: val });
    };

    return { setGameInstructions };
}
