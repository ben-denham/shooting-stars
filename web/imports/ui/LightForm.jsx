import React, { useState, useCallback } from 'react';
import { Meteor } from 'meteor/meteor';
import classNames from 'classnames';
import {createUseStyles} from 'react-jss';
import { HuePicker, AlphaPicker } from 'react-color';
import tinycolor from 'tinycolor2';
import { debounce } from 'lodash';

import { COLOUR_MODES, ANIMATIONS } from '/imports/db/LightsCollection';

const candycaneStripeSquareImage = '/images/candycane-stripe-square.png';

const useStyles = createUseStyles({
  lightForm: {
    position: 'relative',
    border: '12px solid transparent',
    borderImage: `url(${candycaneStripeSquareImage})`,
    borderImageRepeat: 'round',
    borderImageSlice: 50
  },
  emptyMessage: {
    position: 'absolute',
    width: '100%',
    paddingTop: '20px',
  },
  button: {
    margin: '20px 20px !important'
  },
  activeButton: {
    color: 'red'
  },
  invisible: {
    visibility: 'hidden',
  },
  picker: {
    margin: '30px auto',
    maxWidth: '80%',
  },
  links: {
    '& a': {
      color: 'white',
      '&:visited': {
        color: 'white'
      }
    }
  }
});

export const LightForm = ({ light, className }) => {
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

  const pickerColour = tinycolor.fromRatio({
    h: light?.colourHue || 0,
    s: 1,
    v: 1,
    a: light?.colourSaturation || 0,
  }).toHex8String();

  return (
    <div className={classNames(className, classes.lightForm)}>
      <div className={classNames({[classes.emptyMessage]: true, [classes.invisible]: light})}>
        Select a light!
      </div>
      <div className={classNames({[classes.invisible]: !light})}>
        <div>
          {COLOUR_MODES.map((colourMode) => (
            <button
              key={colourMode}
              value={colourMode}
              className={classNames({
                [classes.button]: true,
                [classes.activeButton]: (light?.colourMode === colourMode)
              })}
              onClick={() => handleColourModeChange(colourMode)}
            >
              {colourMode}
            </button>
          ))}
        </div>
        <div className={classNames({[classes.invisible]: light?.colourMode != 'colour'})}>
          <HuePicker className={classes.picker} color={pickerColour} onChange={handleHueChange}></HuePicker>
          <AlphaPicker className={classes.picker} style={{margin: 'auto'}} color={pickerColour} onChange={handleSaturationChange}></AlphaPicker>
        </div>
        <div>
          {ANIMATIONS.map((animation) => (
            <button
              key={animation}
              value={animation}
              className={classNames({
                [classes.button]: true,
                [classes.activeButton]: (light?.animation === animation)
              })}
              onClick={() => handleAnimationChange(animation)}
            >
              {animation}
            </button>
          ))}
        </div>
        <div className={classes.links}>
          <a href="https://github.com/ben-denham/shooting-stars">Source Code on GitHub</a>
        </div>
      </div>
    </div>
  )
}
