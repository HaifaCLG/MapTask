import React, { useContext, useEffect } from 'react';
import { AppContext } from '../AppContext';
import { Box, CircularProgress, IconButton, List, ListItem, TextField } from '@material-ui/core';
import SendIcon from '@material-ui/icons/Send';
import { useChat } from './useChat';
import { main_blue, main_gray } from '../common/colors';
import './Chat.css';

function Chat(): JSX.Element {
    const { state } = useContext(AppContext);
    const { botType, onKeyPress, sendUserMsg, inputTxt, setInputTxt } = useChat();
    const game_role = state.games[state.curr_game].game_config.game_role;

    useEffect(() => {
        const cc = document.getElementById('chat_list');
        if (!cc) return;
        cc.scrollTo({
            top: cc.scrollHeight,
            behavior: 'smooth',
        });
    }, [state.games[state.curr_game].chat]);

    return (
        <div className="chat_container">
            <List id="chat_list" style={{ height: '90%', overflowY: 'auto' }}>
                {state.games[state.curr_game].chat.map(function (c, idx) {
                    const direction = c.id != game_role ? 'row' : 'row-reverse';
                    const color = c.id != game_role ? main_gray : main_blue;

                    return (
                        <ListItem key={idx}>
                            <div style={{ display: 'flex', flexDirection: direction, width: '100%' }}>
                                <span
                                    style={{
                                        color: 'white',
                                        backgroundColor: color,
                                        borderRadius: '8px',
                                        padding: '8px',
                                        fontSize: '18px',
                                    }}
                                >
                                    {c.msg}
                                </span>
                            </div>
                        </ListItem>
                    );
                })}
                {botType ? (
                    <Box sx={{ display: 'flex', marginLeft: '16px' }}>
                        <CircularProgress style={{ color: main_gray, width: '30px', height: '30px' }} />
                    </Box>
                ) : null}
            </List>

            <div className="input_panel">
                <TextField
                    style={{ width: '90%' }}
                    variant="outlined"
                    value={inputTxt}
                    placeholder={'Type here'}
                    onChange={(e) => setInputTxt(e.target.value)}
                    onKeyDown={(e) => onKeyPress(e)}
                />
                <IconButton color="primary" size="medium" onClick={sendUserMsg}>
                    <SendIcon />
                </IconButton>
            </div>
        </div>
    );
}

export default Chat;
