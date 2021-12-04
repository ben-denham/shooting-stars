import React, { useState } from 'react';
import { useTracker } from 'meteor/react-meteor-data';

import { LightsCollection } from '/imports/db/LightsCollection';
import { LightList } from './LightList'
import { LightForm } from './LightForm'

export const App = () => {
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
    <div>
      {isLoading && <div className="loading">loading...</div>}
      <LightList lights={lights} setSelectedLightId={setSelectedLightId}></LightList>
      <LightForm light={selectedLight}></LightForm>
    </div>
  );
};
