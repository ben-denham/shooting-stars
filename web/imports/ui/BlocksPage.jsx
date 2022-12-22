import React, { useEffect, useState } from 'react';
import { useTracker } from 'meteor/react-meteor-data';
import { createUseStyles } from 'react-jss';
import classNames from 'classnames';
import { useSwipeable } from 'react-swipeable';
import Snowfall from 'react-snowfall';
import Color from 'color';

import { BlocksStatesCollection } from '/imports/db/BlocksStatesCollection';
import { LoadingSpinner } from './LoadingSpinner';

const DEBUG = false;

const colours = {
  // Empty
  0: '#030303',
  // I
  1: '#FFD900',
  // J
  2: '#FF0000',
  // L
  3: '#00CF00',
  // O
  4: '#9500FF',
  // S
  5: '#FA7100',
  // T
  6: '#00FAAB',
  // Z
  7: '#0064FA',
  // GHOST
  8: '#030303',
  // GARBAGE
  9: '#030303',
};

const useStyles = createUseStyles({
  page: {
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    flex: 1,
  },
  loading: {
    margin: 'auto'
  },
  instructions: {
    fontFamily: 'Courgette',
    fontSize: '24px',
    padding: '0 20px',
  },
  gameWrapper: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  playfield: {
    position: 'relative',
    background: '#030303',
    border: '12px ridge #a75220',
  },
  pixelsWrapper: {
    display: 'grid',
    gridTemplateColumns: 'repeat(10, 1fr)',
    gap: '0.3vh',
    padding: '0.3vh',
  },
  pixel: {
    height: '2.9vh',
    aspectRatio: 1,
    borderRadius: '0.7vh',
    borderWidth: '0.7vh',
    borderStyle: 'outset',
    boxSizing: 'border-box',
    zIndex: 1,
  },
  emptyPixel: {
    border: 'none',
    background: 'none !important',
  },
  scores: {
    display: 'flex',
    fontFamily: 'DejaVu Sans Mono, monospace',
    fontSize: '16px',
  },
  aiModeMessage: {
    fontFamily: 'Courgette',
    fontSize: '24px',
    position: 'absolute',
    top: '35%',
    width: '100%',
  },
  aiModeMessagePara: {
    margin: 0,
    padding: '1em',
  },
});

export const BlocksPage = () => {
  const classes = useStyles();

  const { state, isLoading } = useTracker(() => {
    const handler = Meteor.subscribe('blocksStates');

    if (!handler.ready()) {
      return { state: null, isLoading: true };
    }

    const state = BlocksStatesCollection.findOne({key: 'game-state'});

    return { state };
  });

  const now = (new Date()).getTime();
  const aiMode = (!DEBUG) && (state ? (
    // Assume aiMode if the state is over 10000 milliseconds old
    state.aiMode || ((now - state.timestamp) > 10000)
  ) : false);

  const sendInput = (input) => {
    Meteor.call('blocks.sendInput', input);
  };

  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => sendInput('left'),
    onSwipedRight: () => sendInput('right'),
    onSwipedUp: () => sendInput('rotate'),
    onSwipedDown: () => sendInput('drop'),
    trackMouse: true,
  });

  const handleKey = (e) => {
    switch (e.key) {
    case 'ArrowLeft':
      sendInput('left');
      break;
    case 'ArrowRight':
      sendInput('right');
      break;
    case 'ArrowUp':
      sendInput('rotate');
      break;
    case 'ArrowDown':
      sendInput('drop');
      break;
    }
  };

  // Add event listeners
  useEffect(() => {
    window.addEventListener("keydown", handleKey);
    // Remove event listeners on cleanup
    return () => {
      window.removeEventListener("keydown", handleKey);
    };
  }, []); // Empty array ensures that effect is only run on mount and unmount

  const formatScore = (score) => (score <= 9999999999) ? score : 'Too huge!!!';

  return (
    <div {...swipeHandlers} className={classes.page}>
      {isLoading && <LoadingSpinner className={classes.loading}></LoadingSpinner>}
      {!isLoading && state &&
       <>
         <div className={classes.gameWrapper}>
           <div className={classes.scores}>
             {!aiMode &&
              <div>Score: {formatScore(state.score)}</div>}
             <div style={{flex: 1, minWidth: '2vh'}}></div>
             <div>High score: {formatScore(state.highScore)}</div>
           </div>
           <div className={classes.playfield}>
             <div className={classes.pixelsWrapper}
                  style={{visibility: aiMode ? 'hidden' : 'visible'}}>
               {state.playfield.flat().map((pixel, pixelIdx) =>
                 <div key={pixelIdx}
                      className={classNames({
                        [classes.pixel]: true,
                        [classes.emptyPixel]: ((pixel == 0) || (pixel == 8)),
                      })}
                      style={{
                        background: Color(colours[pixel]).desaturate(0.2).hex(),
                        borderColor: Color(colours[pixel]).desaturate(0.2).darken(0.05).hex(),
                      }}>
                 </div>
               )}
             </div>
             {aiMode &&
              <div className={classes.aiModeMessage}>
                <p className={classes.aiModeMessagePara}>
                  Running AI trained by last user session, make any move to start a new game and teach the AI!
                </p>
              </div>
             }
             <Snowfall
             speed={[0.7, 1.0]}
               wind={[-0.2, 0.5]}
               radius={[0.5, 1.0]}
               snowflakeCount={50}
             />
           </div>
         </div>
         <p className={classes.instructions}>Swipe left/right/up/down or use arrow&nbsp;keys</p>
       </>
      }
    </div>
  );
};
