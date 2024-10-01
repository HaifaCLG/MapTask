import React, { useState } from 'react';
import { Box, Button, CircularProgress } from '@material-ui/core';
import { Typography } from '@material-ui/core';
import { useContext } from 'react';
import { AppContext } from '../AppContext';
import Header from '../common/Header';
import {
    end_page_title1_str,
    end_page_group_4_str,
    end_page_group_5_str,
    end_page_group_6_str,
    end_page_group_7_str,
    end_page_group_8_str,
    end_page_group_5_subtitle,
} from '../common/strings';
import RatingQuestion from './RatingQuestion';
import TextFieldQuestion from './TextFieldQuestion';
import SelectQuestion from './SelectQuestion';
import { useNavigate } from 'react-router-dom';
import { upload } from '../api';
import { main_blue } from '../common/colors';

import './EndPage.css';

function SurveyGeneral(): JSX.Element {
    const { state, setState } = useContext(AppContext);
    const navigate = useNavigate();
    const [currGroup, SetCurrGroup] = useState(0);
    const [reg, SetReg] = useState('not_sent');

    React.useEffect(() => {
        if (!state.consent) navigate('/');
        if (state.uploaded) {
            SetReg('done');
        }
    }, []);

    const survey_groups: string[][] = [];
    const survey_groups_titles: string[] = [
        end_page_group_4_str,
        end_page_group_5_str,
        end_page_group_6_str,
        end_page_group_7_str,
        end_page_group_8_str,
    ];

    const survey_groups_subtitles: string[] = ['', end_page_group_5_subtitle, '', ''];

    survey_groups.push(Object.keys(state.general_survey).slice(0, 9));
    survey_groups.push(Object.keys(state.general_survey).slice(9, 19));
    survey_groups.push(Object.keys(state.general_survey).slice(19, 31));
    survey_groups.push(Object.keys(state.general_survey).slice(31, 32));
    survey_groups.push(Object.keys(state.general_survey).slice(32, 50));

    const scroll_begin = () => {
        const tr = document.getElementById('container');
        if (!tr) return;
        tr.scrollTo({
            top: 0,
            behavior: 'smooth',
        });
    };

    const onUploadFinish = (success: boolean) => {
        if (success) {
            SetReg('done');
            setState({ ...state, uploaded: true });
            window.open('https://app.prolific.co/submissions/complete?cc=C15G3HZJ');
        } else {
            SetReg('fail');
        }
    };

    const next = () => {
        scroll_begin();
        if (currGroup == survey_groups.length - 1) {
            upload(state, onUploadFinish);
            SetReg('loading');
        } else {
            SetCurrGroup(currGroup + 1);
        }
    };

    const back = () => {
        scroll_begin();
        if (currGroup == 0) return;
        SetCurrGroup(currGroup - 1);
    };

    const is_valid = () => {
        const curr_questions_keys = survey_groups[currGroup];
        for (let i = 0; i < curr_questions_keys.length; i++) {
            const key = curr_questions_keys[i];
            if (state.general_survey[key].answer === '') {
                return false;
            }
        }
        return true;
    };

    return (
        <div className="End">
            <Header />
            <div className="End_Container" id="container">
                {reg == 'not_sent' ? (
                    <>
                        <Typography style={{ marginTop: '16px' }} variant="h4">
                            {end_page_title1_str}
                        </Typography>
                        <div className="Group">
                            <Typography variant="h5">{survey_groups_titles[currGroup]}</Typography>
                            <Typography variant="h6" style={{ marginBottom: '32px', fontSize: '16px' }}>
                                {survey_groups_subtitles[currGroup]}
                            </Typography>
                            {survey_groups[currGroup].map(function (key) {
                                const t = state.general_survey[key].type;
                                if (t == 'rating')
                                    return (
                                        <RatingQuestion
                                            meta={state.general_survey[key]}
                                            id={key}
                                            key={key}
                                            survey="general"
                                        />
                                    );
                                else if (t == 'textfield')
                                    return (
                                        <TextFieldQuestion
                                            meta={state.general_survey[key]}
                                            id={key}
                                            key={key}
                                            survey="general"
                                        />
                                    );
                                else if (t == 'select')
                                    return (
                                        <SelectQuestion
                                            meta={state.general_survey[key]}
                                            id={key}
                                            key={key}
                                            survey="general"
                                        />
                                    );
                            })}
                        </div>
                        <div style={{ display: 'flex', width: '100%', justifyContent: 'space-between' }}>
                            <Button
                                disabled={currGroup == 0}
                                style={{
                                    textTransform: 'none',
                                    marginLeft: '16px',
                                    marginBottom: '16px',
                                }}
                                className="nav_btn"
                                variant="outlined"
                                color="primary"
                                onClick={back}
                            >
                                Back
                            </Button>
                            <Button
                                style={{
                                    textTransform: 'none',
                                    marginRight: '16px',
                                    marginBottom: '16px',
                                }}
                                variant="outlined"
                                color="primary"
                                onClick={next}
                                disabled={!is_valid()}
                            >
                                {currGroup == survey_groups.length - 1 ? 'Finish' : 'Next'}
                            </Button>
                        </div>
                    </>
                ) : null}
                {reg == 'loading' ? (
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            marginTop: '25%',
                            justifyContent: 'center',
                            alignItems: 'center',
                        }}
                    >
                        <CircularProgress style={{ color: main_blue, width: '30px', height: '30px' }} />
                        <Typography style={{ marginTop: '1em' }} variant="h5">
                            Please wait, this might take some time. <br /> You will be redirected to Prolific when done.{' '}
                            <br /> In case you are not redirected, please click the button again.
                        </Typography>
                        <p className="consentText" style={{ fontWeight: 700 }}>
                            Please do not refresh the page as progress will be lost.
                        </p>{' '}
                    </Box>
                ) : null}
                {reg == 'done' ? (
                    <Typography style={{ marginTop: '25%' }} variant="h4">
                        Thank you! <br /> <br /> Prolific completion code: C15G3HZJ
                    </Typography>
                ) : null}
                {reg == 'fail' ? (
                    <Box sx={{ display: 'flex', marginTop: '25%', flexDirection: 'column' }}>
                        <Button
                            style={{
                                textTransform: 'none',
                                fontSize: '20px',
                            }}
                            className="nav_btn"
                            variant="outlined"
                            color="primary"
                            onClick={() => {
                                SetReg('loading');
                                upload(state, onUploadFinish);
                            }}
                        >
                            {' '}
                            Please Click Here Again To Finish
                        </Button>
                        <p className="consentText" style={{ fontWeight: 700 }}>
                            Please do not refresh the page as progress will be lost.
                        </p>{' '}
                    </Box>
                ) : null}
            </div>
        </div>
    );
}

export default SurveyGeneral;
