import React, { useEffect, useState } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Slide } from '@material-ui/core';
import { useContext } from 'react';
import { TransitionProps } from '@material-ui/core/transitions';
import { AppContext } from '../AppContext';
import { useGameInstructions } from './useGameInstructions';
import { ins_sub_title_str, ins_instructions_str } from './strings';
import { role_strings } from '../Wrapper';

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
        children: React.ReactElement<any, any>;
    },
    ref: React.Ref<unknown>,
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

function GameInstructionsDialog({}): JSX.Element {
    const { state } = useContext(AppContext);
    const [im, setIm] = useState<HTMLImageElement>();
    const { setGameInstructions } = useGameInstructions();
    const game = state.games[state.curr_game];

    const role_string = role_strings[state.games[state.curr_game].game_config.game_role];

    useEffect(() => {
        const image = new Image();
        image.onload = function () {
            setIm(image);
        };
        image.onerror = function (err) {
            console.log('img load err', err);
        };

        let img_map_name = '';
        if (game.game_config.game_role == 1) img_map_name = game.map_metadata.im_src;
        else {
            const prefix = game.map_metadata.im_src.split('_')[0];
            img_map_name = prefix + '_0_nav.jpg';
        }

        image.src = require(`../map_task/maps/${img_map_name}`);
    }, []);

    return (
        <>
            <Dialog
                open={state.open_instructions}
                TransitionComponent={Transition as any}
                keepMounted
                onClose={() => setGameInstructions(false)}
            >
                <DialogTitle style={{ fontSize: '1.5rem' }}>
                    Game instructions, your role is the {role_string}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText style={{ fontSize: '1.25rem' }}>{ins_sub_title_str}</DialogContentText>
                    {ins_instructions_str.map((e, idx) => (
                        <DialogContentText key={idx}>{e}</DialogContentText>
                    ))}

                    <img
                        src={im?.src}
                        width={game.map_metadata.im_width / 5}
                        height={game.map_metadata.im_height / 5}
                    />
                </DialogContent>
                <DialogActions>
                    <Button
                        style={{ textTransform: 'none' }}
                        variant="outlined"
                        color="primary"
                        onClick={() => setGameInstructions(false)}
                    >
                        Ok
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}

export default GameInstructionsDialog;
