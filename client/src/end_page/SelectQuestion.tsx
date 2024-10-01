import React from 'react';
import { MenuItem, TextField } from '@material-ui/core';
import { Typography } from '@material-ui/core';
import { useContext } from 'react';
import { AppContext } from '../AppContext';
import { IQuestionInterface } from '../Wrapper';

function SelectQuestion(data: IQuestionInterface): JSX.Element {
    const { state, setState } = useContext(AppContext);
    const survey = data.survey === 'general' ? state.general_survey : state.map_survey;

    const simple_set = (e: any) => {
        survey[data.id].answer = e.target.value.toString();
        if (data.survey === 'general') setState({ ...state, general_survey: survey });
        else setState({ ...state, map_survey: survey });
    };

    return (
        <div className="QuestionGroup">
            <Typography style={{ width: '50%' }} component="legend" align="left">
                {data.meta.question}
            </Typography>
            <TextField
                style={{ width: '50%' }}
                onChange={(event) => simple_set(event)}
                id={data.id}
                select
                label="Select"
                value={survey[data.id].answer}
            >
                {data.meta.selectOptions!.map((option) => (
                    <MenuItem key={option} value={option}>
                        {option}
                    </MenuItem>
                ))}
            </TextField>
        </div>
    );
}

export default SelectQuestion;
