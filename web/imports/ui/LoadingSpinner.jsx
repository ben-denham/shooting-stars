import React from 'react';
import {createUseStyles} from 'react-jss';
import classNames from 'classnames';

/* From: https://loading.io/css/ */

const useStyles = createUseStyles({
  '@keyframes lds-ring': {
    from: {
      transform: 'rotate(0deg)'
    },
    to: {
      transform: 'rotate(360deg)'
    }
  },
  ldsRing: {
    display: 'inline-block',
    position: 'relative',
    width: '80px',
    height: '80px',
  },
  ldsRingInner: {
    boxSizing: 'border-box',
    display: 'block',
    position: 'absolute',
    width: '64px',
    height: '64px',
    margin: '8px',
    border: '8px solid #FFFFFF',
    borderRadius: '50%',
    animation: '$lds-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite',
    borderColor: '#FFFFFF transparent transparent transparent'
  },
  ldsRingInnerOne: {
    animationDelay: '-0.45s',
  },
  ldsRingInnerTwo: {
    animationDelay: '-0.3s',
  },
  ldsRingInnerThree: {
    animationDelay: '-0.15s',
  },
});

export const LoadingSpinner = ({ className }) => {
  const classes = useStyles();

  return (
    <div className={classNames(classes.ldsRing, className)}>
      <div className={classNames(classes.ldsRingInner, classes.ldsRingInnerOne)}></div>
      <div className={classNames(classes.ldsRingInner, classes.ldsRingInnerTwo)}></div>
      <div className={classNames(classes.ldsRingInner, classes.ldsRingInnerThree)}></div>
    </div>
  )
}
