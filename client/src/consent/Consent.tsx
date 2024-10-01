import React, { useContext } from 'react';
import { Box, Button, CircularProgress, Typography } from '@material-ui/core';
import { AppContext } from '../AppContext';
import { useNavigate } from 'react-router-dom';
import Header from '../common/Header';
import { main_blue } from '../common/colors';
import { useRegister } from '../useRegister';
import './Consent.css';

const consent_txt1 =
    'The purpose of this research study is to better understand the linguistic properties of written, online conversations. For this reason, we will be asking participants to complete a Map Task that involves giving directions to a conversational partner via a chat interface followed by a language history questionnaire  (30 minutes, computed as 5-7 minutes per game times 4 games) and exit survey (5-10 minutes). There are no foreseeable risks associated with this project, nor are there any direct benefits to you. However, your participation will allow researchers to better understand how language is used in an informal, written, online setting.';
const consent_txt2 = `If you choose to participate, your data will be associated only with your Prolific ID, not your real name, making it difficult to link your responses back to you. If you complete the study (i.e. all 4 maps), you will be paid £6, corresponding to £9.00/hour for the 40 minutes we anticipate the full study to take. Your participation is voluntary, and you may withdraw from the study at any time by simply closing your browser window. If you decide to withdraw after you have submitted responses, your responses will be retained by the researchers along with all other data associated with this project. This study is being conducted by Dr. Shuly Wintner (shuly@cs.haifa.ac.il) and Dr. Melinda Fricke (melinda.fricke@pitt.edu), who can be reached by email if you have any questions.`;

function Conset(): JSX.Element {
    const { state, setState } = useContext(AppContext);
    const [isProlific, setIsProlific] = React.useState(false);
    const { register_game } = useRegister();
    const navigate = useNavigate();

    React.useEffect(() => {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const prolific_id = urlParams.get('PROLIFIC_PID');
        const study_id = urlParams.get('STUDY_ID');
        const seassion_id = urlParams.get('SESSION_ID');

        if (!prolific_id || !study_id || !seassion_id) return;

        setIsProlific(true);

        if (state.registerd === 'yes') return;
        register_game({ prolific_id, study_id, seassion_id });
    }, []);

    const onClick = () => {
        setState({ ...state, consent: true });
        navigate('/map_task');
    };

    const redner_conset = (ready: boolean) => {
        return (
            <>
                <div>
                    <h6 className="consentText">
                        {consent_txt1} <br /> <br /> {consent_txt2} <br /> <br />
                    </h6>
                    <p className="consentText" style={{ fontWeight: 700 }}>
                        Please do not refresh the page as progress will be lost.
                    </p>
                </div>
                {ready ? (
                    <Button
                        className="register_btn"
                        style={{ textTransform: 'none' }}
                        variant="outlined"
                        color="primary"
                        onClick={() => onClick()}
                    >
                        Accept and Begin
                    </Button>
                ) : (
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            margin: '32px',
                            justifyContent: 'center',
                            alignItems: 'center',
                        }}
                    >
                        <CircularProgress style={{ color: main_blue, width: '30px', height: '30px' }} />
                        <p className="" style={{ fontWeight: 700, color: main_blue }}>
                            Loading the experiment, this might take a few seconds...
                        </p>
                    </Box>
                )}
            </>
        );
    };

    return (
        <div className="conset">
            <Header />
            <div className="conset_container">
                {!isProlific && (
                    <div style={{ fontSize: '18px', fontWeight: 700 }}>
                        <p>No Prolific id found!</p>
                        <p>Please return to Prolific and try again.</p>
                    </div>
                )}
                {state.registerd === 'err' && (
                    <Typography variant="h5" style={{ margin: '16px' }}>
                        An errur occured, please try again later
                    </Typography>
                )}
                {state.registerd === 'yes' && redner_conset(true)}
                {state.registerd === 'load' && redner_conset(false)}
            </div>
        </div>
    );
}

export default Conset;
