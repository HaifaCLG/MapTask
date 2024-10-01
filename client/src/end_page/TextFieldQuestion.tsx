import React from 'react';
import { TextField } from '@material-ui/core';
import { Typography } from '@material-ui/core';
import { useContext } from 'react';
import { AppContext } from '../AppContext';
import { IQuestionInterface } from '../Wrapper';

function TextFieldQuestion(data: IQuestionInterface): JSX.Element {
    const { state, setState } = useContext(AppContext);
    const survey = data.survey === 'general' ? state.general_survey : state.map_survey;

    const simple_set = (e: any) => {
        survey[data.id].answer = e.target.value.toString();
        if (data.survey === 'general') setState({ ...state, general_survey: survey });
        else setState({ ...state, map_survey: survey });
    };

    return (
        <div className="QuestionGroup">
            <div style={{ width: '50%', display: 'flex', flexDirection: 'column' }}>
                <Typography component="legend" align="left">
                    {data.meta.question}
                </Typography>
                {data.meta.questionCont ? (
                    <Typography variant="caption" align="left">
                        {data.meta.questionCont}
                    </Typography>
                ) : null}
            </div>

            <TextField
                style={{ width: '50%' }}
                id={data.id}
                label="type here"
                variant="outlined"
                onChange={(event) => simple_set(event)}
                type={data.meta.numberText ? 'number' : undefined}
                InputProps={{
                    inputProps: { min: 0 },
                }}
                value={survey[data.id].answer}
                required
            />
        </div>
    );
}

export default TextFieldQuestion;
