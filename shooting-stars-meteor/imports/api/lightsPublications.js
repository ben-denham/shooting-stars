import { Meteor } from 'meteor/meteor';
import { LightsCollection } from '/imports/db/LightsCollection';

Meteor.publish('lights', function publishLights() {
  return LightsCollection.find({});
});
