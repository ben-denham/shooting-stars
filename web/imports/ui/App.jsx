import React, { useState } from 'react';
import { useTracker } from 'meteor/react-meteor-data';
import {createUseStyles} from 'react-jss';
import classNames from 'classnames';

import { LightsPage } from './LightsPage';
import { BlocksPage } from './BlocksPage';
import { PaintPage } from './PaintPage';
import { StoryPage } from './StoryPage';

const useStyles = createUseStyles({
  app: {
    margin: '0px auto',
    height: '100%',
    width: '100%',
    maxWidth: '768px',
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'stretch',
    background: '#121212',
    position: 'relative',
  },
  pageMenu: {
    display: 'flex',
    gap: '0.2em',
    zIndex: 1,
    background: '#080808',
  },
  pageButton: {
    flex: 1,
    fontFamily: 'Courgette',
    background: '#444444',
    border: 'none',
    color: 'white',
    fontSize: '1.4em',
    marginTop: '0.2em',
    padding: '0.25em 0',
    borderRadius: '0.4em 0.4em 0 0',
    cursor: 'pointer',
  },
  selectedPageButton: {
    background: '#777777',
  },
  links: {
    margin: '10px 0 10px 0',
    '& a': {
      fontSize: '0.8em',
      color: 'white',
      '&:visited': {
        color: 'white'
      }
    }
  }
});

export const App = () => {
  const classes = useStyles();
  const [selectedPageId, setSelectedPageId] = useState('blocks');

  const pages = {
    blocks: 'Blocks',
    lights: 'Icicles',
    paint: 'Paint',
    story: 'Story',
  };

  return (
    <div className={classes.app}>
      <div className={classes.pageMenu}>
        {Object.keys(pages).map((pageId, _) =>
          <button key={pageId}
                  className={classNames({
                    [classes.pageButton]: true,
                    [classes.selectedPageButton]: (selectedPageId == pageId),
                  })}
                  onClick={() => setSelectedPageId(pageId)}>{pages[pageId]}</button>
        )}
      </div>
      {(selectedPageId == 'lights') && <LightsPage />}
      {(selectedPageId == 'blocks') && <BlocksPage />}
      {(selectedPageId == 'paint') && <PaintPage />}
      {(selectedPageId == 'story') && <StoryPage />}
      <div className={classes.links}>
        <a href="https://github.com/ben-denham/shooting-stars">Source Code on GitHub</a>
      </div>
    </div>
  );
};
