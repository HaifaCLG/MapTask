import React from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Slide } from '@material-ui/core';
import { useContext } from 'react';
import { TransitionProps } from '@material-ui/core/transitions';
import { AppContext } from '../AppContext';
import { useApp } from './useApp';

const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
        children: React.ReactElement<any, any>;
    },
    ref: React.Ref<unknown>,
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

function GameEndDialog(): JSX.Element {
    const { state } = useContext(AppContext);
    const { navigate_to_end_page } = useApp();
    const game = state.games[state.curr_game];

    return (
        <>
            <Dialog
                open={game.game_state.end}
                TransitionComponent={Transition as any}
                keepMounted
                // onClose={navigate_to_end_page}
            >
                <DialogTitle>{game.game_state.end_modal_title}</DialogTitle>
                <DialogContent>
                    <DialogContentText>{game.game_state.end_modal_text}</DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button
                        style={{ textTransform: 'none' }}
                        variant="outlined"
                        color="primary"
                        onClick={navigate_to_end_page}
                    >
                        Next
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}

export default GameEndDialog;
