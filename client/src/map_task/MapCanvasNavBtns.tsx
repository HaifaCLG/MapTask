import React from 'react';
import { IconButton } from '@material-ui/core';

import ArrowLeftIcon from '@material-ui/icons/ArrowLeft';
import ArrowRightIcon from '@material-ui/icons/ArrowRight';
import ArrowDropUpIcon from '@material-ui/icons/ArrowDropUp';
import ArrowDropDownIcon from '@material-ui/icons/ArrowDropDown';
import './MapCanvas.css';

export interface ImapLetter {
    btn_size: number;
    onClick: (step: number) => void;
    columns: number;
}

function MapCanvasNavBtns(props: ImapLetter): JSX.Element {
    const onUp = () => {
        props.onClick(-props.columns);
    };
    const onDown = () => {
        props.onClick(props.columns);
    };
    const onLeft = () => {
        props.onClick(-1);
    };
    const onRight = () => {
        props.onClick(1);
    };

    const icon_style = {
        zoom: 1,
        // backgroundColor: 'white',
    };

    return (
        <div
            className="map_nav_buttons"
            style={{
                width: props.btn_size * 3,
                height: props.btn_size * 3,
            }}
        >
            <div className="map_nav_btn_row">
                <IconButton color="inherit" size="medium" onClick={onUp} style={{ background: '#64e3f3' }}>
                    <ArrowDropUpIcon style={icon_style} />
                </IconButton>
            </div>
            <div className="map_nav_btn_row" id={'middle_row'}>
                <IconButton color="primary" size="medium" onClick={onLeft} style={{ background: '#64e3f3' }}>
                    <ArrowLeftIcon style={icon_style} />
                </IconButton>
                <IconButton color="primary" size="medium" onClick={onRight} style={{ background: '#64e3f3' }}>
                    <ArrowRightIcon style={icon_style} />
                </IconButton>
            </div>
            <div className="map_nav_btn_row">
                <IconButton color="primary" size="medium" onClick={onDown} style={{ background: '#64e3f3' }}>
                    <ArrowDropDownIcon style={icon_style} />
                </IconButton>
            </div>
        </div>
    );
}

export default MapCanvasNavBtns;
