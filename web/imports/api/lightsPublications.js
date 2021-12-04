import { Meteor } from 'meteor/meteor';
import { LightsCollection } from '/imports/db/LightsCollection';

Meteor.publish('lights', function publishLights() {
  return LightsCollection.find({}, {
    fields: {
      idx: 1,
      colourMode: 1,
      colourHue: 1,
      colourSaturation: 1,
      animation: 1,
    }
  });
});
