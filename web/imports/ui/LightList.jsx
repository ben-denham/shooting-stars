import React from 'react';
import {createUseStyles} from 'react-jss';
import classNames from 'classnames';
import Snowfall from 'react-snowfall';

import candycaneStripeImage from '/imports/ui/assets/images/candycane-stripe.png';
import lightsSegmentImage from '/imports/ui/assets/images/lights-segment.png';
import { animationCss, getLightCss } from '/imports/ui/colors.js';

const styles = {
  ...animationCss,
  lightList: {
    position: 'relative',
    background: 'black',
    border: '12px ridge #a75220',
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'stretch',
    alignContent: 'space-around'
  },
  lightButton: (props) => ({
    border: 0,
    padding: 0,
    margin: 0,
    '&:focus': {
      outline: 0,
      zIndex: 1,
      '& > $lightBorder': {
        boxShadow: '0px 0px 5px 5px white',
        borderRadius: '8%',
      }
    },
    width: '20%',
    position: 'relative',
    background: 'transparent',
    zIndex: 0,
    ...(props ? props.lightCss : {})
  }),
  lightBorder: {
    position: 'absolute',
    boxSizing: 'border-box',
    width: '100%',
    height: '100%',
  },
  lightBorderSelected: {
    border: '10px solid transparent',
    borderImage: `url(${candycaneStripeImage})`,
    borderImageRepeat: 'round',
    borderImageSlice: 50
  },
  lightBackground: {
    position: 'absolute',
    boxSizing: 'border-box',
    width: '100%',
    height: '100%',
    zIndex: -1
  },
  lightImage: {
    display: 'block',
    width: '100%',
  }
};

const useStyles = createUseStyles(styles);

const Light = ({ light, isSelected, onClick }) => {
  const lightCss = getLightCss(light);
  const classes = useStyles({ lightCss });

  return (
    <button
      className={classNames({
        [classes.lightButton]: true
      })}
      onClick={onClick}
    >
      <div
        className={classNames({
          [classes.lightBorder]: true,
          [classes.lightBorderSelected]: isSelected
        })}
      ></div>
      <div className={classes.lightBackground}></div>
      <img className={classes.lightImage} src={lightsSegmentImage} />
    </button>
  );
}

export const LightList = ({ lights, selectedLight, setSelectedLightId, className }) => {
  const classes = useStyles();

  return (
    <div className={classNames(className, classes.lightList)}>
      <Snowfall
        speed={[0.7, 1.0]}
        wind={[-0.2, 0.5]}
        radius={[0.5, 1.0]}
        snowflakeCount={50}
      />
      { lights.map(light =>
        <Light key={ light._id }
               light={light}
               isSelected={selectedLight === light}
               onClick={() => setSelectedLightId(light._id)}>
        </Light>
      )}
    </div>
  )
}
