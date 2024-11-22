import { Meteor } from 'meteor/meteor';
import { LightsCollection } from '/imports/db/LightsCollection';

Meteor.publish('lights', async function publishLights() {
  return await LightsCollection.findAsync({}, {
    fields: {
      idx: 1,
      colourMode: 1,
      colourHue: 1,
      colourSaturation: 1,
      animation: 1,
    }
  });
});
