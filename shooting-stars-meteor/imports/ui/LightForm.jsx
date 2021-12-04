import React, { useState } from 'react';
import classNames from 'classnames';
import {createUseStyles} from 'react-jss';

const useStyles = createUseStyles({
  activeButton: {
    color: 'red'
  }
});

const COLOUR_MODE_CONFIGS = [
  {
    mode: 'white',
  },
  {
    mode: 'colour',
  },
  {
    mode: 'rainbow',
  },
];

export const LightForm = ({ light, updateLight }) => {
  const classes = useStyles();

  return (
    <div>
      {!light &&
       <span>Select a light!</span>}
      {light &&
       <div>
         {COLOUR_MODE_CONFIGS.map((modeConfig) => (
           <button
             key={modeConfig.mode}
             className={classNames({
               [classes.activeButton]: (light.colourMode === modeConfig.mode)
             })}
             onClick={() => updateLight(light, {
                 colourMode: modeConfig.mode
               })}
           >
             {modeConfig.mode}
           </button>
         ))}
       </div>}
    </div>
  )
}
