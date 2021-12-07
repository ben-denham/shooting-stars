import React from 'react';
import {createUseStyles} from 'react-jss';
import classNames from 'classnames';
import tinycolor from 'tinycolor2';

const offColour = '#333333';
const maskOpacity = 0.9;

const useStyles = createUseStyles({
  '@keyframes gradualAnimation': {
    from: {
      filter: 'hue-rotate(0deg)'
    },
    to: {
      filter: 'hue-rotate(360deg)'
    }
  },
  '@keyframes twinkleAnimation': {
    '0%': {
      opacity: 0,
    },
    '49%': {
      opacity: 0,
    },
    '50%': {
      opacity: maskOpacity,
    },
    '99%': {
      opacity: maskOpacity
    },
    '100%': {
      opacity: 0
    }
  },
  '@keyframes rainAnimation': {
    '0%': {
      opacity: 0,
    },
    '75%': {
      opacity: maskOpacity
    },
    '100%': {
      opacity: maskOpacity
    },
  },
  '@keyframes waveAnimationSingle': {
    '0%': {
      marginLeft: '0%',
    },
    '50%': {
      marginLeft: '100%',
    },
    '50.0001%': {
      marginLeft: '-100%',
    },
    '100%': {
      marginLeft: '0%',
    },
  },
  // Assumes 10 lights, as variables don't work here here.
  '@keyframes waveAnimationTen': {
    '0%': {
      marginLeft: '0%',
    },
    '5%': {
      marginLeft: '100%',
    },
    '5.0001%': {
      marginLeft: '-100%',
    },
    '10%': {
      marginLeft: '0%',
    },
    '100%': {
      marginLeft: '0%',
    }
  },
  fullSize: {
    position: 'absolute',
    top: 0,
    left: 0,
    boxSizing: 'border-box',
    width: '100%',
    height: '100%',
  },
  button: {
    display: 'block',
    border: 0,
    padding: 0,
    margin: 0,
    '&:focus': {
      outline: 0,
      zIndex: 1,
      '& > $lightSelection': {
        boxShadow: '0px 0px 5px 2px white',
        borderRadius: '6px',
      }
    },
    cursor: 'pointer',
    position: 'relative',
    background: 'transparent',
    zIndex: 0
  },
  lightBackground: ({ lightBackground: { colour, animation } }) => ({
    extend: 'fullSize',
    zIndex: -20,
    background: colour,
    animation: animation
  }),
  lightSelection: {
    extend: 'fullSize'
  },
  lightSelectionSelected: ({ selectedStyle }) => selectedStyle,
  maskContainer: {
    extend: 'fullSize',
    zIndex: -10,
    overflow: 'hidden'
  },
  topMask: ({ topMask: { opacity, animation } }) => ({
    width: '100%',
    height: '50%',
    background: offColour,
    opacity: opacity,
    animation: animation,
  }),
  botMask: ({ botMask: { opacity, animation } }) => ({
    width: '100%',
    height: '50%',
    top: '50%',
    background: offColour,
    opacity: opacity,
    animation: animation,
  }),
  lightImage: {
    display: 'block',
    width: '100%',
  }
});

export const LightButton = ({ light, image, isSelected, selectedStyle,
                              lightIndex, className, ...rest }) => {
  const { colourMode, colourHue, colourSaturation, animation } = light;

  const styleConfig = {
    lightBackground: {
      colour: offColour,
      animation: 'unset'
    },
    topMask: {
      opacity: 0,
      animation: 'unset',
    },
    botMask: {
      opacity: 0,
      animation: 'unset',
    },
    selectedStyle
  };

  // colourMode
  if (light.colourMode === 'white') {
    styleConfig.lightBackground.colour = '#FDF4DC';
  }
  else if (light.colourMode === 'colour') {
    styleConfig.lightBackground.colour = tinycolor.fromRatio({
      h: light?.colourHue || 0,
      s: light?.colourSaturation || 0,
      v: 1,
      a: 1,
    }).toHexString();
  }
  else if (light.colourMode === 'rainbow') {
    styleConfig.lightBackground.colour = 'linear-gradient(to right, #FF3333,#FFFF33,#33FF33,#33FFFF,#3333FF)';
  }
  else if (light.colourMode === 'gradual') {
    styleConfig.lightBackground.colour = '#FF3333';
    styleConfig.lightBackground.animation = '$gradualAnimation 4.25s infinite';
  }

  // animation
  if (light.animation === 'twinkle') {
    styleConfig.topMask.animation = '$twinkleAnimation 2s infinite';
    styleConfig.botMask.animation = '$twinkleAnimation 2s infinite reverse';
  }
  else if (light.animation === 'rain') {
    styleConfig.topMask.opacity = maskOpacity;
    styleConfig.topMask.animation = '$rainAnimation 2s 0.25s infinite';
    styleConfig.botMask.opacity = maskOpacity;
    styleConfig.botMask.animation = '$rainAnimation 2s 1.25s infinite';
  }
  else if (light.animation === 'wave') {
    styleConfig.topMask.opacity = maskOpacity;
    styleConfig.botMask.opacity = maskOpacity;
    if (Number.isInteger(lightIndex)) {
      // We assume 10 lights
      const delay = (lightIndex / 2).toString();
      styleConfig.topMask.animation = '$waveAnimationTen linear 5s ' + delay + 's infinite';
      styleConfig.botMask.animation = '$waveAnimationTen linear 5s ' + delay + 's infinite';
    }
    else {
      styleConfig.topMask.animation = '$waveAnimationSingle linear 1s infinite';
      styleConfig.botMask.animation = '$waveAnimationSingle linear 1s infinite';
    }
  }

  const classes = useStyles(styleConfig);

  return (
    <button className={classNames(className, classes.button)} {...rest} >
      <div className={classes.lightBackground}></div>
      <div
        className={classNames({
          [classes.lightSelection]: true,
          [classes.lightSelectionSelected]: isSelected
        })}
      ></div>
      <div className={classes.maskContainer}>
        <div className={classes.topMask}></div>
        <div className={classes.botMask}></div>
      </div>
      {image &&
       <img className={classes.lightImage} src={image} />}
    </button>
  );
}
