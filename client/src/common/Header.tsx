import React from 'react';
import './Header.css';

function Header(): JSX.Element {
    return (
        <div className="Header">
            <div className="icons">
                <img className="edu_logo" src={'edu_logo.png'} />
                <img className="pit_logo" src={'pit_logo.jpg'} />
            </div>
            <div className="icons">
                <img className="clg_logo" src={'clg_logo.jpg'} />
                <img className="haifa_logo" src={'haifa_logo.jpg'} />
            </div>
        </div>
    );
}

export default Header;
