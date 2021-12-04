import React, { useState } from 'react';
import classNames from 'classnames';
import {createUseStyles} from 'react-jss';
import { Meteor } from 'meteor/meteor';

const useStyles = createUseStyles({
  activeButton: {
    color: 'red'
  }
});

const COLOUR_MODE_CONFIGS = [
  {
    colourMode: 'white',
  },
  {
    colourMode: 'colour',
  },
  {
    colourMode: 'rainbow',
  },
];

export const LightForm = ({ light }) => {
  const classes = useStyles();

  return (
    <div>
      {!light &&
       <span>Select a light!</span>}
      {light &&
       <div>
         {COLOUR_MODE_CONFIGS.map((modeConfig) => (
           <button
             key={modeConfig.colourMode}
             className={classNames({
               [classes.activeButton]: (light.colourMode === modeConfig.colourMode)
             })}
             onClick={() => Meteor.call('lights.setColourMode', light._id, modeConfig.colourMode)}
           >
             {modeConfig.colourMode}
           </button>
         ))}
       </div>}
    </div>
  )
}
