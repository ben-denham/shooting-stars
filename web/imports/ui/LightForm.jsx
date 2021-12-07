import React, { useState, useCallback } from 'react';
import { Meteor } from 'meteor/meteor';
import classNames from 'classnames';
import {createUseStyles} from 'react-jss';
import { HuePicker, AlphaPicker } from 'react-color';
import tinycolor from 'tinycolor2';
import { debounce } from 'lodash';

import { COLOUR_MODES, ANIMATIONS } from '/imports/db/LightsCollection';
import { LightButton } from './LightButton';

const candycaneStripeImage = '/images/candycane-stripe.png';
const candycaneStripeSquareImage = '/images/candycane-stripe-square.png';
const smallLightsImage = '/images/small-lights.png';

const useStyles = createUseStyles({
  lightForm: {
    position: 'relative',
  },
  emptyMessage: {
    fontFamily: 'Courgette',
    fontSize: '24px',
    marginTop: '20px'
  },
  closeButton: {
    position: 'sticky',
    top: 0,
    left: 0,
    zIndex: 1,
    width: '100%',
    height: '25px',
    border: 0,
    padding: 0,
    background: '#555555',
    boxShadow: '0 0 5px 2px #555555',
    cursor: 'pointer',
    '&:focus': {
      outline: 'none',
      boxShadow: '0 0 5px 2px white',
    }
  },
  closeArrow: {
    position: 'relative',
    top: '-3px',
    border: 'solid white',
    borderWidth: '0 2px 2px 0',
    width: '10px',
    height: '10px',
    display: 'inline-block',
    transform: 'rotate(45deg)',
  },
  formElements: {
    margin: '35px auto 0 auto',
    maxWidth: '500px',
    width: '100%',
    maxWidth: '400px',
  },
  buttonRow: {
    display: 'flex',
    justifyContent: 'space-evenly',
  },
  buttonWrapper: {
    width: '18%',
    height: '18%',
    borderRadius: '6px',
    boxShadow: '0 0 5px 5px #555555',
    '& > button > *': {
      borderRadius: '6px'
    }
  },
  invisible: {
    visibility: 'hidden',
  },
  pickers: {
    margin: '20px 0 30px 0',
  },
  picker: ({ displayColour }) => ({
    margin: '25px auto',
    cursor: 'pointer',
    width: '100%',
    '& > div > div > div > div': {
      position: 'relative',
      top: '-3px',
      border: '3px solid black',
      boxShadow: '0 0 5px 2px #AAAAAA !important'
    }
  }),
  huePicker: ({ hueColour }) => ({
    '& > div > div > div > div': {
      background: `${hueColour} !important`,
    }
  }),
  saturationPicker: ({ saturationColour}) => ({
    '& > div > div > div > div': {
      background: `${saturationColour} !important`,
    },
    '& > div > div:first-child > div': {
      background: 'white !important'
    }
  }),
  links: {
    margin: '25px 0 10px 0',
    '& a': {
      fontSize: '0.8em',
      color: 'white',
      '&:visited': {
        color: 'white'
      }
    }
  }
});

export const LightForm = ({ light, setSelectedLightId, className }) => {
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
  const hueColour = tinycolor.fromRatio({
    h: light?.colourHue || 0,
    s: 1,
    v: 1,
    a: 1
  }).toHexString();
  const saturationColour = tinycolor.fromRatio({
    h: light?.colourHue || 0,
    s: light?.colourSaturation || 0,
    v: 1,
    a: 1
  }).toHexString();
  const classes = useStyles({ hueColour, saturationColour });

  return (
    <div className={classNames(className, classes.lightForm)}>
      {!light && (
        <div className={classes.emptyMessage}>
          Select a light to change!
        </div>
      )}
      {light && (
        <>
          <button
            className={classes.closeButton}
            onClick={() => setSelectedLightId(null)}
          >
            <div className={classes.closeArrow}></div>
          </button>
          <div className={classes.formElements}>
            <div className={classes.buttonRow}>
              {COLOUR_MODES.map((colourMode) => (
                <div className={classes.buttonWrapper} key={colourMode}>
                  <LightButton
                    light={{...light, colourMode: colourMode, animation: 'static'}}
                    onClick={() => handleColourModeChange(colourMode)}
                    isSelected={light.colourMode === colourMode}
                    selectedStyle={{
                      borderStyle: 'solid',
                      borderWidth: '6px',
                      borderImage: `url(${candycaneStripeImage})`,
                      borderImageRepeat: 'round',
                      borderImageSlice: 50,
                    }}
                    image={smallLightsImage}
                  />
                </div>
              ))}
            </div>
            <div className={classNames({[classes.pickers]: true, [classes.invisible]: light?.colourMode != 'colour'})}>
              <HuePicker
                className={classNames(classes.picker, classes.huePicker)}
                color={pickerColour}
                onChange={handleHueChange}
                width='80%'
              />
              <AlphaPicker
                className={classNames(classes.picker, classes.saturationPicker)}
                color={pickerColour}
                onChange={handleSaturationChange}
                width='80%'
              />
            </div>
            <div className={classes.buttonRow}>
              {ANIMATIONS.map((animation) => (
                <div className={classes.buttonWrapper} key={animation}>
                  <LightButton
                    light={{colourMode: 'colour', colourHue: 0, colourSaturation: 0, animation: animation}}
                    onClick={() => handleAnimationChange(animation)}
                    isSelected={light.animation === animation}
                    selectedStyle={{
                      borderStyle: 'solid',
                      borderWidth: '6px',
                      borderImage: `url(${candycaneStripeImage})`,
                      borderImageRepeat: 'round',
                      borderImageSlice: 50,
                    }}
                    image={smallLightsImage}
                  />
                </div>
              ))}
            </div>
          </div>
        </>
      )}
      <div className={classes.links}>
        <a href="https://github.com/ben-denham/shooting-stars">Source Code on GitHub</a>
      </div>
    </div>
  );
}
