import React, { useContext } from 'react';
import { Box, Button, CircularProgress } from '@material-ui/core';
import Header from '../common/Header';
import { useRegister } from '../useRegister';
import { main_blue } from './colors';
import { AppContext } from '../AppContext';
import { useNavigate } from 'react-router-dom';
import { maps } from '../Wrapper';

function Conset(): JSX.Element {
    const { create_new_game } = useRegister();
    const { state } = useContext(AppContext);
    const navigate = useNavigate();

    React.useEffect(() => {
        if (!state.consent) navigate('/');
    }, []);

    const next_btn = () => {
        if (state.curr_game < maps.length - 1) create_new_game();
        else navigate('/map_survey');
    };

    return (
        <div className="conset">
            <Header />
            <div className="conset_container">
                {state.registerd === 'load' ? (
                    <Box sx={{ display: 'flex', margin: '32px' }}>
                        <CircularProgress style={{ color: main_blue, width: '30px', height: '30px' }} />
                    </Box>
                ) : (
                    <Button
                        style={{
                            textTransform: 'none',
                            marginTop: '64px',
                            fontSize: '32px',
                        }}
                        variant="outlined"
                        color="primary"
                        onClick={next_btn}
                    >
                        {state.curr_game < maps.length - 1 ? 'Next Map' : 'Finish'}
                    </Button>
                )}
            </div>
        </div>
    );
}

export default Conset;
