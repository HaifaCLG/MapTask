import React, { useState } from 'react';
import { Button } from '@material-ui/core';
import { Typography } from '@material-ui/core';
import { useContext } from 'react';
import { AppContext } from '../AppContext';
import Header from '../common/Header';
import {
    end_page_group_1_str,
    end_page_title1_str,
    end_page_group_2_str,
    end_page_group_3_str,
} from '../common/strings';
import RatingQuestion from './RatingQuestion';
import TextFieldQuestion from './TextFieldQuestion';
import SelectQuestion from './SelectQuestion';
import { useNavigate } from 'react-router-dom';
import './EndPage.css';
import { maps } from '../Wrapper';

function SurveyMap(): JSX.Element {
    const navigate = useNavigate();
    const { state } = useContext(AppContext);
    const [currGroup, SetCurrGroup] = useState(0);

    React.useEffect(() => {
        if (!state.consent) navigate('/');
    }, []);

    const survey_groups: string[][] = [];
    const survey_groups_titles: string[] = [end_page_group_1_str, end_page_group_2_str, end_page_group_3_str];

    const map_survey = state.map_survey;

    survey_groups.push(Object.keys(map_survey).slice(0, 3));
    survey_groups.push(Object.keys(map_survey).slice(3, 12));
    survey_groups.push(Object.keys(map_survey).slice(12, 14));

    const scroll_begin = () => {
        const tr = document.getElementById('container');
        if (!tr) return;
        tr.scrollTo({
            top: 0,
            behavior: 'smooth',
        });
    };

    const is_valid = () => {
        const curr_questions_keys = survey_groups[currGroup];
        for (let i = 0; i < curr_questions_keys.length; i++) {
            const key = curr_questions_keys[i];
            if (state.map_survey[key].answer === '') {
                return false;
            }
        }
        return true;
    };

    const next = () => {
        scroll_begin();
        if (currGroup == survey_groups.length - 1) {
            navigate('/general_survey');
        } else {
            SetCurrGroup(currGroup + 1);
        }
    };

    const render_next_survey_btn = () => {
        if (currGroup === survey_groups.length - 1 && state.curr_game < maps.length - 1) return null;
        return (
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
                {'Next'}
            </Button>
        );
    };

    const back = () => {
        scroll_begin();
        if (currGroup == 0) return;
        SetCurrGroup(currGroup - 1);
    };

    return (
        <div className="End">
            <Header />
            {state.registerd === 'yes' && (
                <div className="End_Container" id="container">
                    <Typography style={{ marginTop: '16px' }} variant="h4">
                        {end_page_title1_str}
                    </Typography>
                    <div className="Group">
                        <Typography variant="h5" style={{ marginBottom: '32px' }}>
                            {survey_groups_titles[currGroup]}
                        </Typography>
                        {survey_groups[currGroup].map(function (key) {
                            if (map_survey[key].ignore) return null;
                            const t = map_survey[key].type;
                            if (t == 'rating')
                                return <RatingQuestion meta={map_survey[key]} id={key} key={key} survey="map" />;
                            else if (t == 'textfield')
                                return <TextFieldQuestion meta={map_survey[key]} id={key} key={key} survey="map" />;
                            else if (t == 'select')
                                return <SelectQuestion meta={map_survey[key]} id={key} key={key} survey="map" />;
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
                        <div>{render_next_survey_btn()}</div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default SurveyMap;
