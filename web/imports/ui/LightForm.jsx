import React, { useState, useCallback } from 'react';
import { Meteor } from 'meteor/meteor';
import classNames from 'classnames';
import {createUseStyles} from 'react-jss';
import { HuePicker, AlphaPicker } from 'react-color';
import tinycolor from 'tinycolor2';
import { debounce } from 'lodash';

import { COLOUR_MODES, ANIMATIONS } from '/imports/db/LightsCollection';

const useStyles = createUseStyles({
  activeButton: {
    color: 'red'
  }
});

export const LightForm = ({ light }) => {
  const classes = useStyles();

  // Only allow updates once every 0.2 seconds.
  const debounced = (func) => useCallback(debounce(func, 200, { maxWait: 200 }), [light]);
  const handleColourModeChange = debounced((colourMode) => {
    Meteor.call('lights.setColourMode', light._id, colourMode);
  })
  const handleHueChange = debounced(({ hsv }) => {
    const hue = hsv.h / 360;
    Meteor.call('lights.setColourHue', light._id, hue);
  });
  const handleSaturationChange = debounced(({ hsv }) => {
    Meteor.call('lights.setColourSaturation', light._id, hsv.a);
  });
  const handleAnimationChange = debounced((animation) => {
    Meteor.call('lights.setAnimation', light._id, animation);
  })

  if (!light) {
    return <div>Select a light!</div>
  }

  const colour = tinycolor.fromRatio({
    h: light['colourHue'],
    s: 1,
    v: 1,
    a: light['colourSaturation'],
  }).toHex8String();

  return (
    <div>
      <div className="colour-modes">
        {COLOUR_MODES.map((colourMode) => (
          <button
            key={colourMode}
            value={colourMode}
            className={classNames({
              [classes.activeButton]: (light.colourMode === colourMode)
            })}
            onClick={() => handleColourModeChange(colourMode)}
          >
            {colourMode}
          </button>
        ))}
      </div>
      {light.colourMode == 'colour' &&
       <div className="colour-pickers">
         <HuePicker color={colour} onChange={handleHueChange}></HuePicker>
         <AlphaPicker color={colour} onChange={handleSaturationChange}></AlphaPicker>
       </div>
      }
      <div className="animations">
        {ANIMATIONS.map((animation) => (
          <button
            key={animation}
            value={animation}
            className={classNames({
              [classes.activeButton]: (light.animation === animation)
            })}
            onClick={() => handleAnimationChange(animation)}
          >
            {animation}
          </button>
        ))}
      </div>
    </div>
  )
}
