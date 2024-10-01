import React, { useContext, useEffect } from 'react';
import { AppContext } from '../AppContext';
import { MapCellIdx } from '../Wrapper';
import { nav_end_model_str } from '../common/strings';
import MapCanvasNavBtns from './MapCanvasNavBtns';
import './MapCanvas.css';

export interface IMapCanvas {
    width: number;
    height: number;
}

//Note map 3 size is a bit smaller - its a instrcutor role in the allternations so it doesnt matter
const columns = 24;
const rows = 18;
const cells = columns * rows;

export interface ICell {
    text?: string;
    size: number;
    top: number;
    left: number;
}

export interface IPlayer {
    size: number;
    top: number;
    left: number;
    is_head: boolean;
}

// function Cell(props: ICell): JSX.Element {
//     return (
//         <div
//             className="map_cell"
//             style={{
//                 top: props.top,
//                 left: props.left,
//                 width: props.size,
//                 height: props.size,
//             }}
//         >
//             <p style={{ margin: 0, padding: 0 }}>{props.text}</p>
//         </div>
//     );
// }

function Player(props: IPlayer): JSX.Element {
    return (
        <div
            className="map_player"
            style={{
                top: props.top,
                left: props.left,
                width: props.size,
                height: props.size,
                opacity: props.is_head ? 0.8 : 0.6,
            }}
        ></div>
    );
}

const init_path: number[] = [];

function MapCanvas({ width, height }: IMapCanvas): JSX.Element {
    const { state, setState } = useContext(AppContext);
    const [path, setPath] = React.useState(init_path);

    const game = state.games[state.curr_game];
    const role = game.game_config.game_role == 1 ? 'ins' : 'nav';
    const map_id = `map${state.curr_game}_${role}`;

    useEffect(() => {
        if (game.game_state.end) return;
        if (!state.consent) return;
        const start_player_idx = cell_idx_to_flat_idx(game.map_metadata.start_cell);

        if (role == 'nav') setPath([start_player_idx]);
    }, []);

    const col_step = width / columns;
    const row_step = height / rows;

    const render_size = Math.min(col_step, row_step);
    const min_step = Math.min(col_step, row_step);

    const flat_idx_to_pos = (idx: number) => {
        const x_idx = idx % columns;
        const y_idx = Math.floor(idx / columns);

        let left = min_step * x_idx;
        let top = height - min_step * (rows - y_idx);

        const spare_size = Math.max(col_step, row_step) - min_step;

        if (row_step > col_step) top -= (spare_size * rows) / 2;
        else left += (spare_size * columns) / 2;

        return {
            left,
            top,
        };
    };

    const cell_idx_to_flat_idx = (cell: MapCellIdx) => {
        return cell.r * columns + cell.c;
    };

    const flat_idx_to_map_cell_idx = (idx: number): MapCellIdx => {
        const x_idx = idx % columns;
        const y_idx = Math.floor(idx / columns);
        return { r: y_idx, c: x_idx };
    };

    const is_finish = (cell: MapCellIdx): boolean => {
        return (
            Math.sqrt((cell.r - game.map_metadata.end_cell.r) ** 2 + (cell.c - game.map_metadata.end_cell.c) ** 2) < 2
        );
    };

    const on_nav_click = (delta: number) => {
        if (role === 'ins') return;

        const head_index = path[path.length - 1];
        const new_index = head_index + delta;

        if (delta == 1 && head_index % columns == columns - 1) {
            return;
        }
        if (delta == -1 && head_index % columns == 0) {
            return;
        }
        if (new_index < 0 || new_index >= cells) {
            return;
        }
        const new_path = [...path, new_index];
        setPath(new_path);

        const user_path = new_path.map((cell_flat_idx) => flat_idx_to_map_cell_idx(cell_flat_idx));
        const games = [...state.games];
        games[state.curr_game].user_map_path = user_path;

        if (is_finish(flat_idx_to_map_cell_idx(new_index))) {
            const game_state = games[state.curr_game].game_state;
            game_state.end = true;
            game_state.end_modal_text = nav_end_model_str;
        }
        setState({ ...state, games: games });
    };

    const onKeyboard = (e: any) => {
        e.preventDefault();
        if (e.keyCode == 37) {
            on_nav_click(-1);
        } else if (e.keyCode == 39) {
            on_nav_click(1);
        } else if (e.keyCode == 40) {
            on_nav_click(columns);
        } else if (e.keyCode == 38) {
            on_nav_click(-columns);
        } else {
            return;
        }
    };

    // const cell_pos = [...Array(cells).keys()].map((_, index) => {
    //     return flat_idx_to_pos(index);
    // });

    const render = () => {
        return (
            <div
                tabIndex={0}
                id={map_id}
                className="map_container"
                style={{ width: width, height: height }}
                onKeyDown={onKeyboard}
            >
                {/* {cell_pos.map((cell, index) => (
                    <Cell key={index} size={render_size} top={cell.top} left={cell.left} text={index.toString()} />
                ))} */}

                {path.map((cell_flat_idx, index) => {
                    const cell = flat_idx_to_pos(cell_flat_idx);
                    return (
                        <Player
                            key={index}
                            size={render_size}
                            top={cell.top}
                            left={cell.left}
                            is_head={index === path.length - 1}
                        />
                    );
                })}
                {role === 'nav' && <MapCanvasNavBtns btn_size={render_size} columns={columns} onClick={on_nav_click} />}
            </div>
        );
    };

    return render();
}

export default MapCanvas;
