import React, { useState } from 'react';
import { useTracker } from 'meteor/react-meteor-data';
import {createUseStyles} from 'react-jss';

import { LightsCollection } from '/imports/db/LightsCollection';
import { LightList } from './LightList';
import { LightForm } from './LightForm';
import { mediumBreakpoint } from './breakpoints';
import { LoadingSpinner } from './LoadingSpinner';

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
    justifyContent: 'center',
  },
  loading: {
    margin: 'auto'
  },
  lightList: {
    flex: 1,
  },
  lightForm: {
  }
});

export const App = () => {
  const classes = useStyles();

  const { lights, isLoading } = useTracker(() => {
    const handler = Meteor.subscribe('lights');

    if (!handler.ready()) {
      return { lights: [], isLoading: true };
    }

    const lights = LightsCollection.find({}, {
      sort: { idx: 1 }
    }).fetch();

    return { lights };
  });
  const [selectedLightId, setSelectedLightId] = useState(null);

  const selectedLight = lights.find(light => light._id === selectedLightId);

  return (
    <div className={classes.app}>
      {isLoading && <LoadingSpinner className={classes.loading}></LoadingSpinner>}
      {!isLoading &&
       <>
         <LightList
           className={classes.lightList}
           lights={lights}
           setSelectedLightId={setSelectedLightId}
         />
         <LightForm
           className={classes.lightForm}
           light={selectedLight}
         />
       </>}
    </div>
  );
};
