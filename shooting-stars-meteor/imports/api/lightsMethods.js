import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { LightsCollection, COLOUR_MODES } from '/imports/db/LightsCollection';

Meteor.methods({
  'lights.setColourMode'(lightId, colourMode) {
    check(lightId, String);
    check(colourMode, String);

    if (!COLOUR_MODES.includes(colourMode)) {
      throw new Meteor.Error('invalid-colour-mode', 'Invalid colour mode');
    }

    LightsCollection.update(lightId, {
      $set: { colourMode }
    });
  }
});
